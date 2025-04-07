from confluent_kafka import Consumer, KafkaException
import sys 
import os
import django
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Orders.settings')
django.setup()
from Proto.order_pb2 import KafkaOrderMessage, OrderState, OrderOpration, OrderPayment, PaymentState, PaymentMethod
from Proto import order_pb2



# Configure the consumer
conf = {
    'bootstrap.servers': 'localhost:29092',
    'group.id': 'order-service',
    'auto.offset.reset': 'earliest'
}

# Create the consumer instance
consumer = Consumer(conf)
consumer.subscribe(['Orders'])  # Subscribe to the topic
deserialized_order = KafkaOrderMessage()

try:
    while True:
        msg = consumer.poll(1.0)  # Poll for new messages

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaException._PARTITION_EOF:
                print(f"End of partition reached {msg.topic()} [{msg.partition()}]")
            else:
                print(f"Error: {msg.error()}")
            continue
        print(msg.value())
        deserialized_order.ParseFromString(msg.value())    
        print(deserialized_order)
        print(type(deserialized_order))


except KeyboardInterrupt:
    print("Consumer interrupted")
finally:
    consumer.close()  # Ensure consumer is closed on exit