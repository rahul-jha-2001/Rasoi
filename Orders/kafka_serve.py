import os
from confluent_kafka import Consumer, KafkaException, KafkaError
from google.protobuf.message import DecodeError
from dotenv import load_dotenv

import django
from django.conf import settings
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Orders.settings')
django.setup()

from utils.logger import Logger
from utils.gprc_pool import GrpcChannelPool
from Proto import cart_pb2,cart_pb2_grpc,order_pb2
from Order.models import Order,OrderItem,OrderItemAddOn,OrderPayment,order_types,order_state
from Proto.order_pb2 import KafkaOrderMessage,OrderState,PaymentState,PaymentMethod,OrderType
from Proto.cart_pb2 import CartResponse,GetCartRequest
from grpc import RpcError,StatusCode
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal


logger = Logger("KAFKA_service")
JWT_SECRET = os.getenv("JWT_SECRET","Rahul")
CART_SERVICE_ADDR = os.getenv("CART_SERVICE_ADDR","localhost:50051")
KAFKA_HOST = os.getenv("KAFKA_HOST",'localhost')
KAFKA_PORT = os.getenv("KAFKA_PORT","29092")
class OrderOpreation:
    def __init__(self,Cart_stub):
        self.DeserializedOrder = KafkaOrderMessage()
        self.stub = Cart_stub

    def _call_cart(self,cart_uuid:str,store_uuid:str) -> CartResponse:
        cart_request = GetCartRequest(cart_uuid=cart_uuid,store_uuid = store_uuid)
        try:
            response = self.stub.GetCart(cart_request)
        except RpcError as e:
            error_message = e.details()
            if e.code() == StatusCode.NOT_FOUND:
                logger.error(f"Active Cart:{cart_uuid} at Store:{store_uuid} not found")
                return None
            elif e.code() == StatusCode.INVALID_ARGUMENT:
                logger.error(error_message)
                raise ValidationError(error_message)
            elif e.code() == StatusCode.INTERNAL:
                raise Exception(error_message)
        return response
    
    def _payment_order(self,orderpayment: order_pb2.OrderPayment,order:Order) -> OrderPayment:
            try:
                # Debug logging
                logger.debug(f"Creating payment with data: {orderpayment}")
                logger.debug(f"Order ID: {order.order_uuid}")
                
                try:
                    amount = Decimal(orderpayment.amount)
                    logger.debug(f"Amount converted: {amount}")
                except Decimal.InvalidOperation as e:
                    logger.error(f"Invalid amount: {orderpayment.amount}")
                    raise ValueError(f"Invalid amount value: {orderpayment.amount}") from e

                try:
                    method = PaymentMethod.Name(orderpayment.payment_method)
                    status = PaymentState.Name(orderpayment.payment_status)
                    logger.debug(f"Enums converted - Method: {method}, Status: {status}")
                except ValueError as e:
                    logger.error(f"Invalid enum value - Method: {orderpayment.payment_method}, "
                            f"Status: {orderpayment.payment_status}")
                    raise

                payment = OrderPayment.objects.create(
                    order=order,
                    amount=amount,
                    method=method,
                    status=status,
                    time=orderpayment.payment_time,
                    notes=orderpayment.notes,
                    rz_payment_id=orderpayment.rz_payment_id,
                    rz_order_id=orderpayment.rz_order_id,
                    rz_signature=orderpayment.rz_signature
                )
                logger.info(f"Payment created successfully: {payment.id}")
                return payment
            except ValidationError as e:
                # logger.error(f"ValidationError creating Payment:{str(e)}")
                raise
            except ValueError as e:
                # logger.error(f"ValueError creating Payment:{str(e)}")
                raise
            except IntegrityError as e:
                # logger.error(f"IntegrityError creating Payment:{str(e)}")
                raise

            except Exception as e:
                logger.error("Payment creation failed",error = e)
                raise

    def _cart_to_order(self,response:CartResponse) -> Order:   

        with transaction.atomic():# Extract cart details
            cart = response.cart
            try:
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
            except ValidationError as e:
                # logger.error(f"Validation error in order creation: {str(e)}")
                raise
            except ValueError as e:
                # logger.error(f"Value error in order creation: {str(e)}")
                raise
                
            except IntegrityError as e:
                # logger.error(f"Database integrity error: {str(e)}")
                raise
                
            except Exception as e:
                # logger.error(f"Unexpected error in order creation: {str(e)}",e)
                raise        
    
    def create(self, data):
        
        if not data:
            logger.warning("Empty data received for order creation")
            raise ValueError("Received empty data for order creation.")
        
        logger.info(f"Received cart data | Size: {len(data)} bytes")
        
        # Deserialize protobuf
        try:
            self.DeserializedOrder.ParseFromString(data)
            cart_uuid = self.DeserializedOrder.cart_uuid 
            store_uuid = self.DeserializedOrder.store_uuid
            payment = self.DeserializedOrder.payment
        except (DecodeError, AttributeError) as e:
            logger.error(f"Protobuf deserialization failed: {str(e)}")
            raise ValueError("Invalid message format") from e  

        try:
            existing_order = Order.objects.select_related('payment').get(
                cart_uuid=cart_uuid,
                store_uuid=store_uuid
            )
            logger.info(f"Found existing order {existing_order.order_uuid} - skipping creation")
            return existing_order
        except Order.DoesNotExist:
            pass        
            # Process order
        try:
            response = self._call_cart(cart_uuid=cart_uuid, store_uuid=store_uuid)
            order = self._cart_to_order(response)
            self._payment_order(payment, order)
            return order
            
        except (ValidationError, ValueError, IntegrityError, AttributeError) as e:
            # logger.error(f"Order processing failed: {str(e)}")
            raise  # Re-raise to maintain error type
        except Exception as e:
            logger.critical(f"Unexpected error in order creation: {str(e)}",e)
            raise RuntimeError("Order creation failed") from e
        
    def update(self, data):
        if not data:
            logger.warning("Empty data received for order update")
            raise ValueError("Received empty data for order update.")
        
        logger.info(f"Received order update data | Size: {len(data)} bytes")
        
        # Deserialize protobuf
        try:
            self.DeserializedOrder.ParseFromString(data)
            cart_uuid = self.DeserializedOrder.cart_uuid 
            store_uuid = self.DeserializedOrder.store_uuid
            payment = self.DeserializedOrder.payment
            order_state = self.DeserializedOrder.order_status
            operation = self.DeserializedOrder.operation
        except (DecodeError, AttributeError) as e:
            logger.error(f"Protobuf deserialization failed: {str(e)}")
            raise ValueError("Invalid message format") from e
        
        try:
            order =  Order.objects.select_for_update().prefetch_related("payment").get(
                cart_uuid=cart_uuid,
                store_uuid=store_uuid
            )
        except Order.DoesNotExist:
            logger.error(f"Order not found for cart:{cart_uuid} store:{store_uuid}")
            raise 

        with transaction.atomic():
            try:
                # Update payment status if payment info exists
                if payment and order.payment:
                    order.payment.update_status(PaymentState.Name(payment.payment_status))
                
                # Update order status
                if order_state:
                    order.order_status = OrderState.Name(order_state)
                    order.save()
                    
                logger.info(
                    f"Order:{order.order_uuid} Order-No:{order.order_no} "
                    f"status changed to {order.order_status}"
                )

                return  order
            except ValidationError as e:
                logger.error(f"Validation error updating order: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Error updating order: {str(e)}", error=e)
                raise


