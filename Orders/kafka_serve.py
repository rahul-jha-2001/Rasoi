import os
import logging
import traceback
import uuid
from confluent_kafka import Consumer, KafkaException, KafkaError
from google.protobuf.message import DecodeError
from dotenv import load_dotenv

import django
from django.conf import settings
from django.db import transaction,IntegrityError
from django.core.exceptions import ValidationError
django.setup()

from utils.logger import Logger
from Order.models import Order, OrderItem
from proto import Order_pb2


logger = Logger.get_logger("Kafka_Order", logging.INFO)


class PlaceOrder:
    def __init__(self):
        self.DeserializedOrder = Order_pb2.Order()

    @staticmethod
    @transaction.atomic
    def _proto_to_django_order(order_proto: Order_pb2.Order) -> Order:
        """
        Convert a Protobuf Order message to a Django Order instance, strictly for creation.
        """

        correlation_id = str(uuid.uuid4())
        log_context = {
            'correlation_id': correlation_id,
            'order_uuid': order_proto.OrderUuid,
            'store_uuid': order_proto.StoreUuid,
        }

        try:
            # Detailed logging of order creation attempt
            logger.info(f"Attempting to create order | Context: {log_context}")

            # Create a new Order instance
            order = Order.objects.create(
                OrderUuid=order_proto.OrderUuid,  # This must be unique
                StoreUuid=order_proto.StoreUuid,
                UserPhoneNo=order_proto.UserPhoneNo,
                OrderType=order_proto.OrderType,
                TableNo=order_proto.TableNo if order_proto.HasField("TableNo") else None,
                VehicleNo=order_proto.VehicleNo if order_proto.HasField("VehicleNo") else None,
                VehicleDescription=order_proto.VehicleDescription if order_proto.HasField("VehicleDescription") else None,
                CouponName=order_proto.CouponName if order_proto.HasField("CouponName") else None,
                TotalAmount=order_proto.TotalAmount,
                DiscountAmount=order_proto.DiscountAmount,
                FinalAmount=order_proto.FinalAmount,
                PaymentStatus=order_proto.PaymentState,
                PaymentMethod=order_proto.PaymentMethod,
                SpecialInstruction=order_proto.SpecialInstruction,
                OrderStatus=order_proto.OrderStatus,
            )

            # Create OrderItems associated with the Order
            order_items_context = []
            for item_proto in order_proto.Items:
                OrderItem.objects.create(
                    Order=order,
                    ProductUuid=item_proto.ProductUuid,
                    Price=item_proto.Price,
                    Quantity=item_proto.Quantity,
                    Discount=item_proto.Discount,
                    Subtotal=item_proto.SubTotal,
                    TaxedAmount=item_proto.TaxedAmount,
                    DiscountAmount=item_proto.DiscountAmount,
                )
            logger.info(f"Order created successfully | Context: {log_context}, Items: {order_items_context}")
            return order
        except IntegrityError as e:
            # Specific handling for integrity errors
            logger.warning(
                f"Integrity error during order creation | "
                f"Context: {log_context}, "
                f"Error: {str(e)}"
            )
            # Optionally, try to retrieve existing order or handle duplicate
        except ValidationError as e:
            # Handle validation errors with detailed logging
            logger.error(
                f"Validation error during order creation | "
                f"Context: {log_context}, "
                f"Errors: {e.message_dict}"
            )
            raise

        except Exception as e:
            # Catch-all for unexpected errors with full traceback
            logger.error(
                f"Unexpected error during order creation | "
                f"Context: {log_context}, "
                f"Error: {str(e)}\n"
                f"Traceback: {traceback.format_exc()}"
            )
            raise

    def create(self, data):
        """
        Create an order from serialized Protobuf data.
        
        Args:
            data (bytes): Serialized Protobuf data
        
        Returns:
            Order: Created order instance
        """
        correlation_id = str(uuid.uuid4())

        try:
            if not data:
                logger.warning(f"Empty data received for order creation | Correlation ID: {correlation_id}")
                raise ValueError("Received empty data for order creation.")
            
            # Log incoming data size for monitoring
            logger.info(f"Received order data | Size: {len(data)} bytes | Correlation ID: {correlation_id}")
            self.DeserializedOrder.ParseFromString(data)
            return self._proto_to_django_order(self.DeserializedOrder)
        except DecodeError as e:
            logger.error(
                f"Protobuf DecodeError | "
                f"Correlation ID: {correlation_id}, "
                f"Error: {str(e)}, "
                f"Possible data corruption"
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error in order creation | "
                f"Correlation ID: {correlation_id}, "
                f"Error: {str(e)}\n"
                f"Traceback: {traceback.format_exc()}"
            )
            raise



