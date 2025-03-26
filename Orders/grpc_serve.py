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
from google.protobuf import empty_pb2
from google.protobuf.timestamp_pb2 import Timestamp

from Proto import order_pb2,order_pb2_grpc,cart_pb2,cart_pb2_grpc

from Proto.order_pb2 import OrderState,OrderItemState,OrderItemAddOnState
from Order.models import Order,OrderItem,OrderItemAddOn,OrderPayment


from utils.logger import Logger

load_dotenv()

logger = Logger("GRPC_service")

def handle_error(func):
    def wrapper(self, request, context):
        try:
            return func(self, request, context)
        except Order.DoesNotExist:
            logger.warning(f"Order Not Found: Cart_uuid:{getattr(request, 'cart_uuid', '')} Store_uuid:{getattr(request, 'store_uuid', '')} user_phone_no:{getattr(request, 'user_phone_no', '')}")
            context.abort(grpc.StatusCode.NOT_FOUND, f"Cart Not Found: Cart_uuid:{getattr(request, 'cart_uuid', '')} Store_uuid:{getattr(request, 'store_uuid', '')} user_phone_no:{getattr(request, 'user_phone_no', '')}")

        except OrderItem.DoesNotExist:
            logger.error(f"CartItem Not Found: cart_item_uuid:{getattr(request, 'cart_item_uuid', '')}")
            context.abort(grpc.StatusCode.NOT_FOUND, f"CartItem Not Found: cart_item_uuid:{getattr(request, 'cart_item_uuid', '')}")
            
        except OrderItemAddOn.DoesNotExist:
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

# def interceptor:
#     metadata = context.invocation_metadata()

#         # Convert metadata to a dictionary
#         metadata_dict = {key: value for key, value in metadata}

#         # Log or use metadata
#         token = str(metadata_dict.get("authorization", "").split(" ")[-1])

