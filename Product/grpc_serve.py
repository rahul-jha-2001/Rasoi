import os
import sys
import uuid
from concurrent import futures
import grpc

import django,os
from django.core.exceptions import ValidationError,ObjectDoesNotExist,MultipleObjectsReturned,PermissionDenied
from django.db import IntegrityError,DatabaseError
from django.db import transaction
from django.conf import settings

from grpc_interceptor.exceptions import GrpcException,Unauthenticated,FailedPrecondition

import PIL

from dotenv import load_dotenv
load_dotenv()   

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Product.settings')
django.setup()

from proto import Product_pb2,Product_pb2_grpc
from proto.Product_pb2 import (
    product,
    category,
    add_on,
    product,
    error,
    Productstatus
)
from decimal import Decimal
from product_app.models import Category,Product as Product_model,Add_on
from datetime import datetime
from utils.logger import Logger

import boto3
from botocore.exceptions import ClientError
from utils.image_handler import image_handler

logger = Logger("GRPC_service")

BUCKET_NAME = os.getenv("BUCKET_NAME")
REGION_NAME = os.getenv("AWS_DEFAULT_REGION")
AWS_ACCESS_KEY_ID= os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY= os.getenv("AWS_SECRET_ACCESS_KEY")


def handle_error(func):
    def wrapper(self, request, context):
        try:
            return func(self, request, context)
        except Product_model.DoesNotExist:
            logger.warning(f"Product Not Found: {getattr(request, 'product_uuid', '')}")
            context.abort(grpc.StatusCode.NOT_FOUND, "Product Not Found")

        except Category.DoesNotExist:
            logger.error(f"Category Not Found: {getattr(request, 'category_uuid', '')}")
            context.abort(grpc.StatusCode.NOT_FOUND, "Category Not Found")
            
        except Add_on.DoesNotExist:
            logger.error(f"Add-on Not Found: {getattr(request, 'add_on_uuid', '')}")
            context.abort(grpc.StatusCode.NOT_FOUND, "Add-on Not Found")

        except ObjectDoesNotExist:
            logger.error("Requested object does not exist")
            context.abort(grpc.StatusCode.NOT_FOUND, "Requested Object Not Found")

        except MultipleObjectsReturned:
            logger.error(f"Multiple objects found for request")
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Multiple matching objects found")

        except ValidationError as e:
            logger.error(f"Validation Error: {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Validation Error: {str(e)}")

        except IntegrityError as e:
            logger.error(f"Integrity Error: {str(e)}")
            context.abort(grpc.StatusCode.ALREADY_EXISTS, "Integrity constraint violated")

        except DatabaseError as e:
            logger.error(f"Database Error: {str(e)}",e)
            context.abort(grpc.StatusCode.INTERNAL, "Database Error")

        except PermissionDenied as e:
            logger.warning(f"Permission Denied: {str(e)}",e)
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Permission Denied")

        except ValueError as e:
            logger.error(f"Invalid Value: {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Invalid Value: {str(e)}")

        except TypeError as e:
            logger.error(f"Type Error: {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Type Error: {str(e)}")

        except TimeoutError as e:
            logger.error(f"Timeout Error: {str(e)}")
            context.abort(grpc.StatusCode.DEADLINE_EXCEEDED, "Request timed out")
            
        except PIL.UnidentifiedImageError as e:
            logger.error(f"Image Error: {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Image Error: {str(e)}")
            
        except grpc.RpcError as e:
            logger.error(f"RPC Error: {str(e)}")
            # Don't re-abort as this is likely a propagated error
            raise
            
        except AttributeError as e:
            logger.error(f"Attribute Error: {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Attribute Error: {str(e)}")
            
        except transaction.TransactionManagementError as e:
            logger.error(f"Transaction Error: {str(e)}")
            context.abort(grpc.StatusCode.ABORTED, f"Transaction Error: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected Error: {str(e)}",e)
            context.abort(grpc.StatusCode.INTERNAL, "Internal Server Error")
    return wrapper


