import os
import django
from django.apps import apps
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notifications.settings')
django.setup()

from confluent_kafka import Consumer, KafkaError
from proto.Notifications_pb2 import NotificationMessage,Channel
from typing import Optional
from utils.logger import Logger

from contextlib import contextmanager
from tenacity import retry, stop_after_attempt, wait_exponential
from google.protobuf.message import DecodeError

from message_service.models import Message
from template.models import Template, TemplateVersion, TemplateContent

logger = Logger("KafkaConsumer")
class NotificationKafkaConsumer:
    """
    Kafka consumer for notification messages.
    Handles message deserialization and delegation to Celery tasks.
    """
    
    def __init__(
        self,
        bootstrap_servers: list[str],
        topic: str = 'notifications',
        group_id: str = 'notification_processor',
        auto_offset_reset: str = 'earliest'
    ):
        self.topic = topic
        self.consumer = self._create_consumer(
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset=auto_offset_reset
        )
        self._running = False
        
        # Get Django models
        self.Message = Message
        self.Template = Template
        self.TemplateVersion = TemplateVersion
    
    def _create_consumer(self, **kwargs) -> Consumer:
        """Creates and configures the Kafka consumer"""
        try:
            config = {
                'bootstrap.servers': ','.join(kwargs['bootstrap_servers']),
                'group.id': kwargs['group_id'],
                'auto.offset.reset': kwargs['auto_offset_reset'],
                'enable.auto.commit': True
            }
            
            consumer = Consumer(config)
            consumer.subscribe([self.topic])
            return consumer
        
        except KafkaError as e:
            logger.error(f"Failed to create Kafka consumer: {str(e)}")
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
    def _create_message_record(self, notification: NotificationMessage) -> Optional[str]:
        """Creates a message record in the database"""
        try:
            # Create and validate the message
            message_id, error = self.Message.objects.create_from_notification(notification)

            if error:
                logger.error(f"Failed to create message: {error}")
                return None

            return message_id
        except Exception as e:
            logger.error(f"Error creating message record: {str(e)}")
            return None

    def _render_template(self, template_version, variables: dict) -> str:
        """Renders the template with the provided variables"""
        return self.Message.objects.render_message(template_version, variables)

    def _process_message(self, notification: NotificationMessage) -> bool:
        """
        Processes a single notification message
        Returns True if processing was successful
        """
        try:
            # Create message record
            message_id = self._create_message_record(notification)
            if not message_id:
                logger.error(f"Failed to create message record for notification: {notification}")
                return False
            else:
                logger.info(f"Message record created successfully for notification: {message_id}")
                return True

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return False

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

    def start_consuming(self):
        """
        Main method to start consuming messages
        """
        logger.info(f"Starting to consume messages from topic: {self.topic}")
        self._running = True

        with self._consumer_context():
            while self._running:
                try:
                    # Get message batch
                    message_batch = self.consumer.consume(num_messages=10, timeout=1.0)
                    
                    if not message_batch:
                        continue

                    # Process messages
                    for msg in message_batch:
                        if msg is None:
                            continue
                        if msg.error():
                            logger.error(f"Kafka error: {msg.error()}")
                            continue

                        logger.debug(f"Processing message from partition {msg.partition()}")
                        
                        # Deserialize message
                        notification = self._deserialize_message(msg.value())
                        if not notification:
                                continue

                        # Process message
                        success = self._process_message(notification)
                        if success:
                            logger.info(
                                f"Successfully processed notification for template: "
                                f"{notification.template_name}"
                            )
                        else:
                            logger.error(
                                f"Failed to process notification for template: "
                                f"{notification.template_name}"
                            )

                except Exception as e:
                    logger.error(f"Unexpected error in consumer loop: {str(e)}")
                    # Consider implementing a circuit breaker here

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