class KafkaServer:
    def __init__(self):
        try:
            load_dotenv()
            kafka_brokers = f"{KAFKA_HOST}:{KAFKA_PORT}"
            group_id = 'order_service_group'
            self.consumer_config = {
                'bootstrap.servers': kafka_brokers,
                'group.id': group_id,
                'auto.offset.reset': 'earliest',
                'enable.auto.commit': False,  # Commit offsets manually
            }
            logger.info(f"Kafka brokers: {kafka_brokers}")
            logger.info(f"Consumer group ID: {group_id}")

            self.consumer = Consumer(self.consumer_config)
            self.consumer.subscribe(['Orders'])
            logger.info(f"Subscribed to topic: Orders")


            self.channel_pool = GrpcChannelPool()
            self.channel = self.channel_pool.get_channel(CART_SERVICE_ADDR)
            self.Cart_stub = cart_pb2_grpc.CartServiceStub(self.channel)
            logger.info(f"Initialized gRPC channel to Cart Service at {CART_SERVICE_ADDR}")

            self.place_order_handler = OrderOpreation(Cart_stub = self.Cart_stub)
            # self.update_order_handler = UpdateOrder(Cart_stub = self.cart_stub)
            self.shutdown_flag = False
            

        except Exception as e:
            logger.critical(f"Failed to initialize KafkaServer: {e}",e)
            raise

    def _process_message(self, message):
        try:
            key = message.key().decode('utf-8')
            data = message.value()
            logger.info(f"Processing message with key: {key}")
            
            if key == "OrderPlaced":
                try:
                    order = self.place_order_handler.create(data)
                    logger.info(f"Order {order.order_uuid} placed for cart {order.cart_uuid} at store {order.store_uuid}")
                    return True  # Success flag
                except ValidationError as e:
                    logger.error(f"Validation failed for order: {str(e)}")
                except ValueError as e:
                    logger.error(f"Invalid data in order: {str(e)}")
                except IntegrityError as e:
                    logger.error(f"Database integrity error for order: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error processing order: {str(e)}",error=e)
                return False  # Failure flag
            
            if key == "OrderUpdate":
                try:
                    order = self.place_order_handler.update(data)
                    logger.info(f"Order {order.order_uuid} placed for cart {order.cart_uuid} at store {order.store_uuid}")
                    return True  # Success flag
                except ValidationError as e:
                    logger.error(f"Validation failed for order: {str(e)}")
                except ValueError as e:
                    logger.error(f"Invalid data in order: {str(e)}")
                except IntegrityError as e:
                    logger.error(f"Database integrity error for order: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error processing order: {str(e)}",error=e)
                return False  # Failure flag

            logger.warning(f"Unhandled event type: {key}")
            return False  # Unhandled message type
            
        except UnicodeDecodeError as e:
            logger.error(f"Failed to decode message key: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}",e)
            return False

    def run(self):
        """Main Kafka consumer loop with batch processing and graceful shutdown."""
        try:
            while not self.shutdown_flag:
                msgs = self.consumer.consume(num_messages=10, timeout=0.5)
                
                for msg in msgs:
                    if msg is None:
                        continue
                        
                    if msg.error():
                        self._handle_kafka_error(msg.error())
                        continue

                    try:
                        processing_success = self._process_message(msg)
                        if processing_success:
                            self.consumer.commit(msg)
                        else:
                            logger.warning("Message processing failed - not committing offset")
                    except Exception as e:
                        logger.error(f"Critical error processing message: {str(e)}",error=e)
                        # Consider whether to continue or shutdown based on error severity

        except KeyboardInterrupt:
            logger.info("Graceful shutdown initiated")
            self._shutdown()

    def _handle_kafka_error(self, error):
        """Handle Kafka-specific errors"""
        if error.code() == KafkaError._PARTITION_EOF:
            logger.info(f"End of partition reached: {error}")
        elif error.code() == KafkaError.UNKNOWN_TOPIC_OR_PART:
            logger.error(f"Topic/partition error: {error}")
        else:
            logger.error(f"Kafka protocol error: {error}")

    def _shutdown(self):
        """Graceful shutdown procedure"""
        try:
            self.consumer.close()
            logger.info("Kafka consumer closed gracefully")
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}",e)
        finally:
            self.shutdown_flag = True


if __name__ == "__main__":
     
     """Starts the Kafka server."""
     try:
        kafka_server = KafkaServer()
        logger.info("Starting Kafka server...")
        kafka_server.run()
     except Exception as e:
        logger.error(f"Error in Kafka server: {e}",e)