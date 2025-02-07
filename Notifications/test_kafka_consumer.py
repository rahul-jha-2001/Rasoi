import os
import sys
import django
import time
from confluent_kafka import Producer
from confluent_kafka.error import KafkaError

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notifications.settings')
django.setup()

from proto.Notifications_pb2 import NotificationMessage
from message_service.models import Message
from utils.logger import Logger

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = ['localhost:29092']
TEST_TOPIC = 'notifications'

def test_send_message():
    message = Message.objects.create(
        template_name="Test Template",
        to_address="test@example.com",
        from_address="sender@example.com",
        channel="EMAIL",
        variables={"name_key": "Test User"}
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

def test_send_single_message():
    """Test sending a single message to Kafka"""
    producer = create_kafka_producer()
    
    try:
        # Create and send test notification
        notification = create_test_notification()
        serialized_message = notification.SerializeToString()
        
        # Send message to Kafka
        producer.produce(TEST_TOPIC, serialized_message)
        producer.flush()
        print("\n✅ Test message sent to Kafka successfully!")
        print(f"Template: {notification.template_name}")
        print(f"To: {notification.to_address}")
        return True
            
    except Exception as e:
        print(f"\n❌ Message sending failed: {str(e)}")
        return False


def test_send_multiple_messages():
    """Test sending multiple messages to Kafka"""
    producer = create_kafka_producer()
    messages_count = 5

    names = ["John", "Jane", "Alice", "Bob", "Charlie"]
    try:
        # Send multiple test messages
        for i in range(messages_count):
            notification = create_test_notification()
            notification.to_address = f"test{i}@example.com"
            notification.variables["name"] = names[i]
            serialized_message = notification.SerializeToString()
            
            producer.produce(TEST_TOPIC, serialized_message)
        
        producer.flush()
        print(f"\n✅ Sent {messages_count} test messages to Kafka")
        return True
        
    except Exception as e:
        print(f"\n❌ Multiple messages sending failed: {str(e)}")
        return False

def test_send_invalid_message():
    """Test sending an invalid message to Kafka"""
    producer = create_kafka_producer()
    
    try:
        # Send invalid message
        invalid_message = b'invalid-protobuf-data'
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
        
        # Create template first
        create_test_template()
        
        tests = [
            ("Single Message", test_send_single_message()),
            #("Multiple Messages", test_send_multiple_messages()),
            #("Invalid Message", test_send_invalid_message())
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