class UpdateOrder:
    def __init__(self):
        self.DeserializedOrder = Order_pb2.Order()

    @staticmethod
    @transaction.atomic
    def proto_to_django_order(order_proto: Order_pb2.Order) -> Order:
        """
        Update an existing Django Order instance from a Protobuf Order message.
        
        Args:
            order_proto (Order_pb2.Order): Protobuf order message to update
        
        Returns:
            Order: Updated order instance
        """
        correlation_id = str(uuid.uuid4())
        log_context = {
            'correlation_id': correlation_id,
            'order_uuid': order_proto.OrderUuid,
            'store_uuid': order_proto.StoreUuid,
        }
        try:
            try:
                # Retrieve the existing Order instance
                order = Order.objects.get(OrderUuid=order_proto.OrderUuid)
            except Order.DoesNotExist:
                    logger.error(f"Order not found for update | Context: {log_context}")
                    raise    

            # Update fields of the Order
            # order.StoreUuid = order_proto.StoreUuid
            # order.UserPhoneNo = order_proto.UserPhoneNo

            # Prepare update log for existing order
            original_state = {
                'store_uuid': order.StoreUuid,
                'total_amount': order.TotalAmount,
                'order_status': order.OrderStatus,
                'payment_status': order.PaymentStatus,
            }


            order.OrderType = order_proto.OrderType
            order.TableNo = order_proto.TableNo if order_proto.HasField("TableNo") else None
            order.VehicleNo = order_proto.VehicleNo if order_proto.HasField("VehicleNo") else None
            order.VehicleDescription = order_proto.VehicleDescription if order_proto.HasField("VehicleDescription") else None
            order.CouponName = order_proto.CouponName if order_proto.HasField("CouponName") else None
            order.TotalAmount = order_proto.TotalAmount
            order.DiscountAmount = order_proto.DiscountAmount
            order.FinalAmount = order_proto.FinalAmount
            order.PaymentStatus = order_proto.PaymentState
            order.PaymentMethod = order_proto.PaymentMethod
            order.SpecialInstruction = order_proto.SpecialInstruction
            order.OrderStatus = order_proto.OrderStatus
            try:
                    order.full_clean()
                    order.save()
            except ValidationError as ve:
                logger.error(
                    f"Validation error during order update | "
                    f"Context: {log_context}, "
                    f"Validation Errors: {ve.message_dict}"
                )
                raise
            

            # Log updated order items
            updated_items_context = []
            # Update OrderItems associated with the Order
            for item_proto in order_proto.Items:
                # Update or create items associated with the order
                try:
                    order_item, created = OrderItem.objects.update_or_create(
                                Order=order,
                                ProductUuid=item_proto.ProductUuid,
                                defaults={
                                    'Price': item_proto.Price,
                                    'Quantity': item_proto.Quantity,
                                    'Discount': item_proto.Discount,
                                    'Subtotal': item_proto.SubTotal,
                                    'TaxedAmount': item_proto.TaxedAmount,
                                    'DiscountAmount': item_proto.DiscountAmount,
                                }
                            )
                    updated_items_context.append({
                            'product_uuid': item_proto.ProductUuid,
                            'created': created,
                            'quantity': item_proto.Quantity,
                            'subtotal': item_proto.SubTotal
                        })
                except Exception as item_error:
                    logger.error(
                        f"Error updating order item | "
                        f"Context: {log_context}, "
                        f"Product UUID: {item_proto.ProductUuid}, "
                        f"Error: {str(item_error)}"
                    )
                    raise

                # Log successful update with changes
                logger.info(
                    f"Order updated successfully | "
                    f"Context: {log_context}, "
                    f"Original State: {original_state}, "
                    f"Updated Items: {updated_items_context}"
                )

                return order

        except Order.DoesNotExist as e:
            logger.error(
                f"Order not found for update | "
                f"Context: {log_context}, "
                f"Error: {str(e)}"
            )
            raise

        except ValidationError as ve:
            logger.error(
                f"Validation error during order update | "
                f"Context: {log_context}, "
                f"Validation Errors: {ve.message_dict}"
            )
            raise

        except Exception as e:
            logger.error(
                f"Unexpected error while updating order | "
                f"Context: {log_context}, "
                f"Error: {str(e)}\n"
                f"Traceback: {traceback.format_exc()}"
            )
            raise
    



    def update(self, data):
        """
        Update an order from serialized Protobuf data.
        
        Args:
            data (bytes): Serialized Protobuf data
        
        Returns:
            Order: Updated order instance
        """
        correlation_id = str(uuid.uuid4())
        try:
            if not data:
                logger.warning(f"Empty data received for order update | Correlation ID: {correlation_id}")
                raise ValueError("Received empty data for order update.")
            # Log incoming data size for monitoring
            logger.info(f"Received order update data | Size: {len(data)} bytes | Correlation ID: {correlation_id}")
            
            self.DeserializedOrder.ParseFromString(data)
            return self.proto_to_django_order(self.DeserializedOrder)
        
        
        except DecodeError as e:
            logger.error(
                f"Protobuf DecodeError during order update | "
                f"Correlation ID: {correlation_id}, "
                f"Error: {str(e)}, "
                f"Possible data corruption"
            )
            raise

        except Exception as e:
            logger.error(
                f"Unexpected error in order update | "
                f"Correlation ID: {correlation_id}, "
                f"Error: {str(e)}\n"
                f"Traceback: {traceback.format_exc()}"
            )
            raise





