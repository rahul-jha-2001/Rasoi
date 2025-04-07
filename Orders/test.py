from confluent_kafka import Producer
import json


import sys 
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Orders.settings')
django.setup()
from Proto.order_pb2 import KafkaOrderMessage, OrderState, OrderOpration, OrderPayment, PaymentState, PaymentMethod
from Proto import order_pb2

import time
from datetime import datetime

# Configure the producer
conf = {
    'bootstrap.servers': 'localhost:29092',  # Adjust to your Kafka server settings
    'client.id': 'payment-service'
}


payment=OrderPayment(
        payment_uuid="0c3bf0fd-adf6-4c64-a7f9-46263173ad86",
        rz_order_id= "Order_4545",
        rz_payment_id= "Payment_5454",
        rz_signature= "sadasda",
        amount=700,
        payment_method= PaymentMethod.PAYMENT_METHOD_RAZORPAY,
        payment_status= PaymentState.PAYMENT_STATE_COMPLETE,
        payment_time= datetime.utcnow()
    )

message = order_pb2.KafkaOrderMessage(
    cart_uuid="1b920999-cbf2-4a0d-a730-c7396c1caa31",
    store_uuid = "9c0a689e-c1f4-4bcd-b64a-29d1861db326",
    payment= payment,
    operation=OrderOpration.ORDER_OP_CREATE
)
# Serialize to binary
serialized_data = message.SerializeToString()

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