def check_access(roles:list[str]):
    def decorator(func):
        def wrapper(self, request, context):
            metadata = dict(context.invocation_metadata() or [])
            role = metadata.get("role")

            if not role:
                logger.warning("Missing role in metadata")
                raise Unauthenticated("Role missing from metadata")

            if role == "internal":
                # TODO: Add internal service verification here
                return func(self, request, context)

            if role not in roles:
                logger.warning(f"Unauthorized role: {role}")
                raise Unauthenticated(f"Unauthorized role: {role}")

            # Role-specific access checks
            try:
                if role == "store":
                    store_uuid_in_token = metadata["store_uuid"]
                    if not getattr(request, "store_uuid", None):
                        logger.warning("Store UUID missing in request")
                        raise Unauthenticated("Store UUID is missing in the request")
                    if store_uuid_in_token != getattr(request, "store_uuid", None):
                        logger.warning("Store UUID mismatch")
                        raise Unauthenticated("Store UUID does not match token")

                elif role == "user":
                    phone_in_token = metadata["user_phone_no"]
                    if not getattr(request, "user_phone_no", None):
                        logger.warning("User phone number missing in request")
                        raise Unauthenticated("User phone number is missing in the request")
                    if phone_in_token != getattr(request, "user_phone_no", None):
                        logger.warning("User phone mismatch")
                        raise Unauthenticated("User phone does not match token")

            except KeyError as e:
                logger.warning(f"Missing required metadata for role '{role}': {e}")
                raise Unauthenticated(f"Missing metadata: {e}")

            return func(self, request, context)
        return wrapper
    return decorator

