import os
import django
from django.apps import apps
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notifications.settings')
django.setup()

from confluent_kafka import Consumer, KafkaError
from proto.Notifications_pb2 import NotificationMessage
from typing import Optional, List
from utils.logger import Logger

from contextlib import contextmanager
from tenacity import retry, stop_after_attempt, wait_exponential
from google.protobuf.message import DecodeError

from message_service.models import Message
from template.models import Template
from dataclasses import dataclass

logger = Logger("KafkaConsumer")

@dataclass
class ConsumerConfig:
    """Configuration for the Kafka consumer"""
    bootstrap_servers: List[str]
    topic: str
    group_id: str
    auto_offset_reset: str
    batch_size: int = 10
    max_poll_interval_ms: int = 300000

class NotificationKafkaConsumer:
    """
    Kafka consumer for notification messages.
    Handles message deserialization and delegation to Celery tasks.
    
    Args:
        config (ConsumerConfig): Configuration for the consumer
    """
    
    def __init__(
        self,
        bootstrap_servers: list[str],
        topic: str = 'notifications',
        group_id: str = 'notification_processor',
        auto_offset_reset: str = 'earliest',
        batch_size: int = 10
    ):
        self.config = ConsumerConfig(
            bootstrap_servers=bootstrap_servers,
            topic=topic,
            group_id=group_id,
            auto_offset_reset=auto_offset_reset,
            batch_size=batch_size
        )
        self._validate_config()
        
        self.topic = topic
        self.consumer = self._create_consumer()
        self._running = False
        self._health_status = True
        
        # Get Django models
        self.Message = Message
        self.Template = Template
    
    def _validate_config(self) -> None:
        """Validates the consumer configuration"""
        if not self.config.bootstrap_servers:
            raise ValueError("Bootstrap servers cannot be empty")
        if not self.config.topic:
            raise ValueError("Topic cannot be empty")
        if not self.config.group_id:
            raise ValueError("Group ID cannot be empty")

    def _create_consumer(self) -> Consumer:
        """Creates and configures the Kafka consumer"""
        try:
            config = {
                'bootstrap.servers': ','.join(self.config.bootstrap_servers),
                'group.id': self.config.group_id,
                'auto.offset.reset': self.config.auto_offset_reset,
                'enable.auto.commit': True,
                'max.poll.interval.ms': self.config.max_poll_interval_ms
            }
            
            consumer = Consumer(config)
            consumer.subscribe([self.topic])
            return consumer
        
        except KafkaError as e:
            logger.error(f"Failed to create Kafka consumer: {str(e)}")
            self._health_status = False
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _deserialize_message(self, raw_message: bytes) -> Optional[NotificationMessage]:
        """
        Deserializes a protobuf message with retry logic
        """
        try:
            notification = NotificationMessage()
            notification.ParseFromString(raw_message)
            return notification
        except DecodeError as e:
            logger.error(f"Failed to deserialize message: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during deserialization: {str(e)}")
            return None

    @transaction.atomic
    def _create_message_record(self, notification: NotificationMessage) -> Optional[Message]:
        """Creates a message record in the database"""
        try:
            template_name = notification.template_name
            variables = dict(notification.variables.variables)
            to_phone_number = notification.recipient.to_number
            from_phone_number = notification.recipient.from_number
            # Create and validate the message
            message = self.Message.objects.create_message(template_name, variables, to_phone_number, from_phone_number)
            logger.info(f"MessageId:{message.id} record created successfully for Message Request id: {notification.meta_data.request_id}")

            return message
        except Exception as e:
            logger.error(f"Error creating message record: {str(e)}")
            return None

    def _process_message(self, notification: NotificationMessage) -> Optional[Message]:
        """
        Processes a single notification message
        
        Args:
            notification (NotificationMessage): The notification to process
            
        Returns:
            Message: The message record created
        """
        try:
            message = self._create_message_record(notification)
            if not message:
                logger.error(f"Failed to create message record for Message Request id: {notification.meta_data.request_id}")
                return None
            
            logger.info(f"MessageId:{message.id} record created successfully for Message Request id: {notification.meta_data.request_id}")
            return message

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return None

    @contextmanager
    def _consumer_context(self):
        """Context manager for handling consumer lifecycle"""
        try:
            yield
        except KafkaError as e:
            logger.error(f"Kafka error: {str(e)}")
            raise
        finally:
            self._running = False
            try:
                self.consumer.close()
            except Exception as e:
                logger.error(f"Error closing consumer: {str(e)}")

    @property
    def is_healthy(self) -> bool:
        """Returns the health status of the consumer"""
        return self._health_status

    def start_consuming(self):
        """Main method to start consuming messages"""
        logger.info(f"Starting to consume messages from topic: {self.topic}")
        self._running = True
        consecutive_errors = 0
        MAX_CONSECUTIVE_ERRORS = 3

        with self._consumer_context():
            while self._running:
                try:
                    # Get message batch
                    message_batch = self.consumer.consume(
                        num_messages=self.config.batch_size, 
                        timeout=1.0
                    )
                    
                    if not message_batch:
                        continue

                    consecutive_errors = 0  # Reset error counter on successful poll
                    self._health_status = True

                    # Process messages
                    for msg in message_batch:
                        if msg is None or msg.error():
                            logger.error(f"Kafka error: {msg.error() if msg else 'Empty message'}")
                            continue

                        logger.debug(f"Processing message from partition {msg.partition()}")
                        
                        notification = self._deserialize_message(msg.value())
                        if not notification:
                            continue

                        Message = self._process_message(notification)
                        if Message:
                            logger.info(f"Successfully processed MessageId:{Message.id} for Message Request id: {notification.meta_data.request_id}")
                        else:
                            logger.error(f"Failed to process MessageId:{Message.id} for Message Request id: {notification.meta_data.request_id}")

                except Exception as e:
                    logger.error(f"Unexpected error in consumer loop: {str(e)}")
                    consecutive_errors += 1
                    if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                        logger.critical("Circuit breaker triggered - too many consecutive errors")
                        self._health_status = False
                        self.stop_consuming()

    def stop_consuming(self):
        """
        Gracefully stop the consumer
        """
        logger.info("Stopping consumer...")
        self._running = False

if __name__ == "__main__":
    
    # Create and start consumer
    consumer = NotificationKafkaConsumer(
        bootstrap_servers=['localhost:29092'],
        topic='notifications',
        group_id='notification_processor'
    )
    
    try:
        logger.info("Starting consumer")
        consumer.start_consuming()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        consumer.stop_consuming()

