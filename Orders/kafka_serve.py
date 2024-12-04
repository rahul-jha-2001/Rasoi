# import sys 
# import os

# sys.path.append(os.getcwd()+r"\Orders\proto")
# import logging
# from dotenv import load_dotenv 

# from confluent_kafka import Consumer, KafkaException
# from confluent_kafka import Message
# import traceback
# import django
# from django.db import transaction
# logger = logging.getLogger(__name__)
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Orders.settings')
# django.setup()
# from Order.models import Order,OrderItem
# from proto import Order_pb2
# class PlaceOrder:
#     def __init__(self):
#         self.DeserializedOrder = Order_pb2.Order()

    
#     @staticmethod
#     @transaction.atomic
#     def proto_to_django_order(order_proto: Order_pb2.Order) -> Order:
#         """
#         Convert a Protobuf Order message to a Django Order instance.
#         """
#         # Create or update the main Order instance
#         order, created = Order.objects.update_or_create(
#             OrderUuid=order_proto.OrderUuid,  # Match using OrderUuid
#             defaults={
#                 'StoreUuid': order_proto.StoreUuid,
#                 'UserPhoneNo': order_proto.UserPhoneNo,
#                 'OrderType': order_proto.OrderType,
#                 'TableNo': order_proto.TableNo if order_proto.HasField("TableNo") else None,
#                 'VehicleNo': order_proto.VehicleNo if order_proto.HasField("VehicleNo") else None,
#                 'VehicleDescription': order_proto.VehicleDescription if order_proto.HasField("VehicleDescription") else None,
#                 'CouponName': order_proto.CouponName if order_proto.HasField("CouponName") else None,
#                 'TotalAmount': order_proto.TotalAmount,
#                 'DiscountAmount': order_proto.DiscountAmount,
#                 'FinalAmount': order_proto.FinalAmount,
#                 'PaymentStatus': order_proto.PaymentState,
#                 'PaymentMethod': order_proto.PaymentMethod,
#                 'SpecialInstruction': order_proto.SpecialInstruction,
#                 'OrderStatus': order_proto.OrderStatus,
#             }
#         )

#         # Create or update OrderItems associated with the Order
#         for item_proto in order_proto.Items:
#             OrderItem.objects.update_or_create(
#                 Order=order,  # Reference the main Order instance
#                 ProductUuid=item_proto.ProductUuid,  # Match using ProductUuid
#                 defaults={
#                     'Price': item_proto.Price,
#                     'Quantity': item_proto.Quantity,
#                     'Discount': item_proto.Discount,
#                     'Subtotal': item_proto.SubTotal,
#                     'TaxedAmount': item_proto.TaxedAmount,
#                     'DiscountAmount': item_proto.DiscountAmount,
#                 }
#             )

#         return order

#     def create(self, data):
#         """
#         Create an order from serialized Protobuf data.
#         """
#         print(data)
#         try:
#             # Validate data before parsing
#             if not data:
#                 raise ValueError("Received empty data for order creation.")
            
#             logging.info("Parsing Protobuf Order message.")
#             self.DeserializedOrder.ParseFromString(data)

#             # Convert to Django model
#             logging.info("Converting Protobuf Order to Django model.")
#             order = PlaceOrder.proto_to_django_order(self.DeserializedOrder)
#             logging.info(f"Order created successfully: {order.id}")

#         # except  protobuf.exDecodeError as e:
#         #     logging.error(f"Protobuf DecodeError: {e}. Data may be corrupted or invalid.")
#         #     raise
#         except Exception as e:
#             logging.error(f"Error in creating order: {e}")
#             raise


# class UpdateOrder(PlaceOrder):
#     """
#     Subclass for updating orders.
#     Inherits the proto_to_django_order logic from PlaceOrder.
#     """
#     def update(self, data):
#         """
#         Update an existing Order based on the Protobuf message.
#         """
#         # Deserialize Protobuf data
#         self.DeserializedOrder.ParseFromString(data)

#         # Convert Protobuf Order to Django Order (update logic is shared)
#         return self.proto_to_django_order(self.DeserializedOrder)



# class KafkaServer:
#     def __init__(self):
#         # Load environment variables
#         flag = load_dotenv()
#         logging.info(f"Environment variables loaded: {flag}")

#         # Initialize order handlers
#         self.Create_Order = PlaceOrder()
#         self.Update_Order = UpdateOrder()

#         # Kafka consumer configuration
#         self.config = {
#             'bootstrap.servers': 'localhost:9092',
#             'group.id': 'order_service_group',
#             'auto.offset.reset': 'earliest',
#             'enable.auto.commit': False,  # Commit offsets manually
#             # 'bootstrap.servers': 'localhost:9092',
#             # 'group.id': 'my-group',
#             # 'auto.offset.reset': 'earliest'
#         }

#         # Create Kafka consumer and subscribe to topics
#         self.consumer = Consumer(self.config)
#         self.consumer.subscribe(['Orders'])

#     def _process_message(self, message: Message):
#         """
#         Process a Kafka message.
#         """
#         try:
#             key = message.key().decode('utf-8')
#             data = message.value()  # Serialized Protobuf data

#             logging.info(f"Processing message with key: {key}")
            
#             # Debugging: Log raw data length and content (truncate if large)
#             logging.debug(f"Received data length: {len(data)}")
#             logging.debug(f"Raw data (truncated): {data[:100]}")