class ProductService(Product_pb2_grpc.ProductServiceServicer):

    def __init__(self):
        super().__init__()


    def _verify_wire_format(self,GRPC_message,GRPC_message_type,context_info = ""):
        """
        Helper to verify protobuf wire format
        Args:
            GRPC_message: The protobuf message to verify
            GRPC_message_type:The Protobuf message class type
            context_info: Additional context for logging 
        Returns:
            bool:True if Verifications Succeeds

        """
        try:
            serialized = GRPC_message.SerializeToString()
            logger.debug(f"Serialized Message Size: {len(serialized)} bytes")
            logger.debug(f"Message before serializtion: {GRPC_message}")

            test_msg = GRPC_message_type()
            test_msg.ParseFromString(serialized)

            original_fields = GRPC_message.ListFields()
            test_fields = test_msg.ListFields()

            if len(original_fields) != len(test_fields):
                logger.error(f"Field count mismatch - Original: {len(original_fields)}, Deserialized: {len(test_fields)}")
                logger.error(f"Original fields: {[f[0].name for f in original_fields]}")
                logger.error(f"Deserialized fields: {[f[0].name for f in test_fields]}")
            
            return True
        except Exception as e:
            logger.error(f"Wire Format verifications failed for {GRPC_message_type.__name__}{context_info}: {str(e)}")
            logger.error(f"Message Contents: {GRPC_message}")
            try:
                logger.error(f"Serialized hex: {serialized.hex()}")
            except:
                pass
            return False
    
    def _category_to_proto(self,category:Category|None) -> Product_pb2.category:
        try:
        # Create an empty response object
            response = Product_pb2.category()
            
            # Add UUID fields with specific error handling
            try:
                response.category_uuid = str(category.category_uuid)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert category_uuid: {e}")
                response.category_uuid = ""  # Or some default value
                
            try:
                response.store_uuid = str(category.store_uuid)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert store_uuid: {e}")
                response.store_uuid = ""
                
            # Add string fields
            try:
                response.name = category.name or ""
            except AttributeError as e:
                logger.warning(f"Failed to get name: {e}")
                response.name = ""
                
            try:
                response.description = category.description or ""
            except AttributeError as e:
                logger.warning(f"Failed to get description: {e}")
                response.description = ""
                
            # Add numeric field
            try:
                response.display_order = int(category.display_order)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert display_order: {e}")
                response.display_order = 0
                
            # Add boolean fields
            try:
                response.is_available = bool(category.is_available)
            except AttributeError as e:
                logger.warning(f"Failed to get is_available: {e}")
                response.is_available = False
                
            try:
                response.is_active = bool(category.is_active)
            except AttributeError as e:
                logger.warning(f"Failed to get is_active: {e}")
                response.is_active = False
                
            # Add timestamp fields
            try:
                response.created_at = category.created_at
            except (AttributeError, ValueError) as e:
                logger.warning(f"Failed to convert created_at: {e}")
                # Leave timestamp at default (epoch)
                
            try:
                response.updated_at = category.updated_at
            except (AttributeError, ValueError) as e:
                logger.warning(f"Failed to convert updated_at: {e}")
                # Leave timestamp at default (epoch)
            
            if not self._verify_wire_format(response, Product_pb2.category, f"category_id={category.category_uuid}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize category {category.category_uuid}")
            return response
        except Exception as e:
            logger.error("Error Creating ",e)

    def _add_on_to_proto(self,add_on:Add_on|None) -> Product_pb2.add_on:
        try:
            response  = Product_pb2.add_on()
            try:
                response.add_on_uuid = str(add_on.add_on_uuid)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert add_on_uuid: {e}")
                response.add_on_uuid = ""  # Or some default value
            
            try:
                response.name = str(add_on.name)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert name: {e}")
                response.name = ""  # Or some default value

            try:
                response.is_available = add_on.is_available
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert is_available: {e}")
                response.is_available = False # Or some default value    

            try:
                response.max_selectable = int(add_on.max_selectable)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert max_selectable: {e}")
                response.max_selectable = 1  # Or some default value    

            try:
                response.GST_percentage = add_on.GST_percentage
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert GST_percentage: {e}")
                response.GST_percentage = 18.00  # Or some default value            

            try:
                response.price = Decimal(add_on.price)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert price: {e}")
                response.price = ""  # Or some default value    
            
            try:
                response.created_at = add_on.created_at
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert created_at: {e}")
                response.created_at = ""  # Or some default value    

            try:
                response.updated_at = add_on.updated_at
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert updated_at: {e}")
                response.updated_at = ""  # Or some default value 
            return response               
        except Exception as e:
            logger.error("Error Creating ",e)
            raise


    def _product_to_proto(self,Product_obj:Product_model|None) -> Product_pb2.product:
        
        try:
            #create empty product object
            response = Product_pb2.product()
            try:
                response.product_uuid = str(Product_obj.product_uuid)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert product_uuid: {e}")
                response.product_uuid = ""  # Or some default value
            
            try:
                response.store_uuid = str(Product_obj.store_uuid)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert store_uuid: {e}")
                response.store_uuid = ""  # Or some default value

            try:
                response.name = str(Product_obj.name)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert name: {e}")
                response.name = ""  # Or some default value    

            try:
                response.description = str(Product_obj.description)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert description: {e}")
                response.description = ""  # Or some default value    

            try:
                response.status = Product_obj.status
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert status: {e}")
                response.status = Productstatus.DRAFT  # Or some default value            

            try:
                response.is_available = Product_obj.is_available
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert is_available: {e}")
                response.is_available = ""  # Or some default value    
            try:
                response.display_price = Product_obj.display_price
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert display_price: {e}")
                response.display_price = ""  # Or some default value    

            try:
                response.price = Product_obj.price
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert price: {e}")
                response.price = ""  # Or some default value       
            try:
                response.GST_percentage = Product_obj.GST_percentage
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert GST_percentage: {e}")
                response.GST_percentage = ""  # Or some default value        

            try:
                
                response.category_uuid = str(Product_obj.category.category_uuid)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert category: {e}")
                response.category_uuid = ""  # Or some default value        

            try:
                response.dietary_pref = Product_obj.dietary_pref
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert dietary_pref: {e}")
                response.dietary_pref = ""  # Or some default value        

            try:
                response.image_URL = Product_obj.image_url
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert image_url: {e}")
                response.image_URL = ""  # Or some default value        
            
            if not self._verify_wire_format(response, Product_pb2.product, f"product_id={Product_obj.product_uuid}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize Product {Product_obj.product_uuid}")
            return response
    
        except Exception as e:
            logger.error("Error Creating ",e)
            raise





        # if Product_obj is None:
        #     response = Product_pb2.product()
        # else:        
        #     response = Product_pb2.product(
        #         product_uuid=str(Product_obj.product_uuid),
        #         store_uuid=str(Product_obj.store_uuid),
        #         name=str(Product_obj.name),
        #         status=Productstatus(Product_obj.status),
        #         is_available=Product_obj.is_available,
        #         display_price=Product_obj.display_price,
        #         price=Product_obj.price,
        #         GST_percentage=Product_obj.GST_percentage,
        #         category=self._category_to_proto(Product_obj.category),
        #         dietary_pref=str(Product_obj.dietary_pref),
        #         image_URL= Product_obj.image_url,
        #         add_ons=[self._add_on_to_proto(x) for x in Product_obj.add_on.all()]
        #     )
        # if not self._verify_wire_format(response, Product_pb2.product, f"Product_id={Product_obj.product_uuid}"):
        #     raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize category {Product_obj.product_uuid}")
        # return response
    
    @handle_error
    @check_access(roles=["user","store","internal"])
    def CreateProduct(self, request, context):

        size = image_handler.check_size(request.Image)
        if size > 5:
            raise ValidationError(f"Image size:{size}mb exceeds 5mb")
        ext = image_handler.check_extension(request.Image)
        if ext not in ['.jpg','.png','.jpeg']:
            logger.debug(ext)
            raise ValidationError(f"Unspported File Type {ext}")
        category = Category.objects.get(category_uuid = request.category_uuid,store_uuid =request.store_uuid)
        with transaction.atomic():
            product = Product_model.objects.create(
                store_uuid = request.store_uuid,
                name = request.product.name,
                description = request.product.description,
                status = request.product.status,
                is_available = request.product.is_available,
                display_price = request.product.display_price,
                price = request.product.price,
                GST_percentage =request.product.GST_percentage,
                category = category,
                dietary_pref = request.product.dietary_pref,
                )
            
            logger.info(f"Created Product: {product.product_uuid} in category {product.category.category_uuid} at store {product.store_uuid}")
            
            image_name = f"{product.store_uuid}/{product.category.category_uuid}/{product.product_uuid}"

            _,url = image_handler.upload_to_s3(
                request.Image,
                bucket_name=BUCKET_NAME,
                object_name=image_name,
                aws_access_key=AWS_ACCESS_KEY_ID,
                aws_secret_key=AWS_SECRET_ACCESS_KEY,
                region_name=REGION_NAME
            )
            if _:
                product.image_url = url
                product.save()
        

            return Product_pb2.ProductResponse(
                product=self._product_to_proto(product),
                success= True)
       
    @handle_error
    @check_access(roles=["user","store","internal"])
    def GetProduct(self, request, context):

        category = Category.objects.get(category_uuid = request.category_uuid,store_uuid =request.store_uuid)


        product = Product_model.objects.get(store_uuid = request.store_uuid,product_uuid = request.product_uuid,category=category)
        return Product_pb2.ProductResponse(
            product= self._product_to_proto(product),
            success= True
        )
        
    
    @handle_error
    @check_access(roles=["user","store","internal"])
    def ListProducts(self, request, context):
        if request.page < 0:
            request.page = 1
        if request.limit < 0:
            request.limit = 10

        
        products,next_page,prev_page = Product_model.objects.get_products(store_uuid=request.store_uuid,
                                                        category_uuid=request.category_uuid,
                                                        limit=request.limit,
                                                        page = request.page)
        response = Product_pb2.ListProductsResponse(
            products=[self._product_to_proto(x) for x in products],
            success= True,
            next_page=next_page,
            prev_page=prev_page

        )
        return response
    
    @handle_error
    @check_access(roles=["user","store","internal"])
    def UpdateProduct(self, request, context):

        category = Category.objects.get(category_uuid = request.category_uuid,store_uuid =request.store_uuid)


        product = Product_model.objects.get(store_uuid = request.store_uuid,product_uuid = request.product_uuid,category=category)

        with transaction.atomic():
    
            if request.product.HasField('name'):
                    product.description = request.product.name

            if request.product.HasField('description'):
                product.description = request.product.description

            if request.product.HasField('status'):
                product.status = request.product.status
            
            if request.product.HasField('is_available'):
                product.is_available = request.product.is_available

            if request.product.HasField('display_price'):
                product.display_price = request.product.display_price

            if request.product.HasField('price'):
                product.price = request.product.price

            if request.product.HasField('GST_percentage'):
                product.GST_percentage = request.product.GST_percentage

            if request.product.HasField('category_uuid'):
                category = Category.objects.get(category_uuid = request.product.category_uuid)
                product.category = category        

            if request.product.HasField('dietary_pref'):
                product.dietary_pref = request.product.dietary_pref


            product.clean()
            product.save()

            logger.info(f"Product Updated For product id: {product.product_uuid}")
            return Product_pb2.ProductResponse(
                product=self._product_to_proto(product),
                success= True,
            )   


    @handle_error
    @check_access(roles=["user","store","internal"])
    def DeleteProduct(self, request, context):
        category = Category.objects.get(category_uuid = request.category_uuid,store_uuid =request.store_uuid)

        with transaction.atomic():
            product = Product_model.objects.get(store_uuid = request.store_uuid,product_uuid = request.product_uuid,category=category)
            product.delete()
        
            logger.info(f"Deleted product: {request.product_uuid}")
            return Product_pb2.DeleteProductResponse(success=True)

    @handle_error
    @check_access(roles=["user","store","internal"])
    def CreateCategory(self, request, context):
        with transaction.atomic():
            cat = Category.objects.create(
                store_uuid = request.store_uuid,
                name = request.category.name,
                description = request.category.description,
                display_order = request.category.display_order,
                is_available = request.category.is_available,
                is_active = request.category.is_active
            )
            logger.info(f"Category Id:{cat.category_uuid} Created at store Id:{cat.store_uuid}")

            return Product_pb2.CategoryResponse(
                category= self._category_to_proto(cat),
                success= True,
            )
    
    @handle_error
    @check_access(roles=["user","store","internal"])
    def GetCategory(self, request, context):
        
        category_uuid = request.category_uuid
        store_uuid = request.store_uuid

        category = Category.objects.get(category_uuid=category_uuid,store_uuid=store_uuid)

        return Product_pb2.CategoryResponse(
            category=self._category_to_proto(category),
            success= True,
        )

    @handle_error
    @check_access(roles=["store","internal"])
    def UpdateCategory(self, request, context):
    
        category_obj = Category.objects.get(category_uuid=request.category_uuid,store_uuid=request.store_uuid)
        with transaction.atomic():
            if request.category.HasField('name'):
                category_obj.name = request.category.name 

            if request.category.HasField('description'):
                category_obj.description = request.category.description
            
            if request.category.HasField('is_available'):
                category_obj.is_available = request.category.is_available

            if request.category.HasField('display_order'):
                category_obj.display_order = request.category.display_order

            if request.category.HasField('is_active'):
                category_obj.is_active = request.category.is_active

            category_obj.full_clean()
            category_obj.save()
            logger.debug(category_obj)
            logger.info(f"Category Updated For category id: {category_obj.category_uuid}")
            return Product_pb2.CategoryResponse(
                category=self._category_to_proto(category_obj),
                success= True,
            )

    @handle_error
    @check_access(roles=["store","internal"])
    def DeleteCategory(self, request, context):  
        with transaction.atomic():
            Category.objects.get(category_uuid = request.category_uuid,store_uuid=request.store_uuid).delete()
        
            logger.info(f"Deleted Category: {request.category_uuid}")
            return Product_pb2.DeleteCategoryResponse(success=True)
    
    @handle_error
    @check_access(roles=["user","store","internal"])
    def ListCategory(self, request, context):
        if request.page < 0:
            request.page = 1
        if request.limit < 0:
            request.limit = 10
        categories,next_page,prev_page = Category.objects.get_categories(
                                                        store_uuid=request.store_uuid,
                                                        limit=request.limit,
                                                        page = request.page)
        
        response = Product_pb2.ListCategoryResponse(
            categories=[self._category_to_proto(x) for x in categories],
            success= True,
            next_page=next_page,
            prev_page=prev_page

        )
        return response 
    

    @handle_error
    @check_access(roles=["store","internal"])
    def CreateAddOn(self, request, context):
        product:Product_model = Product_model.objects.get(store_uuid = request.store_uuid,product_uuid = request.product_uuid)
        with transaction.atomic(): 
            add_on:Add_on = Add_on.objects.create(
                product = product,
                name = request.add_on.name,
                is_available = request.add_on.is_available,
                max_selectable = request.add_on.max_selectable,
                GST_percentage = request.add_on.GST_percentage,
                price = request.add_on.price
            )
            logger.info(f"Created Add-On:{add_on.add_on_uuid} for product id:{product.product_uuid} at Store id:{product.store_uuid}")
            return Product_pb2.AddOnResponse(
                add_on=self._add_on_to_proto(add_on),
                success= True
            )

    @handle_error
    @check_access(roles=["user","store","internal"])
    def GetAddOn(self,request,context):

        product = Product_model.objects.get(store_uuid = request.store_uuid,product_uuid = request.product_uuid)
        add_on_obj = Add_on.objects.get(
            product = product,
            add_on_uuid = request.add_on_uuid
        )
        return Product_pb2.AddOnResponse(
            add_on= self._add_on_to_proto(add_on_obj),
            success=True
        )
    
    @handle_error
    @check_access(roles=["store","internal"])
    def UpdateAddOn(self, request, context):
        product = Product_model.objects.get(store_uuid = request.store_uuid,product_uuid = request.product_uuid)

        add_on = Add_on.objects.get(add_on_uuid=request.add_on_uuid,product=product)
        with transaction.atomic():
            if request.add_on.HasField('name'):
                add_on.name = request.add_on.name 

            if request.add_on.HasField('is_available'):
                add_on.is_available = request.add_on.is_available
            
            if request.add_on.HasField('max_selectable'):
                add_on.max_selectable = request.add_on.max_selectable

            if request.add_on.HasField('GST_percentage'):
                add_on.GST_percentage = request.add_on.GST_percentage

            if request.add_on.HasField('price'):
                add_on.price = request.add_on.price

            add_on.full_clean()
            add_on.save()
            logger.debug(add_on)
            logger.info(f"add_on Updated For add_on id: {add_on.add_on_uuid}")
            return Product_pb2.AddOnResponse(
                add_on=self._add_on_to_proto(add_on),
                success= True,
            )
       
    @handle_error
    @check_access(roles=["user","store","internal"])
    def ListAddOn(self, request, context):

        product = Product_model.objects.get(store_uuid = request.store_uuid,product_uuid = request.product_uuid)
  
        if request.page < 0:
            request.page = 1
        if request.limit < 0:
            request.limit = 10
        add_ons,next_page,prev_page = Add_on.objects.get_add_ons(
                                                        product = product,
                                                        limit=request.limit,
                                                        page = request.page
                                                        )
        logger.info(f"Successfully listed {len(add_ons)} Add-ons For product Id {request.product_uuid}")
        response = Product_pb2.ListAddOnResponse(
            add_ons=[self._add_on_to_proto(x) for x in add_ons],
            success= True,
            next_page=next_page,
            prev_page=prev_page
        )
        return response

    @handle_error
    @check_access(roles=["user","store","internal"])
    def DeleteAddOn(self, request, context):
        product = Product_model.objects.get(store_uuid = request.store_uuid,product_uuid = request.product_uuid)
        with transaction.atomic():

            add_on = Add_on.objects.get(add_on_uuid = request.add_on_uuid,product=product)
            add_on.delete()
        
            logger.info(f"Deleted Add_on:{request.add_on_uuid} of Product:{product.product_uuid}")
            return Product_pb2.DeleteAddOnResponse(success=True)

