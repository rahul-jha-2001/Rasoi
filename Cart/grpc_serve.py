
import os
from  datetime import datetime
import logging
from concurrent import futures

import django
from django.core.exceptions import ValidationError
from django.db import transaction
from django.core.exceptions import ValidationError,ObjectDoesNotExist,MultipleObjectsReturned,PermissionDenied
from django.db import IntegrityError,DatabaseError
import jwt.utils

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Cart.settings')
django.setup()

from typing import Any, Callable
import grpc
from grpc import RpcError,StatusCode
from grpc_interceptor import ServerInterceptor
from grpc_interceptor.exceptions import GrpcException,Unauthenticated,FailedPrecondition
from dotenv import load_dotenv
from google.protobuf.timestamp_pb2 import Timestamp
import google.protobuf.json_format as json_format

from google.protobuf import empty_pb2 
from api.models import Cart,CartItem,AddOn,Coupon,CouponUsage,Coupon_Validator
from Proto import cart_pb2_grpc as Cart_pb2_grpc
from Proto import cart_pb2 as Cart_pb2
from Proto.cart_pb2 import (
    ORDERTYPE,
    DISCOUNTTYPE,
    CARTSTATE,
)

from google.protobuf import empty_pb2

from utils.logger import Logger

load_dotenv()

logger = Logger("GRPC_service")


class CartVaildator:

    # def __init__(self):
    #     # Connect to the product and store gRPC services
    #     self.product_channel = grpc.insecure_channel('product-service:50051')
    #     self.store_channel = grpc.insecure_channel('store-service:50052')

    #     self.product_stub = product_pb2_grpc.ProductServiceStub(self.product_channel)
    #     self.store_stub = store_pb2_grpc.StoreServiceStub(self.store_channel)
    @staticmethod
    def validate_cart(cart:Cart, coupon:Coupon|None):

        errors = []
        total_price = 0

        if coupon is not None:
            flag,msg = Coupon_Validator.validate(coupon=coupon,cart=cart)
            if not flag:
                return {"valid": flag, "messeage": msg}

        return {"valid": flag, "messeage": "Cart is Valid"}
    

def handle_error(func):
    def wrapper(self, request, context):
        try:
            return func(self, request, context)
        except Cart.DoesNotExist:
            logger.warning(f"Cart Not Found: Cart_uuid:{getattr(request, 'cart_uuid', '')} Store_uuid:{getattr(request, 'store_uuid', '')} user_phone_no:{getattr(request, 'user_phone_no', '')}")
            context.abort(grpc.StatusCode.NOT_FOUND, f"Cart Not Found: Cart_uuid:{getattr(request, 'cart_uuid', '')} Store_uuid:{getattr(request, 'store_uuid', '')} user_phone_no:{getattr(request, 'user_phone_no', '')}")

        except CartItem.DoesNotExist:
            logger.error(f"CartItem Not Found: cart_item_uuid:{getattr(request, 'cart_item_uuid', '')}")
            context.abort(grpc.StatusCode.NOT_FOUND, f"CartItem Not Found: cart_item_uuid:{getattr(request, 'cart_item_uuid', '')}")
            
        except Coupon.DoesNotExist:
            logger.error(f"Coupon Not Found: coupon_uuid: {getattr(request, 'coupon_uuid', '')} coupon_code: {getattr(request, 'coupon_code', '')}")
            context.abort(grpc.StatusCode.NOT_FOUND, f"Coupon Not Found: coupon_uuid: {getattr(request, 'coupon_uuid', '')} coupon_code: {getattr(request, 'coupon_code', '')}")

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


