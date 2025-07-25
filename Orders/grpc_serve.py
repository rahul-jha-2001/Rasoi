import os
from concurrent import futures
import json

import django
from django.core.exceptions import ValidationError
from django.db import transaction
from django.core.exceptions import ValidationError,ObjectDoesNotExist,MultipleObjectsReturned,PermissionDenied
from django.db import IntegrityError,DatabaseError
from django.db import connection as conn
import psycopg2

import select

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Orders.settings')
django.setup()

from typing import Any, Callable
import grpc
from grpc import RpcError,StatusCode
from grpc_interceptor import ServerInterceptor
from grpc_interceptor.exceptions import GrpcException,Unauthenticated,FailedPrecondition
from dotenv import load_dotenv
from google.protobuf.timestamp_pb2 import Timestamp

import jwt
import time

from Proto import order_pb2,order_pb2_grpc,cart_pb2,cart_pb2_grpc

from Proto.order_pb2 import PaymentMethod,PaymentState,OrderType,OrderState
from Proto.order_pb2 import OrderState,OrderType,PaymentMethod,PaymentState
from Order.models import Order,OrderItem,OrderItemAddOn,OrderPayment,order_state,payment_method,payment_state


from utils.logger import Logger
from utils.gprc_pool import GrpcChannelPool
from utils.uuid_checker import is_valid_uuid

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET","Rahul")
CART_SERVICE_ADDR = os.getenv("CART_SERVICE_ADDR","localhost:50051")
GRPC_SERVER_PORT = os.getenv('GRPC_SERVER_PORT', '50053')
logger = Logger("GRPC_service")

def handle_error(func):
    def wrapper(self, request, context):
        try:
            return func(self, request, context)

        except Order.DoesNotExist:
            logger.warning(f"Order Not Found: Cart_uuid:{getattr(request, 'cart_uuid', '')} Store_uuid:{getattr(request, 'store_uuid', '')} user_phone_no:{getattr(request, 'user_phone_no', '')}")
            context.abort(grpc.StatusCode.NOT_FOUND, f"Cart Not Found: Cart_uuid:{getattr(request, 'cart_uuid', '')} Store_uuid:{getattr(request, 'store_uuid', '')} user_phone_no:{getattr(request, 'user_phone_no', '')}")

        except OrderItem.DoesNotExist:
            logger.warning(f"CartItem Not Found: cart_item_uuid:{getattr(request, 'cart_item_uuid', '')}")
            context.abort(grpc.StatusCode.NOT_FOUND, f"CartItem Not Found: cart_item_uuid:{getattr(request, 'cart_item_uuid', '')}")

        except OrderItemAddOn.DoesNotExist:
            logger.warning(f"Coupon Not Found: coupon_uuid: {getattr(request, 'coupon_uuid', '')} coupon_code: {getattr(request, 'coupon_code', '')}")
            context.abort(grpc.StatusCode.NOT_FOUND, f"Coupon Not Found: coupon_uuid: {getattr(request, 'coupon_uuid', '')} coupon_code: {getattr(request, 'coupon_code', '')}")

        except ObjectDoesNotExist:
            logger.warning("Requested object does not exist")
            context.abort(grpc.StatusCode.NOT_FOUND, "Requested Object Not Found")

        except MultipleObjectsReturned:
            logger.warning("Multiple objects found for request")
            context.abort(grpc.StatusCode.FAILED_PRECONDITION, "Multiple matching objects found")

        except ValidationError as e:
            logger.warning(f"Validation Error: {str(e)}")
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Validation Error: {str(e)}")

        except IntegrityError as e:
            logger.warning(f"Integrity Error: {str(e)}")
            context.abort(grpc.StatusCode.ALREADY_EXISTS, "Integrity constraint violated")

        except DatabaseError as e:
            logger.error(f"Database Error: {str(e)}")
            context.abort(grpc.StatusCode.INTERNAL, "Database Error")


        except PermissionDenied as e:
            logger.warning(f"Permission Denied: {str(e)}")
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
            raise  # Don't re-abort, just propagate the error

        except FailedPrecondition as e:
            context.abort(e.status_code,e.details)

        except Unauthenticated as e:
            context.abort(grpc.StatusCode.PERMISSION_DENIED,e.details)
            

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
            context.abort(grpc.StatusCode.INTERNAL, f"Internal Server Error")
    
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
    