class KafkaServer:
    def __init__(self):
        try:
            load_dotenv()
            kafka_brokers = os.getenv('KAFKA_BROKERS', 'kafka:29092')
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

            self.place_order_handler = PlaceOrder()
            self.update_order_handler = UpdateOrder()
            self.shutdown_flag = False


        except Exception as e:
            logger.critical(f"Failed to initialize KafkaServer: {e}")
            logger.debug(traceback.format_exc())
            raise

    def _process_message(self, message):
        try:
            key = message.key().decode('utf-8')
            data = message.value()
            logger.info(f"Processing message with key: {key}")

            if key == "OrderPlaced":
                try:
                    self.place_order_handler.create(data)
                    logger.info("Order placed successfully.")
                except Exception as e:
                    logger.info("Order cannot be placed")

            elif key == "OrderUpdate":
                try:
                    self.Update_order_handler.update(data)
                    logger.info("Order Updated successfully.")
                except Exception as e:
                    logger.info("Order cannot be Updated")    
            else:
                logger.warning(f"Unhandled event type: {key}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            logger.debug(traceback.format_exc())
            raise

    def run(self):
        """
        Main Kafka consumer loop with batch processing and graceful shutdown.
        """
        try:
            while not self.shutdown_flag:
                msgs = self.consumer.consume(num_messages=10, timeout=1.0)
                for msg in msgs:
                    if msg is None:
                        continue
                    if msg.error():
                        if msg.error().code() == KafkaError._PARTITION_EOF:
                            logger.info(f"End of partition reached: {msg.error()}")
                        else:
                            logger.error(f"Kafka error: {msg.error()}")
                        continue

                    try:
                        self._process_message(msg)
                        self.consumer.commit(msg)
                    except Exception:
                        logger.error(f"Message processing failed. Key: {msg.key()}")

        except KeyboardInterrupt:
            logger.info("Kafka consumer stopping due to keyboard interrupt.")
            self.shutdown_flag = True
        except Exception as e:
            logger.error(f"Unhandled error in Kafka consumer: {e}")
            logger.debug(traceback.format_exc())
        finally:
            self.consumer.close()
            logger.info("Kafka consumer closed.")

    def stop(self):
        """
        Signal the consumer loop to stop.
        """
        self.shutdown_flag = True


if __name__ == "__main__":
     
     """Starts the Kafka server."""
     try:
        kafka_server = KafkaServer()
        logger.info("Starting Kafka server...")
        kafka_server.run()
     except Exception as e:
        logger.error(f"Error in Kafka server: {e}")