from confluent_kafka import Consumer, KafkaException
import json
import sys 
import os

sys.path.append(os.getcwd()+r"\Orders\proto")
print(sys.path)
from proto import Order_pb2,Order_pb2_grpc


# Configure the consumer
conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-group',
    'auto.offset.reset': 'earliest'
}

# Create the consumer instance
consumer = Consumer(conf)
consumer.subscribe(['Orders'])  # Subscribe to the topic
deserialized_order = Order_pb2.Order()

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
        print(deserialized_order.Items[0])
        print(type(deserialized_order.Items[0]))


except KeyboardInterrupt:
    print("Consumer interrupted")
finally:
    consumer.close()  # Ensure consumer is closed on exit