class CartService(Cart_pb2_grpc.CartServiceServicer):

    def _verify_wire_format(self, GRPC_message, GRPC_message_type, context_info=""):
        try:
            serialized = GRPC_message.SerializeToString()
            test_msg = GRPC_message_type()
            test_msg.ParseFromString(serialized)

            logger.debug(f"Message before serialization: {GRPC_message}")
            logger.debug(f"Serialized Message Size: {len(serialized)} bytes ")
            logger.debug(f"Serialized data (hex): {serialized.hex()}")

            original_fields = GRPC_message.ListFields()
            test_fields = test_msg.ListFields()

            if len(original_fields) != len(test_fields):
                logger.error(f"Field count mismatch - Original: {len(original_fields)}, Deserialized: {len(test_fields)}")
                logger.error(f"Original fields: {[f[0].name for f in original_fields]}")
                logger.error(f"Deserialized fields: {[f[0].name for f in test_fields]}")

            # Log field values for debugging
            logger.debug("Original field values:")
            for (field1, value1), (field2, value2) in zip(original_fields, test_fields):
                logger.debug(f"Field: {field1.name}, Og_Value: {value1} Test_Value: {value2}")

            # logger.debug("Deserialized field values:")
            # for field2, value2 in test_fields:
            #     logger.debug(f"Field: {field.name}, Value: {value}")

            return True
        except Exception as e:
            logger.error(f"Wire Format verification failed for {GRPC_message_type.__name__} {context_info}: {str(e)}")
            logger.error(f"Serialized data (hex): {serialized.hex()}")
            return False


    def _AddOn_to_response(self, add_on: AddOn) -> Cart_pb2.AddOn:
        try:
            response = Cart_pb2.AddOn()
            try:
                response.cart_item_uuid = str(add_on.cart_item.cart_item_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert cart_uuid: {e}")
                raise

            try:
                response.add_on_name = add_on.add_on_name
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert add_on_name: {e}")
                raise

            try:
                response.add_on_uuid = str(add_on.add_on_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert add_on_uuid: {e}")
                raise

            try:
                response.quantity = int(add_on.quantity)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert quantity: {e}")
                raise

            try:
                response.unit_price = float(add_on.unit_price)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert unit_price: {e}")
                raise

            try:
                response.is_free = bool(add_on.is_free)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert is_free: {e}")
                raise

            try:
                response.subtotal_amount = float(add_on.sub_total)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert subtotal_amount: {e}")
                raise
            
            if not self._verify_wire_format(response, Cart_pb2.AddOn, f"Addon_id={add_on.add_on_uuid}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize Add On {add_on.add_on_uuid}")
            
            
            return response
        
        except Exception as e:
            logger.error(f"Unexpected error in _AddOn_to_response: {e}")
            raise
    
   
    def _CartItem_to_response(self,cart_item:CartItem) -> Cart_pb2.CartItem:
        try:
            response = Cart_pb2.CartItem()
            try:
                response.cart_item_uuid = str(cart_item.cart_item_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert cart_item_uuid: {e}")
                raise

            try:
                response.cart_uuid = str(cart_item.cart.cart_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert cart_uuid: {e}")
                raise

            try:
                response.product_name = str(cart_item.product_name)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert product_name: {e}")
                raise
            try:
                response.discount = float(cart_item.discount)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert discount: {e}")
                raise

            try:
                response.product_uuid = str(cart_item.product_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert product_uuid: {e}")
                raise

            try:
                response.tax_percentage = float(cart_item.tax_percentage)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert tax_percentage: {e}")
                raise

            # Handling numeric fields with default values
            try:
                response.unit_price = float(cart_item.unit_price)
                response.quantity = int(cart_item.quantity)
                response.add_ons_total = float(cart_item.add_ons_total)
                response.subtotal_amount = float(cart_item.sub_total)
                response.discount_amount = float(cart_item.discount_amount)
                response.price_before_tax = float(cart_item.price_before_tax)
                response.tax_amount = float(cart_item.tax_amount)
                response.final_price = float(cart_item.final_price)
                response.packaging_cost = float(cart_item.packaging_cost)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert numeric fields: {e}")
                raise

            # Handling repeated field `add_ons`
            try:
                response.add_ons.extend([self._AddOn_to_response(add_on) for add_on in cart_item.get_add_on()])
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert add_ons: {e}")
                raise

            if not self._verify_wire_format(response, Cart_pb2.CartItem, f"Cartitem_id={cart_item.cart_item_uuid}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize Cart Item {cart_item.cart_item_uuid}")
            return response
        except Exception as e:
            logger.error(f"Unexpected error in _CartItem_to_response: {e}")
            raise


    def _Cart_to_response(self, cart: Cart) -> Cart_pb2.Cart:
        try:
            response = Cart_pb2.Cart()  # Add this line first
            
            try:
                response.store_uuid = str(cart.store_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert store_uuid: {e}")
                raise

            try:
                response.cart_uuid = str(cart.cart_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert cart_uuid: {e}")
                raise
            

            try:
                response.user_phone_no = str(cart.user_phone_no)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert user_phone_no: {e}")
                raise

            try:
                response.order_type = int(ORDERTYPE.Value(cart.order_type))
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert order_type: {e}")
                raise

            try:
                response.table_no = str(cart.table_no) or ""
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert table_no: {e}")
                raise

            try:
                response.vehicle_no = str(cart.vehicle_no) or ""
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert vehicle_no: {e}")
                raise

            try:
                response.vehicle_description = str(cart.vehicle_description) or ""
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert vehicle_description: {e}")
                raise

            try:
                response.coupon_code = str(cart.coupon_code) or ""
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert coupon_code: {e}")
                raise

            try:
                response.special_instructions = str(cart.special_instructions) or ""
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert special_instructions: {e}")
                raise

            # Handling repeated field `items`
            try:
                ITEMS = [self._CartItem_to_response(item) for item in cart.get_items()]
                response.items.extend(ITEMS or [])
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert items: {e}")
                raise

            # Handling float fields with default 0.0
            try:
                response.sub_total = float(cart.sub_total)
                response.total_discount = float(cart.total_discount)
                response.total_price_before_tax = float(cart.total_price_before_tax)
                response.total_tax = float(cart.tax_amount)
                response.packaging_cost = float(cart.packaging_cost)
                response.final_amount = float(cart.final_amount)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert float fields: {e}")
                raise

            try:
                response.cart_state = CARTSTATE.Value(cart.state)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert cart_state: {e}")
                raise
            # Handling timestamps
            try:
                if cart.created_at:
                    response.created_at.FromDatetime(cart.created_at)
                if cart.updated_at:
                    response.updated_at.FromDatetime(cart.updated_at)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert timestamps: {e}")
                raise

            if not self._verify_wire_format(response, Cart_pb2.Cart, f"Cart_id={cart.cart_uuid}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize Cart {cart.cart_uuid}")
            logger.info(f"{response}")
            return Cart_pb2.CartResponse(cart=response)
        except Exception as e:
            logger.error(f"Unexpected error in _Cart_to_response: {e}",e)
            raise


    @handle_error
    @check_access(roles=["user","store","internal"])
    def CreateCart(self, request, context):

        try:
            with transaction.atomic():
                cart = Cart.objects.get_active_cart(store_uuid =  request.store_uuid ,user_phone_no = request.user_phone_no)
                cart.order_type = ORDERTYPE.Name(request.order_type)
                cart.table_no = request.table_no or ""
                cart.vehicle_no = request.vehicle_no or ""
                cart.vehicle_description = request.vehicle_description or ""
                logger.info(f"Fetched Cart{cart.cart_uuid} for Phone No:{cart.user_phone_no} at store: {cart.store_uuid}")
                return self._Cart_to_response(cart)
        except Cart.DoesNotExist:
            with transaction.atomic():
                cart = Cart.objects.create(store_uuid = request.store_uuid,
                    user_phone_no = request.user_phone_no,
                    order_type = ORDERTYPE.Name(request.order_type),
                    table_no = request.table_no or "",
                    vehicle_no = request.vehicle_no or "",
                    vehicle_description = request.vehicle_description or "")
                
                logger.info(f"Created Cart{cart.cart_uuid} for Phone No:{cart.user_phone_no} at store: {cart.store_uuid}")
                return self._Cart_to_response(cart)
            
    @handle_error
    @check_access(roles=["user","store","internal"])
    def GetCart(self, request, context):
        
        if getattr(request,"cart_uuid",None):
            cart = Cart.objects.get_active_cart(cart_uuid=request.cart_uuid)
            return self._Cart_to_response(cart)
        
        # Fall back to store_uuid + user_phone_no combination
        elif getattr(request,"store_uuid",None) and getattr(request,"user_phone_no",None):
            cart = Cart.objects.get_active_cart(
                store_uuid=request.store_uuid,
                user_phone_no=request.user_phone_no
            )
            return self._Cart_to_response(cart)
        
        else:
            raise ValueError("Must provide either cart_uuid or both store_uuid and user_phone_no")

        
    @handle_error    
    @check_access(roles=["user","store","internal"])
    def UpdateCart(self, request, context):
        cart

        if getattr(request,"cart_uuid",None):
            cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)
        
        # Fall back to store_uuid + user_phone_no combination
        elif getattr(request,"store_uuid",None) and getattr(request,"user_phone_no",None):
            cart = Cart.objects.get_active_cart(
                store_uuid=request.store_uuid,
                user_phone_no=request.user_phone_no
            )
        else:
            raise ValueError("Must provide either cart_uuid or both store_uuid and user_phone_no")
        with transaction.atomic():
            logger.debug(f"Before Update:{cart}")
            if request.cart.order_type:
                cart.order_type = ORDERTYPE.Name(request.cart.order_type)
            if request.cart.table_no:
                cart.cart.table_no = request.cart.table_no
            if request.cart.vehicle_no:
                cart.vehicle_no = request.cart.vehicle_no    
            if request.cart.vehicle_description:
                cart.vehicle_description = request.cart.vehicle_description
            if request.cart.speacial_instructions:
                cart.speacial_instructions = request.cart.speacial_instructions
            
            logger.debug(f"After Update:{cart}")
            cart.full_clean()
            cart.save() 
            

            logger.info(f"Cart:{cart.cart_uuid} Updated for {cart.store_uuid} and {cart.user_phone_no}")
            return self._Cart_to_response(cart)

    @handle_error
    @check_access(roles=["user","store","internal"])
    def DeleteCart(self, request, context):

        if getattr(request,"cart_uuid",None):
            cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)
            cart.delete()
            logger.info(f"Cart:{cart.cart_uuid} for Phone_no:{cart.user_phone_no} at store:{cart.store_uuid} ")
            return empty_pb2()
        

        if getattr(request,"store_uuid",None) and getattr(request,"user_phone_no",None):
            cart = Cart.objects.get_active_cart(store_uuid = request.store_uuid,user_phone_no = request.user_phone_no)
            cart.delete()
            logger.info(f"Cart:{cart.cart_uuid} for Phone_no:{cart.user_phone_no} at store:{cart.store_uuid} ")
            return empty_pb2()
        
    @handle_error    
    @check_access(roles=["user","store","internal"])
    def AddCartItem(self, request, context):
        cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)

        with transaction.atomic():
            cart_item = CartItem.objects.create(
                cart = cart,
                product_name = request.cart_item.product_name,
                product_uuid = request.cart_item.product_uuid,
                tax_percentage = request.cart_item.tax_percentage,
                packaging_cost = request.cart_item.packaging_cost,
                unit_price = request.cart_item.unit_price,
                quantity = request.cart_item.quantity
            )

            logger.info(f"Cart-Item:{cart_item.cart_item_uuid} added to cart:{cart_item.cart.cart_uuid}")
            return self._Cart_to_response(cart)

    @handle_error
    @check_access(roles=["user","store","internal"])
    def RemoveCartItem(self, request, context):
        cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)

        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)
        with transaction.atomic():
            cart_item.delete()
            logger.info(f"Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
            return self._Cart_to_response(cart)


    @handle_error
    @check_access(roles=["user","store","internal"])
    def CreateAddOn(self, request, context):
        cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)
        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)
        with transaction.atomic():
            add_on = AddOn.objects.create(
                cart_item = cart_item,
                add_on_name = request.add_on.add_on_name,
                add_on_uuid = request.add_on.add_on_uuid,
                quantity = request.add_on.quantity,
                unit_price = request.add_on.unit_price,
                is_free = request.add_on.is_free
            )
            logger.info(f"Add-on:{add_on.add_on_uuid} to Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
            return self._Cart_to_response(cart)

    @handle_error
    @check_access(roles=["user","store","internal"])
    def UpdateAddOn(self, request, context):
        cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)
        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)
        add_on = AddOn.objects.get(cart_item = cart_item,add_on_uuid = request.add_on_uuid)
        with transaction.atomic():
            if request.add_on.add_on_name:
                add_on.add_on_name = request.add_on.add_on_name
            if request.add_on.quantity:
                add_on.quantity = request.add_on.quantity
            if request.add_on.unit_price:
                add_on.unit_price = request.add_on.unit_price
            if request.add_on.is_free:
                add_on.is_free = request.add_on.is_free

            add_on.save()
            logger.info(f"Updated Add-on:{add_on.add_on_uuid} in Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
            return self._Cart_to_response(cart)

    @handle_error
    @check_access(roles=["user","store","internal"])
    def RemoveAddOn(self, request, context):
        cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)
        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)
        add_on = AddOn.objects.get(cart_item = cart_item,add_on_uuid = request.add_on_uuid)
        with transaction.atomic():
            add_on.delete()
            logger.info(f"Removed Add-on:{add_on.add_on_uuid} from Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
            return self._Cart_to_response(cart)

    @handle_error
    @check_access(roles=["user","store","internal"])
    def AddQuantity(self, request, context):
        cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)

        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)
        with transaction.atomic():
            cart_item.add_quantity(1)
            logger.info(f"Add Quantity t0 Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
            return self._Cart_to_response(cart)

    @handle_error
    @check_access(roles=["user","store","internal"])
    def RemoveQuantity(self, request, context):
        cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)

        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)
        with transaction.atomic():
            if cart_item.quantity == 1:
                cart_item.delete()
                logger.info(f"Deleted Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
                return self._Cart_to_response(cart)
            cart_item.remove_quantity(1)
            logger.info(f"Removed Quantity t0 Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
            return self._Cart_to_response(cart)

    @handle_error
    @check_access(roles=["user","store","internal"])
    def IncreaseAddOnQuantity(self, request, context):
        cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)
        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)
        add_on = AddOn.objects.get(cart_item = cart_item,add_on_uuid = request.add_on_uuid)
        with transaction.atomic():
            add_on.add_quantity(1)
            logger.info(f"Increased Quantity to Add-on:{add_on.add_on_uuid} in Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
            return self._Cart_to_response(cart)

    @handle_error
    @check_access(roles=["user","store","internal"])
    def RemoveAddOnQuantity(self, request, context):
        cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)
        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)
        add_on = AddOn.objects.get(cart_item = cart_item,add_on_uuid = request.add_on_uuid)
        
        with transaction.atomic():
            if add_on.quantity == 1:
                add_on.delete()
                logger.info(f"Deleted Add-on:{add_on.add_on_uuid} in Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
                return self._Cart_to_response(cart)
            add_on.remove_quantity(1)
            logger.info(f"Removed Quantity to Add-on:{add_on.add_on_uuid} in Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
            return self._Cart_to_response(cart)

   
    @handle_error
    @check_access(roles=["user","store","internal"])
    def ValidateCoupon(self, request, context):
        cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)

        coupon  = Coupon.objects.get(coupon_code = request.coupon_code,store_uuid = cart.store_uuid)
        Valid,message = Coupon_Validator.validate(coupon=coupon,cart=cart)
        if Valid:
            cart.coupon_code = coupon.coupon_code
            cart.apply_discount(coupon.discount)
            cart.save()
        logger.info(f"Coupon:{coupon.coupon_code} Validation done Valid:{Valid} message:{message}")
        return Cart_pb2.ValidCouponResponse(Valid=Valid,message=message)

    @handle_error
    @check_access(roles=["user","store","internal"])
    def AddCoupon(self, request, context):
        
        cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)

        coupon  = Coupon.objects.get(coupon_code = request.coupon_code,cart_uuid = request.cart_uuid)
        
        Valid,message = Coupon_Validator.validate(coupon=coupon,cart=cart)
        
        if not Valid:
            raise ValidationError(message=message)
        
        with transaction.atomic():
            cart.apply_discount(discount=coupon.discount)
            logger.info(f"Applied discount to Cart:{cart.cart_uuid} from coupon {coupon.coupon_uuid}")
            return self._Cart_to_response(cart=cart)

    @handle_error
    @check_access(roles=["user","store","internal"])
    def RemoveCoupon(self, request, context):
        cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)
        with transaction.atomic():
            cart.remove_discount()
            return self._Cart_to_response(cart)

    @handle_error
    @check_access(roles=["user","store","internal"])
    def ValidateCart(self,request,context):
        # Get the cart based on cart_uuid
            cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)
            with transaction.atomic():
                # Check if the cart has a coupon code
                if cart.coupon_code:
                    try:
                        # Get the coupon object
                        coupon = Coupon.objects.get(store_uuid=cart.store_uuid, coupon_code=cart.coupon_code)

                        # Validate the cart with the coupon using CartValidator
                        temp = CartVaildator.validate_cart(cart=cart, coupon=coupon)
                        if temp["valid"]:
                            # If the coupon is valid, record its usage
                            coupon_usage = CouponUsage.objects.create(
                                coupon=coupon,
                                user_phone_no=cart.user_phone_no,
                                cart_uuid=cart.cart_uuid
                            )
                            logger.info(f"Coupon Usage recorded for coupon:{coupon.coupon_code} by User:{coupon_usage.user_phone_no}")
                        else:
                            logger.warning(f"Cart validation failed for coupon: {cart.coupon_code} and cart: {cart.cart_uuid} for {temp["messeage"]}")
                            raise ValidationError(f"Cart validation failed for coupon: {cart.coupon_code} and cart: {cart.cart_uuid} for {temp["messeage"]}")

                    except ObjectDoesNotExist:
                        logger.error(f"Coupon with code {cart.coupon_code} not found for store {cart.store_uuid}")
                        raise
                cart.lock_cart()

                logger.info(f"Cart {cart.cart_uuid} locked at {cart.updated_at}")

                # Indicate successful validation and locking
                return self._Cart_to_response(cart)