class OrderService(order_pb2_grpc.OrderServiceServicer):

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
    
    def _add_on_to_response(self, add_on:OrderItemAddOn) -> order_pb2.OrderItemAddOn:

        try:   
            response = order_pb2.OrderItemAddOn()

            try:
                response.add_on_uuid = str(add_on.add_on_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert add_on_uuid: {e}")
                raise

            try:
                response.add_on_name = str(add_on.add_on_name)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert add_on_name: {e}")
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
                response.subtotal_amount = float(add_on.subtotal_amount)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert subtotal_amount: {e}")
                raise

            if not self._verify_wire_format(response, order_pb2.OrderItemAddOn, f"add_on_id:{add_on.add_on_uuid}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize AddOn:{add_on.add_on_uuid}")
            return response
        except Exception as e:
            logger.error(f"Unexpected error in _CartItem_to_response: {e}")
            raise e
            
    def _item_to_response(self, item:OrderItem) -> order_pb2.OrderItem:
        try:
            response = order_pb2.OrderItem()

            try:
                response.item_uuid = str(item.item_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert item_uuid: {e}")
                raise

            try:
                response.product_uuid = str(item.product_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert product_uuid: {e}")
                raise

            try:
                response.product_name = str(item.product_name)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert product_name: {e}")
                raise

            try:
                response.unit_price = float(item.unit_price)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert unit_price: {e}")
                raise

            try:
                response.quantity = int(item.quantity)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert quantity: {e}")
                raise

            try:
                response.discount = float(item.discount)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert discount: {e}")
                raise

            try:
                response.tax_percentage = float(item.tax_percentage)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert tax_percentage: {e}")
                raise

            try:
                response.packaging_cost = float(item.packaging_cost)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert packaging_cost: {e}")
                raise

            try:
                response.subtotal_amount = float(item.subtotal_amount)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert subtotal_amount: {e}")
                raise

            try:
                response.discount_amount = float(item.discount_amount)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert discount_amount: {e}")
                raise

            try:
                response.tax_amount = float(item.tax_amount)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert tax_amount: {e}")
                raise

            try:
                response.price_before_tax = float(item.price_before_tax)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert price_before_tax: {e}")
                raise

            try:
                response.final_price = float(item.final_price)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert final_price: {e}")
                raise

            try:
                response.add_ons.extend([self._add_on_to_response(add_on) for add_on in item.add_ons.all()])
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert add_ons: {e}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error in _item_to_response: {e}",e)
            raise e

        if not self._verify_wire_format(response, order_pb2.OrderItem, f"item_id:{item.item_uuid}"):
            raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize Item:{item.item_uuid}")
        return response
        
    def _payment_to_response(self, payment:OrderPayment) -> order_pb2.OrderPayment:
        try:

            response = order_pb2.OrderPayment()

            try:
                response.payment_uuid = str(payment.payment_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert payment_uuid: {e}")
                raise
            try:
                response.rz_order_id = str(payment.rz_order_id)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert rz_order_id: {e}")
                raise
            try:
                response.rz_payment_id = str(payment.rz_payment_id)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert rz_payment_id: {e}")
                raise
            try:
                response.rz_signature = str(payment.rz_signature)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert rz_signature: {e}")
                raise
            try:
                response.amount = float(payment.amount)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert amount: {e}")
                raise
            try:
                response.payment_status = PaymentState.Value(payment.status)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert status: {e}")
                raise e
            try:
                response.payment_method = PaymentMethod.Value(payment.method)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert method: {e}")
                raise e
            try:
                response.notes = str(payment.notes)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert notes: {e}")
                raise
            try:
                response.payment_time = payment.time
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert time: {e}")
                raise

            if not self._verify_wire_format(response, order_pb2.OrderPayment, f"payment_id:{payment.payment_uuid}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize Payment:{payment.payment_uuid}")
            return response
        except Exception as e:
            logger.error(f"Unexpected error in _payment_to_response: {e}",e)
            raise e         

    def _user_order_to_response(self, order:Order) -> order_pb2.OrderUserView:
        try:    
            response = order_pb2.OrderUserView()
            
            try:
                response.cart_uuid = str(order.cart_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.error(f"Order UUID conversion error: {str(e)}")
                raise

            try:
                response.order_uuid = str(order.order_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.error(f"Order UUID conversion error: {str(e)}")
                raise

            try:
                response.order_no = str(order.order_no)
            except (AttributeError, TypeError, ValueError) as e:
                logger.error(f"Order number conversion error: {str(e)}")
                raise

            try:
                response.store_uuid = str(order.store_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.error(f"Store UUID conversion error: {str(e)}")
                raise

            try:
                response.user_phone_no = str(order.user_phone_no)
            except (AttributeError, TypeError, ValueError) as e:
                logger.error(f"User phone number conversion error: {str(e)}")
                raise

            try:
                response.order_type = OrderType.Value(order.order_type)
            except (ValueError, AttributeError) as e:
                logger.error(f"Order type conversion error: {str(e)}")
                raise

            try:
                if order.table_no:
                    response.table_no = str(order.table_no)
            except (AttributeError, TypeError, ValueError) as e:
                logger.error(f"Table number conversion error: {str(e)}")
                raise

            try:
                if order.vehicle_no:
                    response.vehicle_no = str(order.vehicle_no)
            except (AttributeError, TypeError, ValueError) as e:
                logger.error(f"Vehicle number conversion error: {str(e)}")
                raise

            try:
                if order.vehicle_description:
                    response.vehicle_description = str(order.vehicle_description)
            except (AttributeError, TypeError, ValueError) as e:
                logger.error(f"Vehicle description conversion error: {str(e)}")
                raise

            try:
                if order.coupon_code:
                    response.coupon_code = str(order.coupon_code)
            except (AttributeError, TypeError, ValueError) as e:
                logger.error(f"Coupon code conversion error: {str(e)}")
                raise

            try:
                items = []
                for item in order.items.all():
                    try:
                        items.append(self._item_to_response(item))
                    except Exception as e:
                        logger.error(f"Error converting item {item.order_item_addOn_uuid}: {str(e)}")
                        raise
                response.items.extend(items)
            except (AttributeError, TypeError) as e:
                logger.error(f"Items conversion error: {str(e)}")
                raise

            try:
                if order.special_instructions:
                    response.special_instructions = str(order.special_instructions)
            except (AttributeError, TypeError, ValueError) as e:
                logger.error(f"Special instructions conversion error: {str(e)}")
                raise

            try:
                response.order_status = OrderState.Value(order.order_status)
            except (ValueError, AttributeError) as e:
                logger.error(f"Order status conversion error: {str(e)}")
                raise

            try:
                if order.payment:
                    payment:OrderPayment = order.payment
                    response.payment_method = PaymentMethod.Value(payment.method)
                    response.payment_state = PaymentState.Value(payment.status)
            except (AttributeError, IndexError) as e:
                logger.error(f"Payment conversion error: {str(e)}")
                raise

            try:
                response.total_subtotal = float(order.subtotal_amount)
                response.total_discount = float(order.discount_amount)
                response.total_price_before_tax = float(order.price_before_tax)
                response.total_tax = float(order.tax_amount)
                response.packaging_cost = float(order.packaging_cost)
                response.final_amount = float(order.final_amount)
            except (TypeError, ValueError, AttributeError) as e:
                logger.error(f"Financial field conversion error: {str(e)}")
                raise

            def convert_time(field_name, dt):
                try:
                    ts = Timestamp()
                    ts.FromDatetime(dt)
                    return ts
                except Exception as e:
                    logger.error(f"{field_name} conversion error: {str(e)}")
                    raise

            try:
                if order.created_at:
                    response.created_at = order.created_at
            except Exception as e:
                logger.error(f"Created at time conversion error: {str(e)}")
                raise

            try:
                if order.updated_at:
                    response.updated_at = order.updated_at
            except Exception as e:
                logger.error(f"Updated at time conversion error: {str(e)}",e)
                raise
            
            if not self._verify_wire_format(response, order_pb2.OrderUserView, f"order_id:{order.order_uuid}"): 
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize Order:{order.order_uuid}")
            
            return response
        
        except Exception as e:
            logger.error(f"Unexpected error in _store_order_to_response: {e}",e)        
            raise e
    
    def _store_order_to_response(self, order:Order) -> order_pb2.OrderStoreView:
        try:    
            response = order_pb2.OrderStoreView()
            
            try:
                response.cart_uuid = str(order.cart_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.error(f"Order UUID conversion error: {str(e)}")
                raise

            try:
                response.order_uuid = str(order.order_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.error(f"Order UUID conversion error: {str(e)}")
                raise

            try:
                response.order_no = str(order.order_no)
            except (AttributeError, TypeError, ValueError) as e:
                logger.error(f"Order number conversion error: {str(e)}")
                raise

            try:
                response.store_uuid = str(order.store_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.error(f"Store UUID conversion error: {str(e)}")
                raise

            try:
                response.user_phone_no = str(order.user_phone_no)
            except (AttributeError, TypeError, ValueError) as e:
                logger.error(f"User phone number conversion error: {str(e)}")
                raise

            try:
                response.order_type = OrderType.Value(order.order_type)
            except (ValueError, AttributeError) as e:
                logger.error(f"Order type conversion error: {str(e)}")
                raise

            try:
                if order.table_no:
                    response.table_no = str(order.table_no)
            except (AttributeError, TypeError, ValueError) as e:
                logger.error(f"Table number conversion error: {str(e)}")
                raise

            try:
                if order.vehicle_no:
                    response.vehicle_no = str(order.vehicle_no)
            except (AttributeError, TypeError, ValueError) as e:
                logger.error(f"Vehicle number conversion error: {str(e)}")
                raise

            try:
                if order.vehicle_description:
                    response.vehicle_description = str(order.vehicle_description)
            except (AttributeError, TypeError, ValueError) as e:
                logger.error(f"Vehicle description conversion error: {str(e)}")
                raise

            try:
                if order.coupon_code:
                    response.coupon_code = str(order.coupon_code)
            except (AttributeError, TypeError, ValueError) as e:
                logger.error(f"Coupon code conversion error: {str(e)}")
                raise

            try:
                items = []
                for item in order.items.all():
                    try:
                        items.append(self._item_to_response(item))
                    except Exception as e:
                        logger.error(f"Error converting item {item.order_item_addOn_uuid}: {str(e)}")
                        raise
                response.items.extend(items)
            except (AttributeError, TypeError) as e:
                logger.error(f"Items conversion error: {str(e)}")
                raise

            try:
                if order.special_instructions:
                    response.special_instructions = str(order.special_instructions)
            except (AttributeError, TypeError, ValueError) as e:
                logger.error(f"Special instructions conversion error: {str(e)}")
                raise

            try:
                response.order_status = OrderState.Value(order.order_status)
            except (ValueError, AttributeError) as e:
                logger.error(f"Order status conversion error: {str(e)}")
                raise

            try:
                if order.payment:
                    payment = order.payment
                    response.payment.CopyFrom(self._payment_to_response(payment))
            except (AttributeError, IndexError) as e:
                logger.error(f"Payment conversion error: {str(e)}")
                raise

            try:
                response.subtotal_amount = float(order.subtotal_amount)
                response.discount_amount = float(order.discount_amount)
                response.price_before_tax = float(order.price_before_tax)
                response.tax_amount = float(order.tax_amount)
                response.packaging_cost = float(order.packaging_cost)
                response.final_amount = float(order.final_amount)
            except (TypeError, ValueError, AttributeError) as e:
                logger.error(f"Financial field conversion error: {str(e)}")
                raise

            def convert_time(field_name, dt):
                try:
                    ts = Timestamp()
                    ts.FromDatetime(dt)
                    return ts
                except Exception as e:
                    logger.error(f"{field_name} conversion error: {str(e)}")
                    raise

            try:
                if order.created_at:
                    response.created_at = order.created_at
            except Exception as e:
                logger.error(f"Created at time conversion error: {str(e)}")
                raise

            try:
                if order.updated_at:
                    response.updated_at = order.updated_at
            except Exception as e:
                logger.error(f"Updated at time conversion error: {str(e)}",e)
                raise
            
            if not self._verify_wire_format(response, order_pb2.OrderStoreView, f"order_id:{order.order_uuid}"): 
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize Order:{order.order_uuid}")
            
            return response
        
        except Exception as e:
            logger.error(f"Unexpected error in _store_order_to_response: {e}",e)        
            raise e

    def __init__(self):
        
        self.channel_pool = GrpcChannelPool()
        self.channel = self.channel_pool.get_channel(CART_SERVICE_ADDR)
        self.Cart_stub = cart_pb2_grpc.CartServiceStub(self.channel)
        logger.info(f"Initialized gRPC channel to Cart Service at {CART_SERVICE_ADDR}")
        self.meta_data =[ 
            ("role","internal"),
            ("service","order")
        ]
        super().__init__()
    
    @handle_error
    @check_access(roles=["store","internal"])
    def CreateOrder(self, request, context):
        cart_uuid = request.cart_uuid
        store_uuid = request.store_uuid
        
        if not is_valid_uuid(store_uuid):
            raise ValidationError(f"store_uud:{store_uuid} is not Valid Uuid")
        if not is_valid_uuid(cart_uuid):
            raise ValidationError(f"cart_uuid:{cart_uuid} is not Valid Uuid")

        try:
            order = Order.objects.get(cart_uuid = cart_uuid,store_uuid = store_uuid)
            return order_pb2.StoreOrderResponse(
            order = self._store_order_to_response(order))
        except Order.DoesNotExist:
            pass

        cart_request = cart_pb2.GetCartRequest(cart_uuid=cart_uuid,store_uuid = store_uuid)
        
        try:
            response = self.Cart_stub.GetCart(cart_request,metadata = self.meta_data)
        except RpcError as e:

            error_message = e.details()
            if e.code() == StatusCode.NOT_FOUND:
                logger.error(f"Active Cart: {cart_uuid} not found")
                raise GrpcException(error_message,status_code=e.code())
            elif e.code() == StatusCode.INVALID_ARGUMENT:
                logger.error(error_message)
                raise GrpcException(error_message,status_code=e.code())
            elif e.code() == StatusCode.INTERNAL:
                logger.error(error_message)
                raise GrpcException(error_message,status_code=e.code())
            elif e.code() == StatusCode.UNAVAILABLE:
                logger.error(f"Cart Service does not exist at:{CART_SERVICE_ADDR}")
                raise GrpcException("Internal Server Error",status_code=StatusCode.UNAVAILABLE)
        
        with transaction.atomic():# Extract cart details
            cart = response.cart
            order = Order.objects.create(
                store_uuid = cart.store_uuid,
                cart_uuid = cart.cart_uuid,
                user_phone_no = cart.user_phone_no,
                order_type =  OrderType.Name(cart.order_type),
                table_no=cart.table_no,
                vehicle_no=cart.vehicle_no,
                vehicle_description=cart.vehicle_description,
                coupon_code=cart.coupon_code,
                special_instructions=cart.special_instructions,
                order_status=order_state.ORDER_STATE_PLACED,
                subtotal_amount=cart.sub_total,
                discount_amount=cart.total_discount,
                price_before_tax=cart.total_price_before_tax,
                tax_amount=cart.total_tax,
                packaging_cost=cart.packaging_cost,
                final_amount=cart.final_amount
            )

            # Process order items
            order_items = []
            order_add_ons = []
            for i in cart.items:
                item = OrderItem(
                    order=order,
                    product_name=i.product_name,
                    product_uuid=i.product_uuid,
                    unit_price=i.unit_price,
                    discount=i.discount,
                    quantity = i.quantity,
                    add_ons_total = i.add_ons_total,
                    tax_percentage=i.tax_percentage,
                    packaging_cost=i.packaging_cost,
                    subtotal_amount=i.subtotal_amount,
                    discount_amount=i.discount_amount,
                    price_before_tax=i.price_before_tax,
                    tax_amount=i.tax_amount,
                    final_price=i.final_price
                )
                order_items.append(item)

            # Bulk insert items
            created_items = OrderItem.objects.bulk_create(order_items)

            # Process add-ons after item creation
            for item, i in zip(created_items, cart.items):
                for j in i.add_ons:
                    add_on = OrderItemAddOn(
                        order_item=item,
                        add_on_name=j.add_on_name,
                        add_on_uuid=j.add_on_uuid,
                        quantity=j.quantity,
                        unit_price=j.unit_price,
                        is_free=j.is_free,
                        subtotal_amount=j.subtotal_amount
                    )
                    order_add_ons.append(add_on)

            # Bulk insert add-ons
            if order_add_ons:
                OrderItemAddOn.objects.bulk_create(order_add_ons)

            # Create payment record (outside item loop)
            payment = OrderPayment.objects.create(
                order=order,
                amount=order.final_amount,
                method=PaymentMethod.Name(PaymentMethod.PAYMENT_METHOD_CASH),
                status=PaymentState.Name(PaymentState.PAYMENT_STATE_COMPLETE),
            )
            return order_pb2.StoreOrderResponse(
            order = self._store_order_to_response(order)
        )

    @handle_error
    @check_access(roles=["store","internal"])
    def GetOrder(self,request,context):
        
        store_uuid = request.store_uuid

        if not is_valid_uuid(store_uuid):
            raise ValidationError(f"store_uud:{store_uuid} is not Valid Uuid")
        
        if request.order_uuid:
            if not is_valid_uuid(request.order_uuid):
                raise ValidationError(f"order_uud:{request.order_uuid} is not Valid Uuid")
            
            order = Order.objects.get(order_uuid = request.order_uuid,store_uuid = store_uuid)
        elif request.store_uuid and request.user_phone_no:
            order = Order.objects.get(user_phone_no = request.user_phone_no,store_uuid = store_uuid)
        elif request.order_no:
            order = Order.objects.get(order_no = request.order_no,store_uuid = store_uuid)
        elif request.cart_uuid:
            if not is_valid_uuid(request.cart_uuid):
                raise ValidationError(f"cart_uuid:{request.cart_uuid} is not Valid Uuid")
            order = Order.objects.get(cart_uuid = request.cart_uuid,store_uuid = store_uuid)
        else:
            raise ValueError(f"No value given to fetch order")

        return order_pb2.StoreOrderResponse(
            order = self._store_order_to_response(order = order)
        )
    
    
    @handle_error
    @check_access(roles=["store","internal"])
    def CancelOrder(self,request,context):

        store_uuid = request.store_uuid
        if not is_valid_uuid(store_uuid):
                raise ValidationError(f"store_uuid:{store_uuid} is not Valid Uuid")
        # Fetch order
        order = None
        if is_valid_uuid(request.order_uuid):
            order = Order.objects.prefetch_related("payment").get(order_uuid=request.order_uuid, store_uuid=store_uuid)
        elif request.order_no:
            order = Order.objects.prefetch_related("payment").get(order_no=request.order_no, store_uuid=store_uuid)
        else:
            raise ValueError("No value given to fetch order")

        # Check if order is in a state that allows cancellation
        if order.order_status in {order_state.ORDER_STATE_READY, order_state.ORDER_STATE_COMPLETED,order_state.ORDER_STATE_CANCELED}:
            raise FailedPrecondition("Order cannot be canceled in current state",StatusCode.FAILED_PRECONDITION)

        # Validate payment existence
        if not hasattr(order, "payment"):
            raise Exception("Internal Error Payment Object could not be found")

        with transaction.atomic():
            # Process refund
            order.payment.update_status(payment_state.PAYMENT_STATE_REFUNDED)
            # Update order status
            order.order_status = order_state.ORDER_STATE_CANCELED
            order.save()

            logger.info(f"Order:{order.order_uuid} Order-No:{order.order_no} is Cancelled")

            return order_pb2.StoreOrderResponse(order=self._store_order_to_response(order))


    @handle_error
    @check_access(roles=["store","internal"])
    def UpdateOrderState(self,request,context):
        store_uuid = request.store_uuid
        order_uuid = request.order_uuid

        if not is_valid_uuid(store_uuid):
                raise ValidationError(f"store_uuid:{store_uuid} is not Valid Uuid")
        if not is_valid_uuid(order_uuid):
                raise ValidationError(f"order_uuid:{order_uuid} is not Valid Uuid")        
        
        order = Order.objects.get(order_uuid = order_uuid , store_uuid = store_uuid)

        with transaction.atomic():
            # Process refund
            order.order_status = OrderState.Name(request.order_state)
            order.save()
            logger.info(f"Order:{order.order_uuid} Order-No:{order.order_no} status changed to {order.order_status}")

            return order_pb2.StoreOrderResponse(order=self._store_order_to_response(order))


    @handle_error
    @check_access(roles=["store","internal"])
    def ListOrder(self,request,context):

        store_uuid = request.store_uuid
        if not is_valid_uuid(store_uuid):
                raise ValidationError(f"store_uuid:{store_uuid} is not Valid Uuid")


        
        limit = request.limit
        page = request.page

        orders,next_page,prev_page = Order.objects.get_store_orders(store_uuid=store_uuid,limit=limit,page=page)


        return order_pb2.ListOrderResponse(
            orders = [self._store_order_to_response(order) for order in orders],
            next_page = next_page,
            prev_page = prev_page) 

    @handle_error
    @check_access(roles=["store","internal"])
    def StreamOrders(self,request,context):

        store_uuid = request.store_uuid
        
        if not is_valid_uuid(store_uuid):
                raise ValidationError(f"store_uuid:{store_uuid} is not Valid Uuid")

        last_order_time = None  # Keep track of the last streamed order time
        channel_name = f"order_updates_{store_uuid}".replace("-","_")
        
        logger.info(f"Started Stream for store:{store_uuid} at {time.time()}")

        try:
            with conn.cursor() as cursor:
                cursor.execute(f'LISTEN {channel_name}')
                logger.info(f"Started listening to channel {channel_name}")
                HEALTH_CHECK_INTERVAL = 100
                health_check_counter = 0
                while context.is_active():
                    # Check for new notifications
                    if select.select([conn.connection], [], [], 0.1) == ([], [], []):
                        # No notifications available
                        time.sleep(0.1)
                        continue
                    
                    # Process notifications
                    conn.connection.poll()
                    while conn.connection.notifies:
                        notification = conn.connection.notifies.pop(0)
                        try:
                            payload = json.loads(notification.payload)
                            order = Order.objects.get(
                                order_uuid=payload['order_uuid'],
                                store_uuid=store_uuid
                            )
                            last_order_time = time.time()
                            logger.info(f"Order:{order.order_uuid} Streamed for store_uuid:{order.store_uuid} at {last_order_time} ")
                            yield order_pb2.StoreOrderResponse(
                                order=self._store_order_to_response(order)
                            )
                        except Order.DoesNotExist:
                            logger.warning(f"Order {payload.get('order_uuid')} not found")
                        except json.JSONDecodeError:
                            logger.error(f"Invalid payload: {notification.payload}")
                        except KeyError as e:
                            logger.error(f"Missing key in payload: {e}")
                    
                    # Add small sleep to prevent busy waiting
                    health_check_counter += 1
                    if health_check_counter >= HEALTH_CHECK_INTERVAL:
                        health_check_counter = 0
                        try:
                            # Simple query to verify connection is alive
                            with conn.cursor() as ping_cursor:
                                ping_cursor.execute("SELECT 1")
                        except Exception as e:
                            logger.error(f"Connection health check failed: {str(e)}")
                            break 
                    time.sleep(0.25)
                    
        except psycopg2.OperationalError as e:
            logger.error(f"Database connection error: {str(e)}")
        except Exception as e:
            logger.error("Unexpected error in order stream ",e)
        finally:
            # Cleanup
            try:
                with conn.cursor() as cursor:
                    cursor.execute(f'UNLISTEN "{channel_name}";')
            except:
                pass
            logger.info(f"Stopped listening to channel {channel_name}")

    @handle_error
    @check_access(roles=["user","internal"])

    def GetUserOrder(self,request,context):

        if not is_valid_uuid(request.order_uuid):
                raise ValidationError(f"order_uuid:{request.order_uuid} is not Valid Uuid")
        user_phone_no = request.user_phone_no

        if request.order_uuid:
            order = Order.objects.get(user_phone_no = user_phone_no,order_uuid = request.order_uuid)
        elif request.order_no:
            order = Order.objects.get(user_phone_no = user_phone_no,order_no = request.order_no)
        else:
            raise ValueError(f"No value given to fetech order")
        
        return order_pb2.UserOrderResponse(
            order = self._user_order_to_response(order = order)
        )

    @handle_error
    @check_access(roles=["user","internal"])
    def listUserOrder(self,request,context):
        user_phone_no = request.user_phone_no

        store_uuid = request.store_uuid
        limit = request.limit
        page = request.page

        orders,next_page,prev_page = Order.objects.get_user_orders(store_uuid=store_uuid,user_phone_no=user_phone_no,limit=limit,page=page)

        return order_pb2.ListUserOrderResponse(
            orders = [self._user_order_to_response(order) for order in orders],
            next_page = next_page,
            prev_page = prev_page)

   
    @handle_error
    @check_access(roles=["user","internal"])
    def CancelUserOrder(self,request,context):
        
        user_phone_no = request.user_phone_no

        if request.order_uuid:
            order = Order.objects.get(user_phone_no = user_phone_no,order_uuid = request.order_uuid)
        elif request.order_no:
            order = Order.objects.get(user_phone_no = user_phone_no,order_no = request.order_no)
        else:
            logger.warning(f"Order_uuid and Order_NO missing")
            context.abort(StatusCode.INVALID_ARGUMENT,f"Order_uuid and Order_NO missing")
        
        if order.order_status in [order_state.ORDER_STATE_READY,order_state.ORDER_STATE_COMPLETED]:

            raise FailedPrecondition(f"Order already completed or being prepared")

        if order.order_status in [order_state.ORDER_STATE_CANCELED]:
            raise FailedPrecondition(f"Order already canceled")

        if order.payment.method == payment_method.PAYMENT_METHOD_CASH:
            raise FailedPrecondition("Order cannot be cancelled ,Checkout the counter",StatusCode.FAILED_PRECONDITION)

        if order.payment.status == payment_state.PAYMENT_STATE_REFUNDED:
            raise FailedPrecondition("Order has been refunded",StatusCode.FAILED_PRECONDITION)
        with transaction.atomic():
            # Process refund
            order.payment.update_status(payment_state.PAYMENT_STATE_REFUNDED)
            # Update order status
            order.order_status = order_state.ORDER_STATE_CANCELED
            order.save()

            logger.info(f"Order:{order.order_uuid} Order-No:{order.order_no} is Cancelled")

            return order_pb2.UserOrderResponse(order=self._user_order_to_response(order))


def serve():
    
    server = grpc.server(
    futures.ThreadPoolExecutor(max_workers=10)
)

    order_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(),server)

    

    server.add_insecure_port(f"[::]:{GRPC_SERVER_PORT}")
    server.start()
    logger.info(f"Server Stated at {GRPC_SERVER_PORT}")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Stopping gRPC Server...")
        server.stop(0)


if __name__ == "__main__":
        
        """Starts the gRPC server."""
        try:
            logger.info("Starting gRPC server...")
            serve()
        except Exception as e:
            logger.error(f"Error in gRPC server: {e}")
