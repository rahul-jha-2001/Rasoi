import os
import sys
import django
import time
from confluent_kafka import Producer
from confluent_kafka.error import KafkaError

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notifications.settings')
django.setup()

from proto.Notifications_pb2 import NotificationMessage,recipient,Variables,MetaData
from message_service.models import Message
from utils.logger import Logger
from datetime import datetime

Invalid_message = NotificationMessage(
    template_name="seasonal_promotion",
    recipient=recipient(
        to_number="+919876543210",
        from_number="+919876543210",
    ),
    variables=Variables(
        variables={"HEADER_0": "Test User",
                    "BODY_0": "Test User_1",
                    "BODY_1": "Test User_2",
                    "BODY_2": "Test User_3",
                    "BUTTONS_0": "Test User_button_1",
                    }
    ),
    meta_data=MetaData(
        request_id="1234567890",
        source_service="Test Service",
        created_at=datetime.now()
    )
)
# print(Invalid_message)
message = NotificationMessage(
    template_name="seasonal_promotion",
    recipient=recipient(
        to_number="+919876543210",
        from_number="+919876543210",
    ),
    variables=Variables(
        variables={"HEADER_0": "Test User",
                    "BODY_0": "Test User_1",
                    "BODY_1": "Test User_2",
                    "BODY_2": "Test User_3",
                    "BUTTONS_0": "Test User_button_1",
                    "BUTTONS_1": "Test User_button_2",
                    }
    ),
    meta_data=MetaData(
        request_id="1234567890",
        source_service="Test Service",
        created_at=datetime.now()
    )
)
print(message.SerializeToString())
print(dict(message.variables.variables))