class CouponService(Cart_pb2_grpc.CouponServiceServicer):
    
    
    def _verify_wire_format(self, GRPC_message, GRPC_message_type, context_info=""):
        try:
            serialized = GRPC_message.SerializeToString()
            test_msg = GRPC_message_type()
            test_msg.ParseFromString(serialized)

            logger.debug(f"Message before serialization: {GRPC_message}")
            logger.debug(f"Serialized Message Size: {len(serialized)} bytes ")
            logger.debug(f"Serialized data (hex): {serialized.hex()}")

            original_fields = GRPC_message.ListFields()
            test_fields = test_msg.ListFields()

            if len(original_fields) != len(test_fields):
                logger.error(f"Field count mismatch - Original: {len(original_fields)}, Deserialized: {len(test_fields)}")
                logger.error(f"Original fields: {[f[0].name for f in original_fields]}")
                logger.error(f"Deserialized fields: {[f[0].name for f in test_fields]}")

            # Log field values for debugging
            logger.debug("Original field values:")
            for (field1, value1), (field2, value2) in zip(original_fields, test_fields):
                logger.debug(f"Field: {field1.name}, Og_Value: {value1} Test_Value: {value2}")

            # logger.debug("Deserialized field values:")
            # for field2, value2 in test_fields:
            #     logger.debug(f"Field: {field.name}, Value: {value}")

            return True
        except Exception as e:
            logger.error(f"Wire Format verification failed for {GRPC_message_type.__name__} {context_info}: {str(e)}")
            logger.error(f"Serialized data (hex): {serialized.hex()}")
            return False


    def _Coupon_to_response(self,coupon:Coupon) -> Cart_pb2.Coupon:
        try:
            response = Cart_pb2.Coupon()

            try:
                response.coupon_uuid = str(coupon.coupon_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert coupon_uuid: {e}")
                raise

            try:
                response.store_uuid = str(coupon.store_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert store_uuid: {e}")
                raise

            try:
                response.coupon_code = coupon.coupon_code
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert coupon_code: {e}")
                raise

            try:
                response.discount_type = DISCOUNTTYPE.Value(coupon.discount_type)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert discount_type: {e}")
                raise

            try:
                response.valid_from = coupon.valid_from
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert valid_from: {e}")
                raise

            try:
                response.valid_to = coupon.valid_to
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert valid_to: {e}")
                raise

            try:
                response.usage_limit_per_user = int(coupon.usage_limit_per_user)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert usage_limit_per_user: {e}")
                raise

            try:
                response.total_usage_limit = int(coupon.total_usage_limit)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert total_usage_limit: {e}")
                raise

            try:
                response.discount = float(coupon.discount)  # Fixing typo in 'dicount' -> 'discount'
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert discount: {e}")
                raise

            try:
                response.min_spend = float(coupon.min_spend)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert min_spend: {e}")
                raise
            
            try:
                response.max_discount = float(coupon.max_discount)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert max_discount: {e}")
                raise

            try:
                response.is_for_new_users = bool(coupon.is_for_new_users)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert is_for_new_users: {e}")
                raise

            try:
                response.description = coupon.description
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert description: {e}")
                raise

            try:
                response.max_cart_value = float(coupon.max_cart_value or 0.0)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert max_cart_value: {e}")
                raise

            try:
                response.is_active = bool(coupon.is_active)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert is_active: {e}")
                raise

            if not self._verify_wire_format(response, Cart_pb2.Coupon, f"Coupon_id:{coupon.coupon_uuid}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize Coupon_id:{coupon.coupon_uuid}")
            return response
        except Exception as e:
            logger.error(f"Unexpected error in _Coupon_to_response: {e}")
            raise
    
    def _CouponUsage_to_response(self,coupon_usage:CouponUsage) -> Cart_pb2.CouponUsage:
        try:
            response = Cart_pb2.CouponUsage()

            try:
                response.usage_uuid = str(coupon_usage.usage_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert usage_uuid: {e}")
                raise

            try:
                response.Coupon_uuid = str(coupon_usage.coupon.coupon_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert Coupon_uuid: {e}")
                raise

            try:
                response.user_phone_no = coupon_usage.user_phone_no
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert user_phone_no: {e}")
                raise

            try:
                response.used_at = coupon_usage.used_at
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert used_at: {e}")
                raise

            try:
                response.cart_uuid = str(coupon_usage.cart_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert order_uuid: {e}")
                raise

            if not self._verify_wire_format(response, Cart_pb2.CouponUsage, f"Coupon_usage_id:{coupon_usage.coupon.coupon_uuid}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize Coupon_usage_id:{coupon_usage.coupon.coupon_uuid}")
            return response
        except Exception as e:
            logger.error(f"Unexpected error in _CouponUsage_to_response: {e}")
            raise
    
    @handle_error
    @check_access(roles=["store","internal"])
    def CreateCoupon(self,request,context):
        with transaction.atomic():
            coupon =  Coupon.objects.create(

                store_uuid = request.store_uuid,
                coupon_code = request.coupon.coupon_code,
                discount_type = DISCOUNTTYPE.Name(request.coupon.discount_type),
                
                valid_from = datetime.fromtimestamp(request.coupon.valid_from.seconds),
                valid_to = datetime.fromtimestamp(request.coupon.valid_to.seconds),

                usage_limit_per_user = request.coupon.usage_limit_per_user,
                total_usage_limit = request.coupon.total_usage_limit,

                discount = request.coupon.discount,

                min_spend = request.coupon.min_spend,
                max_discount = request.coupon.max_discount,
                is_for_new_users = request.coupon.is_for_new_users,
                description = request.coupon.description,
                is_active = request.coupon.is_active,
            )
            logger.info(
                f"Created Coupon:{coupon.coupon_uuid} at store:{coupon.store_uuid}"
            )

            return self._Coupon_to_response(coupon=coupon)

    @handle_error
    @check_access(roles=["store","internal"])       
    def GetCoupon(self,request,context):

        coupon = Coupon.objects.get(coupon_uuid=request.coupon_uuid,
                                    store_uuid = request.store_uuid)
        
        return self._Coupon_to_response(coupon)


    @handle_error    
    @check_access(roles=["store","internal"])
    def UpdateCoupon(self,request,context):
        coupon = Coupon.objects.get(coupon_uuid=request.coupon_uuid, store_uuid=request.store_uuid)
        with transaction.atomic():
            if request.coupon_code:
                coupon.coupon_code = request.coupon_code
            
            if request.discount_type:
                try:
                    coupon.discount_type = DISCOUNTTYPE.Value(request.discount_type)
                except KeyError:
                    logger.warning(f"Invalid discount_type: {request.discount_type}")
                    raise ValueError("Invalid discount type provided")

            if request.valid_from:
                coupon.valid_from = request.valid_from
            if request.valid_to:
                coupon.valid_to = request.valid_to
            
            coupon.usage_limit_per_user = request.usage_limit_per_user or coupon.usage_limit_per_user
            coupon.total_usage_limit = request.total_usage_limit or coupon.total_usage_limit
            coupon.discount = request.discount or coupon.discount
            coupon.min_spend = request.min_spend or coupon.min_spend
            coupon.max_discount = request.max_discount or coupon.max_discount
            coupon.is_for_new_users = request.is_for_new_users
            coupon.description = request.description or coupon.description
            coupon.max_cart_value = request.max_cart_value or coupon.max_cart_value
            coupon.is_active = request.is_active

            coupon.save()  # ✅ Save the updated coupon

            return self._Coupon_to_response(coupon)

        
    @handle_error
    @check_access(roles=["store","internal"])
    def DeleteCoupon(self,request,context):
        coupon = Coupon.objects.get(coupon_uuid=request.coupon_uuid,
                                    store_uuid = request.store_uuid)
        with transaction.atomic():
            coupon.delete()
            logger.info(f"Coupon:{coupon.coupon_uuid} at store_uuid:{coupon.store_uuid}")        
            return self._Coupon_to_response(coupon)
        
    @handle_error
    @check_access(roles=["store","internal"])
    def listCoupon(self,request,context):
        coupons,next_page,prev_page = Coupon.objects.get_coupons()

        return Cart_pb2.listCouponResponse(
            coupons=[self._Coupon_to_response(coupon) for coupon in coupons],
            next_page=next_page,
            prev_page=prev_page
            )   

    @handle_error
    @check_access(roles=["store","internal"])
    def GetCouponUsage(self, request, context):
        coupon  = Coupon.objects.get(store_uuid= request.store_uuid,coupon_uuid = request.coupon_uuid)

        coupon_usage,next_page,prev_page = CouponUsage.objects.get_coupon_usage()

        return Cart_pb2.GetCouponUsageResponse(
            coupon_usage_list=[self._CouponUsage_to_response(usage) for usage in coupon_usage],
            next_page=next_page,
            prev_page= prev_page
        )



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    Cart_pb2_grpc.add_CartServiceServicer_to_server(CartService(),server)
    Cart_pb2_grpc.add_CouponServiceServicer_to_server(CouponService(),server)

    grpc_port = os.getenv('GRPC_SERVER_PORT', '50051')

    server.add_insecure_port(f"[::]:{grpc_port}")
    server.start()
    logger.info(f"Server Stated at {grpc_port}")
    server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig(level= logging.INFO)
    serve()
