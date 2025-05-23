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

from google.protobuf import empty_pb2
from Proto import product_pb2,product_pb2_grpc
from Proto.product_pb2 import (
    product,
    category,
    add_on,
    Productstatus,
    dietary_preference
    
)
from decimal import Decimal
from product_app.models import Category,Product,DietaryPreference,Add_on,ProductStatus
from datetime import datetime
from utils.logger import Logger
from utils.check_access import check_access

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
        except Product.DoesNotExist:
            logger.warning(f"Product Not Found: {getattr(request, 'product_uuid', '')}")
            context.abort(grpc.StatusCode.NOT_FOUND, "Product Not Found")

        except Category.DoesNotExist:
            logger.error(f"Category Not Found: {getattr(request, 'category_uuid', '')}")
            context.abort(grpc.StatusCode.NOT_FOUND, "Category Not Found")
        
        except DietaryPreference.DoesNotExist:
            logger.error(f"DietaryPreference Not Found: {getattr(request, 'diet_pref_uuid', '')}")
            context.abort(grpc.StatusCode.NOT_FOUND, "DietaryPreference Not Found")
            
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
            context.abort(grpc.StatusCode.ALREADY_EXISTS, f"Object Already Exists")

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
            logger.error(f"Type Error: {str(e)}",e)
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

        except FailedPrecondition as e:
            context.abort(e.status_code,e.details)

        except Unauthenticated as e:
            context.abort(grpc.StatusCode.PERMISSION_DENIED,f"User Not Allowed To make this Call")
        
        except GrpcException as e:
            context.abort(e.status_code,e.details)    
        
        except AttributeError as e:
            logger.error(f"Attribute Error: {str(e)}",e)
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Attribute Error: {str(e)}")
            
        except transaction.TransactionManagementError as e:
            logger.error(f"Transaction Error: {str(e)}")
            context.abort(grpc.StatusCode.ABORTED, f"Transaction Error: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected Error: {str(e)}",e)
            context.abort(grpc.StatusCode.INTERNAL, "Internal Server Error")
    return wrapper