#             if key == "OrderPlaced":
#                 logging.info("Processing 'OrderPlaced' event.")
#                 self.Create_Order.create(data)

#             elif key == "OrderUpdate":
#                 logging.info("Processing 'OrderUpdate' event.")
#                 self.Update_Order.update(data)

#             else:
#                 logging.warning(f"Unknown event key: {key}")
#         except Exception as e:
#             logging.error(f"Error processing message with key {key}: {e}")
#             raise

#     def run(self):
#         """
#         Main Kafka consumer loop with batch processing.
#         """
#         try:
#             while True:
#                 msgs = self.consumer.consume(num_messages=10, timeout=1.0)  # Poll multiple messages
#                 for msg in msgs:
#                     if msg is None:
#                         continue
#                     if msg.error():
#                         logging.error(f"Kafka error: {msg.error()}")
#                         continue

#                     try:
#                         self._process_message(msg)
#                         self.consumer.commit(msg)  # Commit only if processing is successful
#                     except Exception as e:
#                         logging.error(f"Failed to process message: {e}")
#         except KeyboardInterrupt:
#             logging.info("Kafka consumer stopped by user.")
#         finally:
#             self.consumer.close()
#             logging.info("Kafka consumer closed.")

# def serve():
#     """
#     Entry point for starting the Kafka server.
#     """
#     server = KafkaServer()
#     server.run()

import sys
import os
import logging
import traceback
from confluent_kafka import Consumer, KafkaException, KafkaError
from google.protobuf.message import DecodeError
from dotenv import load_dotenv
import django
from django.db import transaction
from django.db import IntegrityError

# Set up Django
sys.path.append(os.getcwd() + r"\Orders\proto")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Orders.settings')
django.setup()
from Order.models import Order, OrderItem
from proto import Order_pb2

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("order_kafka_service.log"),
    ]
)



class PlaceOrder:
    def __init__(self):
        self.DeserializedOrder = Order_pb2.Order()

    @staticmethod
    @transaction.atomic
    def _proto_to_django_order(order_proto: Order_pb2.Order) -> Order:
        """
        Convert a Protobuf Order message to a Django Order instance, strictly for creation.
        """
        try:
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
            return order
        except IntegrityError as e:
            logger.error(f"IntegrityError while creating order: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while creating order: {e}")
            raise

    def create(self, data):
        """
        Create an order from serialized Protobuf data.
        """
        try:
            if not data:
                raise ValueError("Received empty data for order creation.")
            
            self.DeserializedOrder.ParseFromString(data)
            return self._proto_to_django_order(self.DeserializedOrder)
        except DecodeError as e:
            logger.error(f"Protobuf DecodeError: {e}. Data may be corrupted or invalid.")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in creating order: {e}")
            raise



class UpdateOrder:
    def __init__(self):
        self.DeserializedOrder = Order_pb2.Order()

    @staticmethod
    @transaction.atomic
    def proto_to_django_order(order_proto: Order_pb2.Order) -> Order:
        """
        Update an existing Django Order instance from a Protobuf Order message.
        """
        try:
            # Retrieve the existing Order instance
            order = Order.objects.get(OrderUuid=order_proto.OrderUuid)

            # Update fields of the Order
            order.StoreUuid = order_proto.StoreUuid
            order.UserPhoneNo = order_proto.UserPhoneNo
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
            order.save()

            # Update OrderItems associated with the Order
            for item_proto in order_proto.Items:
                # Update or create items associated with the order
                OrderItem.objects.update_or_create(
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
            return order
        except Order.DoesNotExist as e:
            logger.error(f"Order with OrderUuid {order_proto.OrderUuid} does not exist: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while updating order: {e}")
            raise

    def update(self, data):
        """
        Update an order from serialized Protobuf data.
        """
        try:
            if not data:
                raise ValueError("Received empty data for order update.")
            
            self.DeserializedOrder.ParseFromString(data)
            return self.proto_to_django_order(self.DeserializedOrder)
        except DecodeError as e:
            logger.error(f"Protobuf DecodeError: {e}. Data may be corrupted or invalid.")
            raise
        except Order.DoesNotExist as e:
            logger.error(f"Order does not exist for update: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in updating order: {e}")
            raise





class KafkaServer:
    def __init__(self):
        load_dotenv()
        self.consumer_config = {
            'bootstrap.servers': os.getenv('KAFKA_BROKERS',"kafka:9092"),
            'group.id': 'order_service_group',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False,  # Commit offsets manually
        }
        logger.info(f"Kafka Sever address {os.getenv('KAFKA_BROKERS', 'kafka:9092')}")

        self.consumer = Consumer(self.consumer_config)
        self.consumer.subscribe(['Orders'])
        self.place_order_handler = PlaceOrder()
        self.Update_order_handler = UpdateOrder()
        self.shutdown_flag = False

    def _process_message(self, message):
        try:
            key = message.key().decode('utf-8')
            data = message.value()
            logger.info(f"Processing message with key: {key}")

            if key == "OrderPlaced":
                self.place_order_handler.create(data)
                logger.info("Order placed successfully.")
            elif key == "OrderUpdate":
                self.Update_order_handler.update(data)
                logger.info("Order Updated successfully.")
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