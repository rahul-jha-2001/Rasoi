
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
from api.models import Cart,CartItem,AddOn,Coupon,CouponUsage,Coupon_Validator,ServiceSession,Table
from Proto import cart_pb2_grpc as Cart_pb2_grpc
from Proto import cart_pb2 as Cart_pb2
from Proto.cart_pb2 import (
    ORDERTYPE,
    DISCOUNTTYPE,
    CARTSTATE,
    SERVICESESSIONSTATUS,
    PAYMENTTYPE,
)
from Proto import product_pb2_grpc,product_pb2
from Proto.product_pb2 import GetProductRequest,AddOnResponse
from google.protobuf import empty_pb2

from utils.logger import Logger
from utils.gprc_pool import GrpcChannelPool
from utils.check_access import check_access
load_dotenv()

logger = Logger("GRPC_service")
PRODUCT_SERVICE_ADDR = os.getenv("PRODUCT_SERVICE_ADDR","localhost:50052")

class CartVaildator:

    # def __init__(self):
    #     # Connect to the product and store gRPC services
    #     self.product_channel = grpc.insecure_channel('product-service:50051')
    #     # self.store_channel = grpc.insecure_channel('store-service:50052')

    #     self.product_stub = product_pb2_grpc.ProductServiceStub(self.product_channel)
    #     # self.store_stub = store_pb2_grpc.StoreServiceStub(self.store_channel)
    @staticmethod
    def validate_cart(cart: Cart, coupon: Coupon | None):
        errors = []
        total_price = 0
        flag = True  # assume valid unless proven otherwise

        # Check coupon validity
        if coupon is not None:
            flag, msg = Coupon_Validator.validate(coupon=coupon, cart=cart)
            if not flag:
                return {"valid": False, "message": msg}

        # Check for postpaid table with valid session
        if cart.service_session and cart.table:
            if cart.table.payment_type == PAYMENTTYPE.PAYMENT_TYPE_POSTPAID:

                # Ensure cart is active or locked
                if cart.state not in [Cart.cart_state.CART_STATE_ACTIVE, Cart.cart_state.CART_STATE_LOCKED]:
                    return {"valid": False, "message": "Postpaid cart must be in active or locked state"}

                # Ensure phone number exists
                if not cart.user_phone_no:
                    return {"valid": False, "message": "Phone number is required for postpaid orders"}

                # Ensure session is still ongoing
                if cart.service_session.service_status != ServiceSession.ServiceStatus.SERVICE_SESSION_ONGOING:
                    return {
                        "valid": False,
                        "message": f"Service session is not ongoing (current: {cart.service_session.service_status})"
                    }

        return {"valid": flag, "message": "Cart is valid"}
    

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
            logger.error(f"Type Error: {str(e)}",e)
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"Type Error: {str(e)}")

        except TimeoutError as e:
            logger.error(f"Timeout Error: {str(e)}")
            context.abort(grpc.StatusCode.DEADLINE_EXCEEDED, "Request timed out")
            
        except grpc.RpcError as e:
            raise  # Don't re-abort, just propagate the error

        except FailedPrecondition as e:
            context.abort(e.status_code,e.details)

        except Unauthenticated as e:
            context.abort(grpc.StatusCode.PERMISSION_DENIED,f"User Not Allowed To make this Call")
        
        except GrpcException as e:
            context.abort(e.status_code,e.details)
            raise Exception("Forced RollBack due to GrpcException")
            
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
                response.order_type = ORDERTYPE.Value(cart.order_type)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert order_type: {e}")
                raise

            try:
                response.table_no = str(cart.table.table_number) or ""
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert table_number: {e}")
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

            # --- NEW: table_uuid and service_session_uuid ---
            try:
                response.table_uuid = str(cart.table.table_uuid) if cart.table else ""
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert table_uuid: {e}")
                raise

            try:
                response.service_session_uuid = str(cart.service_session.service_session_uuid) if cart.service_session else ""
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert service_session_uuid: {e}")
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

    def _Table_to_response(self, table: Table) -> Cart_pb2.Table:
        """Convert Django Table instance to protobuf Table message."""
        try:
            response = Cart_pb2.Table()

            try:
                response.table_uuid = str(table.table_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert table_uuid: {e}")
                raise

            try:
                response.store_uuid = str(table.store_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert store_uuid: {e}")
                raise

            try:
                response.table_number = table.table_number or ""
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert table_number: {e}")
                raise

            try:
                response.area_name = table.area_name or ""
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert area_name: {e}")
                raise

            try:
                response.payment_type = PAYMENTTYPE.Value(table.payment_type)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert payment_type: {e}")
                raise

            try:
                response.no_of_sitting = table.no_of_sitting
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert no_of_sitting: {e}")
                raise

            try:
                response.is_active = table.is_active
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert is_active: {e}")
                raise

            # # created_at timestamp
            # try:
            #     if table.created_at:
            #         response.created_at.FromDatetime(table.created_at)
            # except Exception as e:
            #     logger.warning(f"Failed to convert created_at: {e}")
            #     raise

            if not self._verify_wire_format(response, Cart_pb2.Table, f"Table_uuid={table.table_uuid}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize Table {table.table_uuid}")
            logger.info(f"{response}")


            return response
        except Exception as e:
            logger.error(f"Unexpected error in _Table_to_response: {e}")
            raise

    def _ServiceSession_to_response(self, session:ServiceSession) -> Cart_pb2.ServiceSession:
        """Convert Django ServiceSession instance to protobuf ServiceSession message."""
        try:
            response = Cart_pb2.ServiceSession()

            try:
                response.service_session_uuid = str(session.service_session_uuid)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert service_session_uuid: {e}")
                raise

            # nested table
            try:
                response.table_uuid =  str(session.table.table_uuid)
            except Exception as e:
                logger.warning(f"Failed to convert table uuid: {e}")
                raise

            # timestamps
            try:
                if session.started_at:
                    ts = Timestamp()
                    ts.FromDatetime(session.started_at)
                    response.started_at.CopyFrom(ts)
                if session.ended_at:
                    ts2 = Timestamp()
                    ts2.FromDatetime(session.ended_at)
                    response.ended_at.CopyFrom(ts2)
            except Exception as e:
                logger.warning(f"Failed to convert timestamps: {e}")
                raise

            try:
                response.service_status = SERVICESESSIONSTATUS.Value(session.service_status)
            except (AttributeError, TypeError, ValueError) as e:
                logger.warning(f"Failed to convert service_status: {e}")
                raise
            
            if not self._verify_wire_format(response, ServiceSession, f"Session_uuid={session.service_session_uuid}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize Session {session.service_session_uuid}")
            logger.info(f"{response}")

            return response
        except Exception as e:
            logger.error(f"Unexpected error in _ServiceSession_to_response: {e}")
            raise

    def __init__(self):
        try:
            self.channel_pool = GrpcChannelPool()
            self.channel = self.channel_pool.get_channel(PRODUCT_SERVICE_ADDR)
            if not self.channel:
                logger.error(f"Failed to create channel to Product Service at {PRODUCT_SERVICE_ADDR}")
                raise ConnectionError(f"Failed to connect to Product Service at {PRODUCT_SERVICE_ADDR}")
            
            self.Product_stub = product_pb2_grpc.ProductServiceStub(self.channel)
            logger.info(f"Initialized gRPC channel to Product Service at {PRODUCT_SERVICE_ADDR}")
            self.meta_data = [
                ("role", "internal"),
                ("service", "product")
            ]
            super().__init__()
        except Exception as e:
            logger.error(f"Failed to initialize CartService: {str(e)}")
            raise


    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def CreateTable(self, request, context):
        logger.debug(f"CreateTable request received: {request}")
        with transaction.atomic():
            table = Table.objects.create(
                store_uuid=request.store_uuid,
                table_number=request.table_number,
                area_name=request.area_name,
                payment_type=PAYMENTTYPE.Name(request.payment_type),
                no_of_sitting=request.no_of_sitting,
            )
            logger.info(f"Created Table {table.table_uuid} in store {table.store_uuid} with table_number {table.table_number}, area_name {table.area_name}, payment_type {table.payment_type}, and no_of_sitting {table.no_of_sitting}")
            return self._Table_to_response(table)

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def GetTable(self, request, context):
        logger.debug(f"GetTable request received: {request}")
        table = Table.objects.get_table(
            table_uuid=request.table_uuid
        )
        logger.info(f"Fetched Table {table.table_uuid} in store {table.store_uuid} with table_number {table.table_number}, area_name {table.area_name}, payment_type {table.payment_type}, and no_of_sitting {table.no_of_sitting}")
        return self._Table_to_response(table)

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def ListTables(self, request, context):
        logger.debug(f"ListTables request received for store_uuid: {request.store_uuid}")
        tables = Table.objects.filter_by_store(request.store_uuid)
        logger.info(f"Found {len(tables)} tables for store_uuid: {request.store_uuid}")
        response = Cart_pb2.ListTablesResponse()
        for t in tables:
            logger.debug(f"Adding Table {t.table_uuid} to response")
            response.tables.append(self._Table_to_response(t))
        return response

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def UpdateTable(self, request, context):
        logger.debug(f"UpdateTable request received: {request}")
        with transaction.atomic():
            table = Table.objects.get(table_uuid=request.table_uuid)
            logger.info(f"Updating Table {table.table_uuid} in store {table.store_uuid}")
            if request.area_name:
                logger.debug(f"Updating area_name to {request.area_name}")
                table.area_name = request.area_name
            if request.HasField('payment_type'):
                logger.debug(f"Updating payment_type to {Cart_pb2.PAYMENTTYPE.Name(request.payment_type)}")
                table.payment_type = Cart_pb2.PAYMENTTYPE.Name(request.payment_type)
            if request.HasField('no_of_sitting'):
                logger.debug(f"Updating no_of_sitting to {request.no_of_sitting}")
                table.no_of_sitting = request.no_of_sitting
            if request.HasField('is_active'):
                logger.debug(f"Updating is_active to {request.is_active}")
                table.is_active = request.is_active
            table.save()
            logger.info(f"Updated Table {table.table_uuid} with new values: area_name={table.area_name}, payment_type={table.payment_type}, no_of_sitting={table.no_of_sitting}, is_active={table.is_active}")
            return self._Table_to_response(table)

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def DeleteTable(self, request, context):
        with transaction.atomic():
            table = Table.objects.get(table_uuid=request.table_uuid)
            table.delete()
            logger.info(f"Deleted Table {request.table_uuid}")
            return empty_pb2.Empty()


    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def CreateServiceSession(self, request, context):
        with transaction.atomic():
            try:
                session = ServiceSession.objects.get_active_session(
                    table_uuid=request.table_uuid
                )
                logger.info(f"Fetched active Session {session.service_session_uuid}")
            except ServiceSession.DoesNotExist:
                table = Table.objects.get(table_uuid=request.table_uuid)
                session = ServiceSession.objects.create(
                    table=table
                )
                logger.info(f"Created Session {session.service_session_uuid} for Table {table.table_uuid}")
            return self._ServiceSession_to_response(session)

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def GetServiceSession(self, request, context):
        session = ServiceSession.objects.get_session(
            session_uuid=request.service_session_uuid
        )
        logger.info(f"Fetched Session {session.service_session_uuid}")
        return self._ServiceSession_to_response(session)
    

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def GetActiveSession(self, request, context):
        session = ServiceSession.objects.get_active_session(
            request.table_uuid )
        logger.info(f"Fetched Session {session.service_session_uuid}")
        return self._ServiceSession_to_response(session)
    
    @handle_error
    @check_access(
        expected_types=["store"],
        allowed_roles={"store": ["admin", "staff"]}, require_resource_match=True)
    def ListServiceSessions(self, request, context):
        # Filter sessions based on request parameters
        filters = {"store_uuid": request.store_uuid}
        if request.HasField("table_uuid"):
            filters["table__table_uuid"] = request.table_uuid
        if request.HasField("service_session_status"):
            filters["service_status"] = SERVICESESSIONSTATUS.Name(request.service_session_status)
        if request.HasField("from"):
            filters["created_at__gte"] = request.from_time.ToDatetime()

        # Fetch paginated sessions using the new paginated_list method
        sessions, next_page, prev_page = ServiceSession.objects.paginated_list(
            filters=filters,
            limit=request.limit or 10,
            page=request.page or 1
        )

        # Build response
        response = Cart_pb2.ListServiceSessionsResponse(
            sessions=[self._ServiceSession_to_response(s) for s in sessions],
            next_page=next_page,
            prev_page=prev_page
        )
        return response

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def UpdateServiceSession(self, request, context):
        with transaction.atomic():
            session = ServiceSession.objects.get_session(
                session_uuid=request.service_session_uuid
            )
            if request.HasField('service_status'):
                session.service_status = Cart_pb2.ServiceSession.Status.Name(request.service_status)
            if request.HasField('ended_at'):
                session.ended_at = request.ended_at.ToDatetime()
            session.save()
            logger.info(f"Updated Session {session.service_session_uuid}")
            return self._ServiceSession_to_response(session)

    @handle_error
    @check_access(
        expected_types=["store"],
        allowed_roles={"store": ["admin", "staff"]},
        require_resource_match=True
    )
    def ValidateServiceSession(self, request, context):
        logger.info(f"Validating service session: {request.service_session_uuid} for store: {request.store_uuid}")

        try:
            # Fetch the service session
            service_session = ServiceSession.objects.filter(
                service_session_uuid=request.service_session_uuid,
                store_uuid=request.store_uuid
            ).first()

            if not service_session:
                logger.warning("Service session not found")
                return Cart_pb2.ValidateSessionResponse(
                    valid=False,
                    message="Service session not found",
                    cart_uuids=[]
                )

            # Check if session is ongoing
            if service_session.service_status != ServiceSession.ServiceStatus.SERVICE_SESSION_ONGOING:
                logger.warning(f"Invalid session status: {service_session.service_status}")
                return Cart_pb2.ValidateSessionResponse(
                    valid=False,
                    message="Service session is not ongoing",
                    cart_uuids=[]
                )

            # Fetch locked carts associated with the session
            locked_carts = Cart.objects.filter(
                service_session=service_session,
                state=Cart.cart_state.CART_STATE_LOCKED
            )

            if not locked_carts.exists():
                logger.warning("No locked carts found for session")
                return Cart_pb2.ValidateSessionResponse(
                    valid=False,
                    message="No locked carts found for this session",
                    cart_uuids=[]
                )

            # Extract UUIDs
            cart_uuids = [str(cart.cart_uuid) for cart in locked_carts]

            # Mark session as ended
            service_session.service_status = ServiceSession.ServiceStatus.SERVICE_SESSION_ENDED
            service_session.ended_at = datetime.now()
            service_session.save()

            logger.info(f"Service session {service_session.service_session_uuid} validated and ended. {len(cart_uuids)} carts locked.")

            return Cart_pb2.ValidateSessionResponse(
                valid=True,
                message=f"Session validated. {len(cart_uuids)} carts ready for billing.",
                cart_uuids=cart_uuids
            )

        except Exception as e:
            logger.error(f"Error validating session: {e}")
            raise



    @handle_error
    @check_access(expected_types=["store", "customer"], allowed_roles={"store": ["admin", "staff"]}, require_resource_match=True)
    def CreateCart(self, request, context):
        with transaction.atomic():
            order_type_str = ORDERTYPE.Name(request.order_type)
            phone = getattr(request, "user_phone_no", None)
            cart = None

            # Try lookup by cart_uuid
            if getattr(request, 'cart_uuid', None):
                cart = Cart.objects.filter(cart_uuid=request.cart_uuid, store_uuid=request.store_uuid).first()

            # Fallback lookup by phone
            if not cart and phone:
                cart = Cart.objects.filter(
                    store_uuid=request.store_uuid,
                    user_phone_no=phone,
                    state=Cart.cart_state.CART_STATE_ACTIVE
                ).first()

            if not cart:
                cart = Cart(store_uuid=request.store_uuid, user_phone_no=phone)

            if request.order_type == ORDERTYPE.ORDER_TYPE_DINE_IN:
                table = Table.objects.filter(
                    store_uuid=request.store_uuid,
                    table_number=request.table_no
                ).select_for_update().first()
                if not table:
                    context.abort(grpc.StatusCode.NOT_FOUND, f"Table {request.table_no} not found")

                session = ServiceSession.objects.filter(
                    table=table,
                    service_status=ServiceSession.ServiceStatus.SERVICE_SESSION_ONGOING
                ).first()

                if not session:
                    session = ServiceSession.objects.create(table=table)

                cart.table = table
                cart.service_session = session
                cart.vehicle_no = ""
                cart.vehicle_description = ""

            elif request.order_type == ORDERTYPE.ORDER_TYPE_DRIVE_THRU:
                cart.table = None
                cart.service_session = None
                cart.vehicle_no = request.vehicle_no or ""
                cart.vehicle_description = request.vehicle_description or ""

            else:
                cart.table = None
                cart.service_session = None
                cart.vehicle_no = ""
                cart.vehicle_description = ""

            cart.order_type = order_type_str
            cart.save()

            logger.info(f"Upserted Cart {cart.cart_uuid} (Type={order_type_str}, Phone={phone})")
            return self._Cart_to_response(cart)


    @handle_error
    @check_access(
        expected_types=["store", "customer"],
        allowed_roles={"store": ["admin", "staff"]},
        require_resource_match=True
    )
    def GetCart(self, request, context):
        if getattr(request, "cart_uuid", None):
            cart = Cart.objects.get_active_cart(cart_uuid=request.cart_uuid)
            return self._Cart_to_response(cart)
        elif getattr(request, "store_uuid", None) and getattr(request, "user_phone_no", None):
            cart = Cart.objects.get_active_cart(
                store_uuid=request.store_uuid,
                user_phone_no=request.user_phone_no
            )
            return self._Cart_to_response(cart)
        else:
            raise ValueError("Must provide either cart_uuid or both store_uuid and user_phone_no")

    @handle_error
    @check_access(expected_types=["store", "customer", "anonymous"], allowed_roles={"store": ["admin", "staff"]}, require_resource_match=True)
    def UpdateCart(self, request, context):
        logger.debug(f"UpdateCart request received: {request}")
        phone = getattr(request, "user_phone_no", None)

        if getattr(request, "cart_uuid", None):
            cart = Cart.objects.get_active_cart(
                cart_uuid=request.cart_uuid,
                user_phone_no=phone,
                store_uuid=request.store_uuid
            )
        elif getattr(request, "store_uuid", None) and phone:
            cart = Cart.objects.get_active_cart(
                store_uuid=request.store_uuid,
                user_phone_no=phone
            )
        else:
            logger.error("Missing required parameters for cart lookup")
            raise ValueError("Must provide either cart_uuid or both store_uuid and user_phone_no")

        with transaction.atomic():
            if request.HasField("order_type"):
                cart.order_type = ORDERTYPE.Name(request.order_type)

            if request.HasField("table_no"):
                table = Table.objects.filter(
                    store_uuid=request.store_uuid,
                    table_number=request.table_no
                ).select_for_update().first()
                if not table:
                    raise GrpcException(status_code=grpc.StatusCode.NOT_FOUND, details=f"Table not found: {request.table_no}")
                cart.table = table

                # Update session if order type is dine-in
                if request.order_type == ORDERTYPE.ORDER_TYPE_DINE_IN:
                    session = ServiceSession.objects.filter(
                        table=table,
                        service_status=ServiceSession.ServiceStatus.SERVICE_SESSION_ONGOING
                    ).first()
                    if not session:
                        session = ServiceSession.objects.create(table=table)
                    cart.service_session = session

            if request.HasField("vehicle_no"):
                cart.vehicle_no = request.vehicle_no

            if request.HasField("vehicle_description"):
                cart.vehicle_description = request.vehicle_description

            if request.HasField("special_instructions"):
                cart.special_instructions = request.special_instructions

            cart.full_clean()
            cart.save()

            logger.info(f"Successfully updated Cart:{cart.cart_uuid} for store:{cart.store_uuid} and user:{phone}")
            return self._Cart_to_response(cart)


    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def DeleteCart(self, request, context):

        if getattr(request,"cart_uuid",None):
            cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)
            cart.delete()
            logger.info(f"Cart:{cart.cart_uuid} for Phone_no:{cart.user_phone_no} at store:{cart.store_uuid} ")
            return empty_pb2.Empty()
        

        if getattr(request,"store_uuid",None) and getattr(request,"user_phone_no",None):
            cart = Cart.objects.get_active_cart(store_uuid = request.store_uuid,user_phone_no = request.user_phone_no)
            cart.delete()
            logger.info(f"Cart:{cart.cart_uuid} for Phone_no:{cart.user_phone_no} at store:{cart.store_uuid} ")
            return empty_pb2.Empty()
        
    @handle_error    
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def AddCartItem(self, request, context):
        logger.debug(f"AddCartItem request - Cart UUID: {request.cart_uuid}, Product UUID: {request.product_uuid}")

        cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)
        logger.debug(f"Found active cart: {cart.cart_uuid} for user: {cart.user_phone_no}")
        product_uuid = str(request.product_uuid)
        store_uuid = str(cart.store_uuid)
        
        product_request = GetProductRequest(
                product_uuid=product_uuid,
                store_uuid=store_uuid
                    )
        logger.debug(f"Making GetProduct request to Product service for product: {request.product_uuid}")
        
        try:
            logger.debug(f"Calling Product service with metadata: {self.meta_data}")
            response = self.Product_stub.GetProduct(product_request,metadata = self.meta_data)
            logger.debug(f"Received product response: {response}")
        except RpcError as e:
            error_message = e.details()
            if e.code() == StatusCode.NOT_FOUND:
                logger.error(f"Active Product: {request.product_uuid} not found")
                raise GrpcException(error_message,status_code=e.code())
            elif e.code() == StatusCode.INVALID_ARGUMENT:
                logger.error(f"Invalid argument error: {error_message}")
                raise GrpcException(error_message,status_code=e.code())
            elif e.code() == StatusCode.INTERNAL:
                logger.error(f"Internal server error: {error_message}")
                raise GrpcException(error_message,status_code=e.code())
            elif e.code() == StatusCode.UNAVAILABLE:
                logger.error(f"Product Service unavailable at: {PRODUCT_SERVICE_ADDR}")
                raise GrpcException("Internal Server Error",status_code=StatusCode.UNAVAILABLE)
            else:
                logger.error(f"Unexpected error: {error_message}")
                raise GrpcException("Internal Server Error",status_code=StatusCode.INTERNAL)

        if response.product is None:
            logger.error(f"Product response empty for product_uuid: {request.product_uuid}")
            raise GrpcException("Product Not Found",status_code=StatusCode.NOT_FOUND)
        if response.product.is_available == False:
            logger.error(f"Product {request.product_uuid} marked as unavailable")
            raise GrpcException("Product Not Available",status_code=StatusCode.NOT_FOUND)

        logger.debug(f"Product validation successful, creating cart item")

        with transaction.atomic():
            cart_item = CartItem.objects.create(
            cart = cart,
            product_name = response.product.name,
            product_uuid = response.product.product_uuid,
            tax_percentage = response.product.GST_percentage,
            packaging_cost = response.product.packaging_cost,
            unit_price = response.product.price,
            quantity = 1
            )

            logger.info(f"Created cart item {cart_item.cart_item_uuid} with product {response.product.name}")
            logger.debug(f"Cart item details - Price: {cart_item.unit_price}, Quantity: {cart_item.quantity}, Tax: {cart_item.tax_percentage}%")
            
            return self._Cart_to_response(cart)

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def RemoveCartItem(self, request, context):
        cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)

        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)
        with transaction.atomic():
            cart_item.delete()
            logger.info(f"Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
            return self._Cart_to_response(cart)


    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def CreateAddOn(self, request, context):
        logger.debug(f"CreateAddOn request - Cart UUID: {request.cart_uuid}, Cart Item UUID: {request.cart_item_uuid}")
        
        cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)
        logger.debug(f"Found active cart: {cart.cart_uuid} for user: {cart.user_phone_no}")
        
        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)
        logger.debug(f"Found cart item: {cart_item.cart_item_uuid} in cart: {cart.cart_uuid}")
        
        add_on_request = product_pb2.GetAddOnRequest(product_uuid=str(cart_item.product_uuid),store_uuid = str(cart.store_uuid),add_on_uuid = str(request.add_on_uuid))  
        logger.debug(f"Making GetAddOn request to Product service for addon: {request.add_on_uuid}")
        
        response:AddOnResponse|None = None  # Initialize response to None
        try:
            logger.debug(f"Calling Product service with metadata: {self.meta_data}")
            response = self.Product_stub.GetAddOn(add_on_request,metadata = self.meta_data)
            logger.debug(f"Received addon response: {response}")
        except RpcError as e:
            error_message = e.details()
            if e.code() == StatusCode.NOT_FOUND:
                logger.error(f"Active Product: {request.product_uuid} not found")
                raise GrpcException(error_message,status_code=e.code())
            elif e.code() == StatusCode.INVALID_ARGUMENT:
                logger.error(f"Invalid argument error: {error_message}")
                raise GrpcException(error_message,status_code=e.code())
            elif e.code() == StatusCode.INTERNAL:
                logger.error(f"Internal server error: {error_message}")
                raise GrpcException(error_message,status_code=e.code())
            elif e.code() == StatusCode.UNAVAILABLE:
                logger.error(f"Product Service unavailable at: {PRODUCT_SERVICE_ADDR}")
                raise GrpcException("Internal Server Error",status_code=StatusCode.UNAVAILABLE)
            
        if response and response.add_on.is_available == False:
            logger.error(f"Add-on: {request.add_on.add_on_uuid} is not available")
            raise GrpcException("Add-on Not Available",status_code=StatusCode.NOT_FOUND)

        logger.debug(f"Addon validation successful, creating addon")
        
        with transaction.atomic():
            add_on = AddOn.objects.create(
            cart_item = cart_item,
            add_on_name = response.add_on.name,
            add_on_uuid = response.add_on.add_on_uuid,
            quantity = 1,
            unit_price = response.add_on.price,
            is_free = response.add_on.is_free,
            max_selectable = response.add_on.max_selectable,
            )
            logger.info(f"Created addon {add_on.add_on_uuid} with name {response.add_on.name}")
            logger.debug(f"Addon details - Price: {add_on.unit_price}, Quantity: {add_on.quantity}, Is Free: {add_on.is_free}")
            
            return self._Cart_to_response(cart)

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def RemoveAddOn(self, request, context):
        cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)
        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)
        add_on = AddOn.objects.get(cart_item = cart_item,add_on_uuid = request.add_on_uuid)
        with transaction.atomic():
            add_on.delete()
            logger.info(f"Removed Add-on:{add_on.add_on_uuid} from Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
            return self._Cart_to_response(cart)

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def AddQuantity(self, request, context):
        cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)

        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)
        with transaction.atomic():
            cart_item.add_quantity(1)
            logger.info(f"Add Quantity t0 Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
            return self._Cart_to_response(cart)

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
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
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def IncreaseAddOnQuantity(self, request, context):
        cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)
        cart_item = CartItem.objects.get(cart = cart,cart_item_uuid = request.cart_item_uuid)
        add_on = AddOn.objects.get(cart_item = cart_item,add_on_uuid = request.add_on_uuid)
        with transaction.atomic():
            add_on.add_quantity(1)
            logger.info(f"Increased Quantity to Add-on:{add_on.add_on_uuid} in Cart_item:{cart_item.cart_item_uuid} in Cart:{cart.cart_uuid}")
            return self._Cart_to_response(cart)

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
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
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
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
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def AddCoupon(self, request, context):
        
        cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)

        coupon  = Coupon.objects.get(coupon_code = request.coupon_code,store_uuid = request.store_uuid)
        
        Valid,message = Coupon_Validator.validate(coupon=coupon,cart=cart)
        
        if not Valid:
            raise ValidationError(message=message)
        
        with transaction.atomic():
            cart.coupon_code = coupon.coupon_code
            cart.apply_discount(discount=coupon.discount)
            cart.save()
            logger.info(f"Applied discount to Cart:{cart.cart_uuid} from coupon {coupon.coupon_uuid}")
            return self._Cart_to_response(cart=cart)

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def RemoveCoupon(self, request, context):
        cart = Cart.objects.get_active_cart(cart_uuid = request.cart_uuid,user_phone_no = request.user_phone_no,store_uuid = request.store_uuid)
        with transaction.atomic():
            cart.remove_discount()
            return self._Cart_to_response(cart)

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
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
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
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
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def GetCoupon(self,request,context):

        coupon = Coupon.objects.get(coupon_uuid=request.coupon_uuid,
                                    store_uuid = request.store_uuid)
        
        return self._Coupon_to_response(coupon)


    @handle_error    
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
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
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def DeleteCoupon(self,request,context):
        coupon = Coupon.objects.get(coupon_uuid=request.coupon_uuid,
                                    store_uuid = request.store_uuid)
        with transaction.atomic():
            coupon.delete()
            logger.info(f"Coupon:{coupon.coupon_uuid} at store_uuid:{coupon.store_uuid}")        
            return self._Coupon_to_response(coupon)
        
    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
    def listCoupon(self,request,context):
        coupons,next_page,prev_page = Coupon.objects.get_coupons()

        return Cart_pb2.listCouponResponse(
            coupons=[self._Coupon_to_response(coupon) for coupon in coupons],
            next_page=next_page,
            prev_page=prev_page
            )   

    @handle_error
    @check_access(
    expected_types=["store"],
    allowed_roles={"store":["admin","staff"]},require_resource_match=True)
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