class ProductService(product_pb2_grpc.ProductServiceServicer):

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
    
    def _category_to_proto(self,category:Category|None) -> product_pb2.category:
        try:
        # Create an empty response object
            response = product_pb2.category()
            
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
                response.name = category.name
            except AttributeError as e:
                logger.warning(f"Failed to get name: {e}")
                response.name = ""
                
            try:
                response.description = category.description
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
            
            if not self._verify_wire_format(response, product_pb2.category, f"category_id={category.category_uuid}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize category {category.category_uuid}")
            return response
        except Exception as e:
            logger.error("Error Creating ",e)

    def _add_on_to_proto(self,add_on:Add_on|None) -> product_pb2.add_on:
        try:
            response  = product_pb2.add_on()
            try:
                response.add_on_uuid = str(add_on.add_on_uuid)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert add_on_uuid: {e}")
                response.add_on_uuid = ""  # Or some default value
            
            try:
                response.product_uuid = str(add_on.product.product_uuid)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert product_uuid: {e}")
                response.product_uuid = ""  # Or some default value
            
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

            try: 
                response.is_free = add_on.is_free
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert is_free: {e}")
                response.is_free = False
             
            return response               
        except Exception as e:
            logger.error("Error Creating ",e)
            raise

    def _diet_pref_to_proto(self,diet_pref:DietaryPreference|None) -> product_pb2.dietary_preference:

        try:
            response = product_pb2.dietary_preference()
            try:
                response.store_uuid = str(diet_pref.store_uuid)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert store_uuid: {e}")
                response.store_uuid = ""  # Or some default value
            try:
                response.diet_pref_uuid = str(diet_pref.diet_pref_uuid)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert diet_pref_uuid: {e}")
                response.diet_pref_uuid = ""  # Or some default value
            try:
                response.name = str(diet_pref.name)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert name: {e}")
                response.name = ""  # Or some default value
            try:
                response.description = str(diet_pref.description)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert description: {e}")
                response.description = ""  # Or some default value
            try:
                response.icon_url = str(diet_pref.icon_url)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert icon_url: {e}")
                response.icon_url = ""  # Or some default value

            if not self._verify_wire_format(response, product_pb2.dietary_preference, f"product_id={diet_pref.diet_pref_uuid}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize Product {diet_pref.diet_pref_uuid}")
            return response
    
        except Exception as e:
            logger.error("Error Creating ",e)
            raise

    def _product_to_proto(self,Product_obj:Product|None) -> product_pb2.product:
        
        try:
            #create empty product object
            response = product_pb2.product()
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
                response.status =  Productstatus.Value(Product_obj.status)
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert status: {e}")
                response.status = Productstatus.PRODUCT_STATE_DRAFT  # Or some default value            

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
                response.category.CopyFrom(self._category_to_proto(Product_obj.category))
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert category: {e}")
                response.dietary_pref.clear()  # If you want to set it empty

            try:
                response.dietary_pref.extend(self._diet_pref_to_proto(diet_pref) for diet_pref in  Product_obj.dietary_prefs.all())
            except (AttributeError, TypeError,Exception) as e:
                logger.warning(f"Failed to convert dietary_pref: {e}")
                response.dietary_pref = ""  # Or some default value        

            try:
                response.add_ons.extend(self._add_on_to_proto(add_on) for add_on in  Product_obj.add_on.all())
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert add_ons: {e}")
                response.add_ons = ""  # Or some default value      

            try:
                response.image_URL = Product_obj.image_url
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert image_url: {e}")
                response.image_URL = ""  # Or some default value  

            try:
                response.created_at = Product_obj.created_at
            except (AttributeError, ValueError) as e:
                logger.warning(f"Failed to convert created_at: {e}")
                # Leave timestamp at default (epoch)
                
            try:
                response.updated_at = Product_obj.updated_at
            except (AttributeError, ValueError) as e:
                logger.warning(f"Failed to convert updated_at: {e}")
                # Leave timestamp at default (epoch)

            try:
                response.packaging_cost = Product_obj.packaging_cost
            except (AttributeError, TypeError) as e:
                logger.warning(f"Failed to convert packaging_cost: {e}")
                response.packaging_cost = 0.0  # Or some default value    


            logger.debug("entering Wire verification")
            if not self._verify_wire_format(response, product_pb2.product, f"product_id={Product_obj.product_uuid}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize Product {Product_obj.product_uuid}")
            return response
    
        except Exception as e:
            logger.error("Error Creating ",e)
            raise


    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def CreateProduct(self, request, context):

        
        category = Category.objects.get(category_uuid = request.category_uuid,store_uuid =request.store_uuid)
        diet_pref = DietaryPreference.objects.get(diet_pref_uuid=request.diet_pref_uuid,store_uuid =request.store_uuid)
        
        with transaction.atomic():
            product = Product.objects.create(
                store_uuid = request.store_uuid,
                name = request.name,
                description = request.description,
                status = Productstatus.Name(request.status),
                is_available = request.is_available,
                display_price = request.display_price,
                price = request.price,
                GST_percentage =request.GST_percentage,
                category = category,
                packaging_cost = request.packaging_cost

                )
        
            product.dietary_prefs.set([diet_pref])
            product.save()

            
            
            if getattr(request,"image_bytes",None):
                size = image_handler.check_size(request.image_bytes)
                if size > 5:
                    raise ValidationError(f"Image size:{size}mb exceeds 5mb")
                ext = image_handler.check_extension(request.image_bytes)
                if ext not in ['.jpg','.png','.jpeg']:
                    logger.debug(ext)
                    raise ValidationError(f"Unspported File Type {ext}")
            
                image_name = f"{product.store_uuid}/{product.category.category_uuid}/{product.product_uuid}"

                _,url = image_handler.upload_to_s3(
                    request.image_bytes,
                    bucket_name=BUCKET_NAME,
                    object_name=image_name,
                    aws_access_key=AWS_ACCESS_KEY_ID,
                    aws_secret_key=AWS_SECRET_ACCESS_KEY,
                    region_name=REGION_NAME
                )
                if _:
                    product.image_url = url
                    

            product.clean()
            product.save()
            logger.info(f"Created Product: {product.product_uuid} in category {product.category.category_uuid} at store {product.store_uuid}")
            return product_pb2.ProductResponse(
                product=self._product_to_proto(product))
       
    @handle_error
    @check_access(
    expected_types=["store","customer"],
    allowed_roles={"store":["admin","staff"]}
)
    def GetProduct(self, request, context):

        if getattr(request,"category_uuid",None):
            category = Category.objects.get(category_uuid = request.category_uuid,store_uuid =request.store_uuid)
            product = Product.objects.get(store_uuid = request.store_uuid,product_uuid = request.product_uuid,category=category)
        else:
            product = Product.objects.get(store_uuid = request.store_uuid,product_uuid = request.product_uuid)
        return product_pb2.ProductResponse(
            product= self._product_to_proto(product)
        )
        
    
    @handle_error
    @check_access(
    expected_types=["store","customer"],
    allowed_roles={"store":["admin","staff"]}
)
    def ListProducts(self, request, context):
        limit = request.limit if request.limit != "" else 10
        page = request.page if request.page != "" else 1

        if getattr(request,"category_uuid",None):
            products,next_page,prev_page = Product.objects.get_products(store_uuid=request.store_uuid,
                                                            category_uuid=request.category_uuid,
                                                            limit=limit,
                                                            page = page)
        
        else:
            products,next_page,prev_page = Product.objects.get_products(store_uuid=request.store_uuid,
                                                            limit=limit,
                                                            page =page)
        response = product_pb2.ListProductsResponse(
            products=[self._product_to_proto(x) for x in products],
            next_page=next_page,
            prev_page=prev_page

        )
        return response
    
    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
    def UpdateProduct(self, request, context):

        category = Category.objects.get(category_uuid = request.category_uuid,store_uuid =request.store_uuid)
        product = Product.objects.get(store_uuid = request.store_uuid,product_uuid = request.product_uuid,category=category)

        with transaction.atomic():
    
            if request.HasField('name'):
                    product.name = request.name

            if request.HasField('description'):
                product.description = request.description

            if request.HasField('status'):
                product.status = Productstatus.Name(request.status)
            
            if request.HasField('is_available'):
                product.is_available = request.is_available

            if request.HasField('display_price'):
                product.display_price = request.display_price

            if request.HasField('price'):
                product.price = request.price

            if request.HasField('GST_percentage'):
                product.GST_percentage = request.GST_percentage
            
            if request.HasField('packaging_cost'):
                product.packaging_cost = request.packaging_cost

            if request.HasField('new_category_uuid'):
                category = Category.objects.get(category_uuid = request.new_category_uuid)
                product.category = category

            if request.HasField('diet_pref_uuid'):
                diet_pref = DietaryPreference.objects.get(diet_pref_uuid = request.diet_pref_uuid)
                product.dietary_prefs.set([diet_pref])

            if request.HasField('image_bytes'):
                size = image_handler.check_size(request.image_bytes)
                if size > 5:
                    raise ValidationError(f"Image size:{size}mb exceeds 5mb")
                ext = image_handler.check_extension(request.image_bytes)
                if ext not in ['.jpg','.png','.jpeg']:
                    logger.debug(ext)
                    raise ValidationError(f"Unspported File Type {ext}")
            
                image_name = f"{product.store_uuid}/{product.category.category_uuid}/{product.product_uuid}"

                _,url = image_handler.upload_to_s3(
                    request.image_bytes,
                    bucket_name=BUCKET_NAME,
                    object_name=image_name,
                    aws_access_key=AWS_ACCESS_KEY_ID,
                    aws_secret_key=AWS_SECRET_ACCESS_KEY,
                    region_name=REGION_NAME
                )
                if _:
                    product.image_url = url
                    product.save()


            product.clean()
            product.save()

            logger.info(f"Product Updated For product id: {product.product_uuid}")
            return product_pb2.ProductResponse(
                product=self._product_to_proto(product)
            )   


    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
    def DeleteProduct(self, request, context):
        category = Category.objects.get(category_uuid = request.category_uuid,store_uuid =request.store_uuid)

        with transaction.atomic():
            product = Product.objects.get(store_uuid = request.store_uuid,product_uuid = request.product_uuid,category=category)
            product.delete()
        
            logger.info(f"Deleted product: {request.product_uuid}")
            return empty_pb2.Empty()

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
    def CreateCategory(self, request, context):
        with transaction.atomic():
            cat = Category.objects.create(
                store_uuid = request.store_uuid,
                name = request.name,
                description = request.description,
                display_order = request.display_order,
                is_available = request.is_available,
                is_active = request.is_active
            )
            logger.info(f"Category Id:{cat.category_uuid} Created at store Id:{cat.store_uuid}")

            return product_pb2.CategoryResponse(
                category= self._category_to_proto(cat)
            )
    
    @handle_error
    @check_access(
    expected_types=["store","customer"],
    allowed_roles={"store":["admin","staff"]})
    def GetCategory(self, request, context):
        
        category_uuid = request.category_uuid
        store_uuid = request.store_uuid

        category = Category.objects.get(category_uuid=category_uuid,store_uuid=store_uuid)

        return product_pb2.CategoryResponse(
            category=self._category_to_proto(category)
        )

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
    def UpdateCategory(self, request, context):
    
        category_obj = Category.objects.get(category_uuid=request.category_uuid,store_uuid=request.store_uuid)
        with transaction.atomic():
            if request.HasField('name'):
                category_obj.name = request.name 

            if request.HasField('description'):
                category_obj.description = request.description
            
            if request.HasField('is_available'):
                category_obj.is_available = request.is_available

            if request.HasField('display_order'):
                category_obj.display_order = request.display_order

            if request.HasField('is_active'):
                category_obj.is_active = request.is_active

            category_obj.full_clean()
            category_obj.save()
            logger.debug(category_obj)
            logger.info(f"Category Updated For category id: {category_obj.category_uuid}")
            return product_pb2.CategoryResponse(
                category=self._category_to_proto(category_obj)
            )

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
    def DeleteCategory(self, request, context):  
        with transaction.atomic():
            Category.objects.get(category_uuid = request.category_uuid,store_uuid=request.store_uuid).delete()
        
            logger.info(f"Deleted Category: {request.category_uuid}")
            return empty_pb2.Empty()
    
    @handle_error
    @check_access(
    expected_types=["store","customer"],
    allowed_roles={"store":["admin","staff"]}
)
    def ListCategory(self, request, context):
        limit = request.limit if request.limit != "" else 10
        page = request.page if request.page != "" else 1
        categories,next_page,prev_page = Category.objects.get_categories(
                                                        store_uuid=request.store_uuid,
                                                        limit=request.limit,
                                                        page = request.page)
        
        response = product_pb2.ListCategoryResponse(
            categories=[self._category_to_proto(x) for x in categories],
            next_page=next_page,
            prev_page=prev_page

        )
        return response 
    

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
    def CreateAddOn(self, request, context):
        product:Product = Product.objects.get(store_uuid = request.store_uuid,product_uuid = request.product_uuid)
        with transaction.atomic(): 
            add_on:Add_on = Add_on.objects.create(
                product = product,
                name = request.name,
                is_available = request.is_available,
                max_selectable = request.max_selectable,
                GST_percentage = request.GST_percentage,
                price = request.price,
                is_free = request.is_free
            )
            logger.info(f"Created Add-On:{add_on.add_on_uuid} for product id:{product.product_uuid} at Store id:{product.store_uuid}")
            return product_pb2.AddOnResponse(
                add_on=self._add_on_to_proto(add_on)
            )

    @handle_error
    @check_access(
    expected_types=["store","customer"],
    allowed_roles={"store":["admin","staff"]}
)
    def GetAddOn(self,request,context):

        product = Product.objects.get(store_uuid = request.store_uuid,product_uuid = request.product_uuid)
        add_on_obj = Add_on.objects.get(
            product = product,
            add_on_uuid = request.add_on_uuid
        )
        logger.info(f"Fetched Add-On:{add_on_obj.add_on_uuid} for product id:{product.product_uuid} at Store id:{product.store_uuid}")  
        return product_pb2.AddOnResponse(
            add_on= self._add_on_to_proto(add_on_obj),
        )
    
    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
    def UpdateAddOn(self, request, context):
        product = Product.objects.get(store_uuid = request.store_uuid,product_uuid = request.product_uuid)

        add_on = Add_on.objects.get(add_on_uuid=request.add_on_uuid,product=product)
        with transaction.atomic():
            if request.HasField('name'):
                add_on.name = request.name 

            if request.HasField('is_available'):
                add_on.is_available = request.is_available
            
            if request.HasField('max_selectable'):
                add_on.max_selectable = request.max_selectable

            if request.HasField('GST_percentage'):
                add_on.GST_percentage = request.GST_percentage

            if request.HasField('price'):
                add_on.price = request.price
            
            if request.HasField('is_free'):
                add_on.is_free = request.is_free

            add_on.save()
            logger.debug(add_on)
            logger.info(f"add_on Updated For add_on id: {add_on.add_on_uuid}")
            return product_pb2.AddOnResponse(
                add_on=self._add_on_to_proto(add_on)
            )
       
    @handle_error
    @check_access(
    expected_types=["store","customer"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=False
)
    def ListAddOn(self, request, context):

        product = Product.objects.get(store_uuid = request.store_uuid,product_uuid = request.product_uuid)
  
        limit = request.limit if request.limit != "" else 10
        page = request.page if request.page != "" else 1
        add_ons,next_page,prev_page = Add_on.objects.get_add_ons(
                                                        product = product,
                                                        limit=limit,
                                                        page = page
                                                        )
        logger.info(f"Successfully listed {len(add_ons)} Add-ons For product Id {request.product_uuid}")
        response = product_pb2.ListAddOnResponse(
            add_ons=[self._add_on_to_proto(x) for x in add_ons],
            next_page=next_page,
            prev_page=prev_page
        )
        return response

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
    def DeleteAddOn(self, request, context):
        product = Product.objects.get(store_uuid = request.store_uuid,product_uuid = request.product_uuid)
        with transaction.atomic():

            add_on = Add_on.objects.get(add_on_uuid = request.add_on_uuid,product=product)
            add_on.delete()
        
            logger.info(f"Deleted Add_on:{request.add_on_uuid} of Product:{product.product_uuid}")
            return empty_pb2.Empty()


    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
    def CreateDietPref(self, request, context):
        with transaction.atomic():
            diet_pref = DietaryPreference.objects.create(
                store_uuid = request.store_uuid,
                name = request.name,
                description = request.description,
            )

            if getattr(request,"icon_image_bytes",None):
                size = image_handler.check_size(request.icon_image_bytes)
                if size > 5:
                    raise ValidationError(f"Image size:{size}mb exceeds 5mb")
                ext = image_handler.check_extension(request.icon_image_bytes)
                if ext not in ['.jpg','.png','.jpeg']:
                    logger.debug(ext)
                    raise ValidationError(f"Unspported File Type {ext}")
            
                image_name = f"{diet_pref.store_uuid}/{diet_pref.diet_pref_uuid}"

                _,url = image_handler.upload_to_s3(
                    request.icon_image_bytes,
                    bucket_name=BUCKET_NAME,
                    object_name=image_name,
                    aws_access_key=AWS_ACCESS_KEY_ID,
                    aws_secret_key=AWS_SECRET_ACCESS_KEY,
                    region_name=REGION_NAME
                )
                if _:
                    diet_pref.icon_url = url
                    diet_pref.full_clean()
                    diet_pref.save()

                logger.info(f"Created Dietary Preference: {diet_pref.diet_pref_uuid} at store {diet_pref.store_uuid}")
            
            return product_pb2.DietPrefResponse(
                dietary_preference=self._diet_pref_to_proto(diet_pref)
            )
    
    @handle_error
    @check_access(
    expected_types=["store","customer"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=False
)
    def GetDietPref(self, request, context):
        diet_pref = DietaryPreference.objects.get(diet_pref_uuid=request.diet_pref_uuid,store_uuid=request.store_uuid)
        return product_pb2.DietPrefResponse(
            dietary_preference=self._diet_pref_to_proto(diet_pref)
        )

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
    def UpdateDietPref(self, request, context):
        diet_pref = DietaryPreference.objects.get(diet_pref_uuid=request.diet_pref_uuid,store_uuid=request.store_uuid)
        with transaction.atomic():
            if request.HasField('name'):
                diet_pref.name = request.name 

            if request.HasField('description'):
                diet_pref.description = request.description
            
            if request.HasField('icon_image_bytes'):
                size = image_handler.check_size(request.icon_image_bytes)
                if size > 5:
                    raise ValidationError(f"Image size:{size}mb exceeds 5mb")
                ext = image_handler.check_extension(request.icon_image_bytes)
                if ext not in ['.jpg','.png','.jpeg']:
                    logger.debug(ext)
                    raise ValidationError(f"Unspported File Type {ext}")
            
                image_name = f"{diet_pref.store_uuid}/{diet_pref.diet_pref_uuid}"

                _,url = image_handler.upload_to_s3(
                    request.icon_image_bytes,
                    bucket_name=BUCKET_NAME,
                    object_name=image_name,
                    aws_access_key=AWS_ACCESS_KEY_ID,
                    aws_secret_key=AWS_SECRET_ACCESS_KEY,
                    region_name=REGION_NAME
                )
                if _:
                    diet_pref.icon_url = url
                    diet_pref.save()

            diet_pref.full_clean()
            diet_pref.save()
            logger.info(f"Dietary Preference Updated For dietary preference id: {diet_pref.diet_pref_uuid}")
            return product_pb2.DietPrefResponse(
                dietary_preference=self._diet_pref_to_proto(diet_pref)
            )
    @handle_error
    @check_access(
    expected_types=["store","customer"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=False
)
    def ListDietPref(self, request, context):
        limit = request.limit if request.limit != "" else 10
        page = request.page if request.page != "" else 1
        diet_prefs,next_page,prev_page = DietaryPreference.objects.get_dietary_prefs(
                                                        store_uuid=request.store_uuid,
                                                        limit=limit,
                                                        page = page)
        
        response = product_pb2.ListDietPrefResponse(
            dietary_preferences=[self._diet_pref_to_proto(x) for x in diet_prefs],
            next_page=next_page,
            prev_page=prev_page

        )
        return response
    
    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True
)
    def DeleteDietPref(self, request, context):
        with transaction.atomic():
            DietaryPreference.objects.get(diet_pref_uuid = request.diet_pref_uuid,store_uuid=request.store_uuid).delete()
        
            logger.info(f"Deleted Dietary Preference: {request.diet_pref_uuid}")
            return empty_pb2.Empty()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add your services to the server
    product_pb2_grpc.add_ProductServiceServicer_to_server(ProductService(), server)
    
    # Get the port from environment variables
    grpc_port = os.getenv('GRPC_SERVER_PORT', '50052')
    
    # Bind the server to the specified port
    server.add_insecure_port(f'[::]:{grpc_port}')
    server.start()
    
    logger.info(f"gRPC server is running on port {grpc_port}")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

