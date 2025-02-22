import os
import sys
import django
import time
from confluent_kafka import Producer
from confluent_kafka.error import KafkaError

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notifications.settings')
django.setup()
import proto.Messages_pb2 as message_pb2
from proto.Messages_pb2 import MessageEvent,Recipient,Variables,MetaData
from message_service.models import Message
from utils.logger import Logger
from datetime import datetime

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = ['localhost:29092']
TEST_TOPIC = 'notifications'


Invalid_message = MessageEvent(
    template_name="seasonal_promotion",
    recipient=Recipient(
        to_number="+919876543210",
        from_number="+919876543210",
    ),
    variables=Variables(
        variables={"HEADER_1": "Test User",
                    "BODY_0": "Test User_1",
                    "BODY_1": "Test User_2",
                    "BODY_2": "Test User_3",
                    "BUTTONS_0": "Test User_button_1",
                    }
    )
)

message = MessageEvent(
    template_name="one_time_password",
    recipient=Recipient(
        to_number="+919977636633",
        from_number="+919876543210",
    ),
    variables=Variables(variables = {
                    "BODY_1": "997",
                    "BUTTON_0": "997"
    }
    )
)



def create_kafka_producer():
    """Create a Kafka producer for testing"""
    try:
        config = {
            'bootstrap.servers': ','.join(KAFKA_BOOTSTRAP_SERVERS),
        }
        return Producer(config)
    except KafkaError as e:
        print(f"\n❌ Failed to create Kafka producer: {str(e)}")
        raise

def test_send_valid_message():
    """Test sending a single message to Kafka"""
    producer = create_kafka_producer()
    
    try:
        # Create and send test notification
        serialized_message = message.SerializeToString()
    
        # Send message to Kafka
        producer.produce(TEST_TOPIC, serialized_message)
        producer.flush()

        print("\n✅ Test message sent to Kafka successfully!")
        print(f"Template: {message.template_name}")
        print(f"To: {message.recipient.to_number}")
        return True
            
    except Exception as e:
        print(f"\n❌ Message sending failed: {str(e)}")
        raise e

def test_send_invalid_message():
    """Test sending an invalid message to Kafka"""
    producer = create_kafka_producer()  
    try:
        # Send invalid message
        invalid_message = Invalid_message.SerializeToString()
        producer.produce(TEST_TOPIC, invalid_message)
        producer.flush()
        
        print("\n✅ Invalid message sent to Kafka")
        return True
        
    except Exception as e:
        print(f"\n❌ Invalid message sending failed: {str(e)}")
        return False

def run_all_tests():
    """Run all test cases"""
    try:
        print("\n🏃 Running Kafka producer tests...")
        tests = [
            ("Valid Message", test_send_valid_message()),
            ("Invalid Message", test_send_invalid_message())
        ]
        
        print("\n📊 Test Results:")
        for test_name, result in tests:
            print(f"{test_name}: {'✅ PASSED' if result else '❌ FAILED'}")
        
    except Exception as e:
        print(f"\n❌ Error during tests: {str(e)}")
        raise

if __name__ == "__main__":
    print("\n📝 Note: Make sure Kafka is running on localhost:9092")
    print("Running producer tests - messages will be sent to 'notifications' topic")
    run_all_tests() 