#         logger.info(f"Authorization token:{token}")
#         try:
#             decoded = jwt.decode(token, options={"verify_signature": False})
#             print("Token is valid:", decoded)
#         except jwt.ExpiredSignatureError:
#             logger.error("Token is expired")
#             context.abort(grpc.StatusCode.UNAUTHENTICATED, "Token is expired")
#         except jwt.InvalidSignatureError:
#             logger.error("Token signature is invalid")
#             context.abort(grpc.StatusCode.UNAUTHENTICATED, "Token signature is invalid")
#         except jwt.InvalidTokenError:
#             logger.error("Token is invalid")
#             context.abort(grpc.StatusCode.UNAUTHENTICATED, "Token is invalid")

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
            response = order_pb2.AddOn(
                add_on_uuid = add_on.add_on_uuid,
                add_on_name = add_on.add_on_name,
                quantity = add_on.quantity,
                unit_price = add_on.unit_price,
                is_free = add_on.is_free,
                subtotal_amount = add_on.subtotal_amount
            )

            if not self._verify_wire_format(response, order_pb2.OrderItemAddOn, f"add_on_id:{add_on.add_on_uuid}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize AddOn:{add_on.add_on_uuid}")
            return response
        except Exception as e:
            logger.error(f"Unexpected error in _CartItem_to_response: {e}")
            raise
            
    def _item_to_response(self, item:OrderItem) -> order_pb2.OrderItem:
        try:
            response = order_pb2.OrderItem(
                item_uuid = item.item_uuid,
                product_uuid = item.product_uuid,
                product_name = item.product_name,
                unit_price = item.unit_price,
                quantity = item.quantity,
                discount = item.discount,
                tax_percentage = item.tax_percentage,
                
                packaging_cost = item.packaging_cost,
                subtotal_amount = item.subtotal_amount,
                discount_amount = item.discount_amount,
                tax_amount = item.tax_amount,
                price_before_tax = item.price_before_tax,
                total_amount = item.total_amount,

                add_ons = [self._add_on_to_response(add_on) for add_on in item.add_ons.all()]

            )

            if not self._verify_wire_format(response, order_pb2.OrderItem, f"item_id:{item.item_uuid}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize Item:{item.item_uuid}")
            return response
        except Exception as e:
            logger.error(f"Unexpected error in _item_to_response: {e}")
            raise

    def _payment_to_response(self, payment:OrderPayment) -> order_pb2.OrderPayment:
        try:
            response = order_pb2.Payment(
                payment_uuid = payment.payment_uuid,
                rz_order_id = payment.rz_order_id,
                rz_payment_id = payment.rz_payment_id,
                rz_signature = payment.rz_signature,
                amount = payment.amount,
                payment_status = payment.status,
                payment_method = payment.payment_method,
                notes = payment.notes,

                payment_time = payment.payment_time

            )
            if not self._verify_wire_format(response, order_pb2.Payment, f"payment_id:{payment.payment_id}"):
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize Payment:{payment.payment_id}")
            return response
        except Exception as e:
            logger.error(f"Unexpected error in _payment_to_response: {e}")
            raise            

    def _user_order_to_response(self, order:Order) -> order_pb2.OrderUserView:
        try:
            response = order_pb2.Order(
                order_uuid = order.order_uuid,
                order_no = order.order_no,
                store_uuid = order.store_uuid,
                user_phone_no = order.user_phone_no,
                order_type = order.order_type,
                table_no = order.table_no,
                vehicle_no = order.vehicle_no,
                vehicle_description = order.vehicle_description,
                coupon_code = order.coupon_code,
                Items = [self._item_to_response(item) for item in order.items.all()],
                special_instructions = order.special_instructions,
                order_status = order.order_status,
                payment_status = order.payment_status,
                payment_method = order.payment_method,


                subtotal_amount = order.subtotal_amount,
                discount_amount = order.discount_amount,
                price_before_tax = order.price_before_tax,
                tax_amount = order.tax_amount,
                packaging_cost = order.packaging_cost,
                final_amount = order.final_amount,

                created_at = order.created_at,
                updated_at = order.updated_at
            )
            if not self._verify_wire_format(response, order_pb2.Order, f"order_id:{order.order_uuid}"): 
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize Order:{order.order_uuid}")
            return response
        except Exception as e:
            logger.error(f"Unexpected error in _userorder_to_response: {e}")        

    def _store_order_to_response(self, order:Order) -> order_pb2.OrderStoreView:
        try:
            response = order_pb2.Order(
                
                order_uuid = order.order_uuid,
                order_no = order.order_no,
                store_uuid = order.store_uuid,
                user_phone_no = order.user_phone_no,
                order_type = order.order_type,
                table_no = order.table_no,
                vehicle_no = order.vehicle_no,
                vehicle_description = order.vehicle_description,
                coupon_code = order.coupon_code,
                Items = [self._item_to_response(item) for item in order.items.all()],
                special_instructions = order.special_instructions,
                order_status = order.order_status,
                payment_status = self._payment_to_response(order.payement.all()[0]) if order.payement.all() else None,

                subtotal_amount = order.subtotal_amount,
                discount_amount = order.discount_amount,
                price_before_tax = order.price_before_tax,
                tax_amount = order.tax_amount,
                packaging_cost = order.packaging_cost,
                final_amount = order.final_amount,

                created_at = order.created_at,
                updated_at = order.updated_at
            )
            if not self._verify_wire_format(response, order_pb2.Order, f"order_id:{order.order_uuid}"): 
                raise grpc.RpcError(grpc.StatusCode.INTERNAL, f"Failed to serialize Order:{order.order_uuid}")
            return response
        except Exception as e:
            logger.error(f"Unexpected error in _userorder_to_response: {e}")        

    @handle_error
    @transaction.atomic
    def CreateOrder(self, request, context):
        order = request.order
        try:
            order = Order.objects.create(
                store_uuid = order.store_uuid,
                user_phone_no = order.user_phone_no,
                order_type = order.order_type,
                table_no = order.table_no,
                vehicle_no = order.vehicle_no,
                vehicle_description = order.vehicle_description,
                
                coupon_code = order.coupon_code,
                special_instructions = order.special_instructions,
                
                order_status = order.order_status,
                payment_status = order.payment_status,
                payment_method = order.payment_method,

                subtotal_amount = order.subtotal_amount,
                discount_amount = order.discount_amount,
                price_before_tax = order.price_before_tax,
                tax_amount = order.tax_amount,
                packaging_cost = order.packaging_cost,
                final_amount = order.final_amount
            )

            for item in request.order.Items:
                order_item = OrderItem.objects.create(
                    order = order,
                    product_uuid = item.product_uuid,
                    product_name = item.product_name,
                    unit_price = item.unit_price,
                    quantity = item.quantity,
                    discount = item.discount,
                    tax_percentage = item.tax_percentage,
                    packaging_cost = item.packaging_cost,
                    subtotal_amount = item.subtotal_amount,
                    discount_amount = item.discount_amount,
                    tax_amount = item.tax_amount,
                    price_before_tax = item.price_before_tax,
                    total_amount = item.total_amount
                )

                for add_on in item.add_ons:
                    OrderItemAddOn.objects.create(
                        item = order_item,
                        add_on_name = add_on.add_on_name,
                        quantity = add_on.quantity,
                        unit_price = add_on.unit_price,
                        is_free = add_on.is_free,
                        subtotal_amount = add_on.subtotal_amount
                    )
            return order_pb2.UserOrderResponse(
                order = self._store_order_to_response(order))
        except Exception as e:
            raise

    @handle_error
    def GetOrder(self, request, context):
        try:
            order = Order.objects.get(order_uuid=request.order_uuid)
            return self._userorder_to_response(order)
        except Exception as e:
            raise



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    order_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(),server)

    grpc_port = os.getenv('GRPC_SERVER_PORT', '50051')

    server.add_insecure_port(f"[::]:{grpc_port}")
    server.start()
    logger.info(f"Server Stated at {grpc_port}")
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