# class HealthCheck(healthcheck_pb2_grpc.HealthServicer):
#     def __init__(self):
#         # Initialize any necessary state here
#         self._status = healthcheck_pb2.HealthCheckResponse.SERVING

#     def Check(self, request, context):
#         # Implement the health check logic here
#         # For example, you can return SERVING if the service is healthy
#         return healthcheck_pb2.HealthCheckResponse(status=self._status)

#     def Watch(self, request, context):
#         # Implement the health watch logic here
#         # This method is used for streaming health status updates
#         # For simplicity, we'll just return the current status in a loop
#         try:
#             while True:
#                 yield healthcheck_pb2.HealthCheckResponse(status=self._status)
#                 # Sleep for a while before sending the next status update
#                 import time
#                 time.sleep(5)
#         except grpc.RpcError:
#             # Handle any RPC errors that occur during streaming
#             context.cancel()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add your services to the server
    Product_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)
    # healthcheck_pb2_grpc.add_HealthServicer_to_server(HealthCheck(),server)
    
    # Get the port from environment variables
    grpc_port = os.getenv('GRPC_SERVER_PORT', '50052')
    
    # Bind the server to the specified port
    server.add_insecure_port(f'[::]:{grpc_port}')
    server.start()
    
    logger.info(f"gRPC server is running on port {grpc_port}")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

