import sys
import os
from  datetime import datetime
import logging
from concurrent import futures

import django
from django.core.exceptions import ValidationError
from django.db import transaction
from django.core.exceptions import ValidationError,ObjectDoesNotExist,MultipleObjectsReturned,PermissionDenied
from django.db import IntegrityError,DatabaseError

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Cart.settings')
django.setup()


import grpc
import traceback
from decimal import Decimal as DecimalType
from dotenv import load_dotenv

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
                response.subtotal_amount = float(cart_item.subtotal_amount)
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
                response.speacial_instructions = str(cart.speacial_instructions) or ""
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
                response.total_subtotal = float(cart.total_subtotal)
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
    @transaction.atomic
    def CreateCart(self, request, context):
        try:
            cart = Cart.objects.get(store_uuid =  request.store_uuid ,user_phone_no = request.user_phone_no)
            cart.order_type = ORDERTYPE.Name(request.order_type)
            cart.table_no = request.table_no or ""
            cart.vehicle_no = request.vehicle_no or ""
            cart.vehicle_description = request.vehicle_description or ""
            logger.info(f"Fetched Cart{cart.cart_uuid} for Phone No:{cart.user_phone_no} at store: {cart.store_uuid}")
            return self._Cart_to_response(cart)
        except Cart.DoesNotExist:
            cart = Cart.objects.create(store_uuid = request.store_uuid,
                user_phone_no = request.user_phone_no,
                order_type = ORDERTYPE.Name(request.order_type),
                table_no = request.table_no or "",
                vehicle_no = request.vehicle_no or "",
                vehicle_description = request.vehicle_description or "")
            
            logger.info(f"Created Cart{cart.cart_uuid} for Phone No:{cart.user_phone_no} at store: {cart.store_uuid}")
            return self._Cart_to_response(cart)
        
    @handle_error    
    def GetCart(self, request, context):
        # Check for cart_uuid first since it's more specific
        if request.cart_uuid:
            cart = Cart.objects.get(cart_uuid=request.cart_uuid)
            return self._Cart_to_response(cart)
        
        # Fall back to store_uuid + user_phone_no combination
        elif request.store_uuid and request.user_phone_no:
            cart = Cart.objects.get(
                store_uuid=request.store_uuid,
                user_phone_no=request.user_phone_no
            )
            return self._Cart_to_response(cart)
        
        else:
            raise ValueError("Must provide either cart_uuid or both store_uuid and user_phone_no")

        
    @handle_error    
    @transaction.atomic
    def UpdateCart(self, request, context):
        if request.cart_uuid:
            cart = Cart.objects.get(cart_uuid=request.cart_uuid)
        
        # Fall back to store_uuid + user_phone_no combination
        elif request.store_uuid and request.user_phone_no:
            cart = Cart.objects.get(
                store_uuid=request.store_uuid,
                user_phone_no=request.user_phone_no
            )
        else:
            raise ValueError("Must provide either cart_uuid or both store_uuid and user_phone_no")
        
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

    @transaction.atomic
    def DeleteCart(self, request, context):

        if request.HasField("cart_uuid"):
            cart = Cart.objects.get(cart_uuid = request.cart_uuid)
            cart.delete()
            logger.info(f"Cart:{cart.cart_uuid} for Phone_no:{cart.user_phone_no} at store:{cart.store_uuid} ")
            return empty_pb2()
        

        if request.HasField("store_uuid") and request.HasField("user_phone_no"):
            cart = Cart.objects.get(store_uuid = request.store_uuid,user_phone_no = request.user_phone_no)
            cart.delete()
            logger.info(f"Cart:{cart.cart_uuid} for Phone_no:{cart.user_phone_no} at store:{cart.store_uuid} ")
            return empty_pb2()
        
    @handle_error    
    @transaction.atomic
    def AddCartItem(self, request, context):
        cart = Cart.objects.get(cart_uuid = request.cart_uuid)

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
    @transaction.atomic
    def RemoveCartItem(self, request, context):
        cart = Cart.objects.get(cart_uuid = request.cart_uuid)

        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)

        cart_item.delete()
        logger.info(f"Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
        return self._Cart_to_response(cart)


    @handle_error
    @transaction.atomic
    def CreateAddOn(self, request, context):
        cart = Cart.objects.get(cart_uuid = request.cart_uuid)
        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)

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
    @transaction.atomic
    def UpdateAddOn(self, request, context):
        cart = Cart.objects.get(cart_uuid = request.cart_uuid)
        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)
        add_on = AddOn.objects.get(cart_item = cart_item,add_on_uuid = request.add_on_uuid)

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
    @transaction.atomic
    def RemoveAddOn(self, request, context):
        cart = Cart.objects.get(cart_uuid = request.cart_uuid)
        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)
        add_on = AddOn.objects.get(cart_item = cart_item,add_on_uuid = request.add_on_uuid)
        add_on.delete()
        logger.info(f"Removed Add-on:{add_on.add_on_uuid} from Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
        return self._Cart_to_response(cart)

    @handle_error
    @transaction.atomic
    def AddQuantity(self, request, context):
        cart = Cart.objects.get(cart_uuid = request.cart_uuid)

        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)

        cart_item.add_quantity(1)
        logger.info(f"Add Quantity t0 Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
        return self._Cart_to_response(cart)

    @handle_error
    @transaction.atomic
    def RemoveQuantity(self, request, context):
        cart = Cart.objects.get(cart_uuid = request.cart_uuid)

        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)
        if cart_item.quantity == 1:
            cart_item.delete()
            logger.info(f"Deleted Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
            return self._Cart_to_response(cart)
        cart_item.remove_quantity(1)
        logger.info(f"Removed Quantity t0 Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
        return self._Cart_to_response(cart)

    @handle_error
    @transaction.atomic
    def IncreaseAddOnQuantity(self, request, context):
        cart = Cart.objects.get(cart_uuid = request.cart_uuid)
        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)
        add_on = AddOn.objects.get(cart_item = cart_item,add_on_uuid = request.add_on_uuid)
        add_on.add_quantity(1)
        logger.info(f"Increased Quantity to Add-on:{add_on.add_on_uuid} in Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
        return self._Cart_to_response(cart)

    @handle_error
    @transaction.atomic
    def RemoveAddOnQuantity(self, request, context):
        cart = Cart.objects.get(cart_uuid = request.cart_uuid)
        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)
        add_on = AddOn.objects.get(cart_item = cart_item,add_on_uuid = request.add_on_uuid)
        if add_on.quantity == 1:
            add_on.delete()
            logger.info(f"Deleted Add-on:{add_on.add_on_uuid} in Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
            return self._Cart_to_response(cart)
        add_on.remove_quantity(1)
        logger.info(f"Removed Quantity to Add-on:{add_on.add_on_uuid} in Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
        return self._Cart_to_response(cart)

   
    @handle_error
    def ValidateCoupon(self, request, context):
        cart = Cart.objects.get(cart_uuid = request.cart_uuid)

        coupon  = Coupon.objects.get(coupon_code = request.coupon_code,cart_uuid = request.cart_uuid)
        Valid,message = Coupon_Validator.validate(coupon=coupon,cart=cart)
        logger.info(f"Coupon:{coupon.coupon_code} Validation done Valid:{Valid} message:{message}")
        return Cart_pb2.ValidCouponResponse(Valid=Valid,message=message)

    @handle_error
    @transaction.atomic
    def AddCoupon(self, request, context):
        
        cart = Cart.objects.get(cart_uuid = request.cart_uuid)

        coupon  = Coupon.objects.get(coupon_code = request.coupon_code,cart_uuid = request.cart_uuid)
        
        Valid,message = Coupon_Validator.validate(coupon=coupon,cart=cart)
        
        if not Valid:
            raise ValidationError(message=message)
        
        cart.apply_discount(discount=coupon.discount)
        logger.info(f"Applied discount to Cart:{cart.cart_uuid} from coupon {coupon.coupon_uuid}")
        return self._Cart_to_response(cart=cart)

    @handle_error
    @transaction.atomic
    def RemoveCoupon(self, request, context):
        cart = Cart.objects.get(cart_uuid = request.cart_uuid)
        cart.remove_discount()

        return self._Cart_to_response(cart)
            


class CouponService(Cart_pb2_grpc.CouponServiceServicer):
    
    
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
                response.max_cart_value = float(coupon.max_cart_value)
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
                response.order_uuid = str(coupon_usage.order_uuid)
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
    @transaction.atomic
    def CreateCoupon(self,request,context):
        coupon =  Coupon.objects.create(

            store_uuid = request.store_uuid,
            coupon_code = request.coupon_code,
            discount_type = request.discount_type,
            
            valid_from = request.valid_from,
            valid_to = request.valid_to,

            usage_limit_per_user = request.usage_limit_per_user,
            total_usage_limit = request.total_usage_limit,

            discount = request.discount,

            min_spend = request.min_spend,
            max_discount = request.max_discount,
            is_for_new_users = request.is_for_new_users,
            description = request.description,
            max_cart_value = request.max_cart_value,
            is_active = request.is_active,
        )
        logger.info(
            f"Created Coupon:{coupon.coupon_uuid} at store:{coupon.store_uuid}"
        )

        return self._Coupon_to_response(coupon=coupon)

    @transaction.atomic
    @handle_error       
    def GetCoupon(self,request,context):

        coupon = Coupon.objects.get(coupon_uuid=request.coupon_uuid,
                                    store_uuid = request.store_uuid)
        
        return self._Coupon_to_response(coupon)


    @handle_error    
    @transaction.atomic
    def UpdateCoupon(self,request,context):
        coupon = Coupon.objects.get(coupon_uuid=request.coupon_uuid, store_uuid=request.store_uuid)

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
    @transaction.atomic
    def DeleteCoupon(self,request,context):
        coupon = Coupon.objects.get(coupon_uuid=request.coupon_uuid,
                                    store_uuid = request.store_uuid)
        coupon.delete()
        logger.info(f"Coupon:{coupon.coupon_uuid} at store_uuid:{coupon.store_uuid}")        
        return self._Coupon_to_response(coupon)
        
    @handle_error
    @transaction.atomic        
    def listCoupon(self,request,context):
        coupons,next_page,prev_page = Coupon.objects.get_coupons()

        return Cart_pb2.listCouponResponse(
            coupons=[self._Coupon_to_response(coupon) for coupon in coupons],
            next_page=next_page,
            prev_page=prev_page
            )   

    @transaction.atomic
    @handle_error
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
