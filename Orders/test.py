from confluent_kafka import Producer
import json


import sys 
import os

sys.path.append(os.getcwd()+r"\Orders\proto")
from proto import Order_pb2,Order_pb2_grpc
# Configure the producer
conf = {
    'bootstrap.servers': 'localhost:29092',  # Adjust to your Kafka server settings
    'client.id': 'python-producer'
}


# Create items
item1 = Order_pb2.OrderItem(
    ProductUuid="987e6543-e21b-43d1-a432-123456789fed",
    Price=20.0,
    Quantity=2,
    Discount=10.0,
    SubTotal=40.0,
    TaxedAmount=42.0,
    DiscountAmount=4.0
)

item2 = Order_pb2.OrderItem(
    ProductUuid="876e5432-d12c-45e6-b234-567890fedcba",
    Price=15.0,
    Quantity=1,
    Discount=5.0,
    SubTotal=15.0,
    TaxedAmount=15.75,
    DiscountAmount=0.75
)

# Create order
order = Order_pb2.Order(
    OrderUuid="183e4567-e89b-12d3-a456-426614274000",
    StoreUuid="456e7890-e12b-34d5-b678-123456789abc",
    UserPhoneNo="+1234567890",
    OrderType="ORDER_TYPE_DINE_IN",
    TableNo="20A",
    CouponName="WELCOME50",
    Items=[item1, item2],
    TotalAmount=57.0,
    DiscountAmount=4.75,
    FinalAmount=52.25,
    PaymentState="PAYMENT_STATE_PENDING",
    PaymentMethod="CASH",
    SpecialInstruction="Extra x spicy",
    OrderStatus="ORDER_STATE_PLACED"
)

# Serialize to binary
serialized_data = order.SerializeToString()

# Create the producer instance
producer = Producer(conf)


# Delivery callback to check if the message was sent successfully
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# Produce a message
topic = 'Orders'
producer.produce(topic, key="OrderPlaced", value=serialized_data, callback=delivery_report )
producer.flush()  # Ensure all messages are sent