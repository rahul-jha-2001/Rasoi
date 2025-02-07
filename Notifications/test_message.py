import os
import sys
import django
from django.core.exceptions import ValidationError

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notifications.settings')
django.setup()

from message_service.models import Message
from template.models import Template
from utils.logger import Logger


def test_message_create():
    template = Template.objects.get(name="seasonal_promotion")
    message = Message.objects.create_message(template_name=template.name,
                                            variables={"HEADER_0": "Header_0_text",
                                                       "BODY_0": "Body_0_text",
                                                       "BODY_1": "Body_1_text",
                                                       "BODY_2": "Body_2_text",
                                                       "BODY_3": "Body_3_text",
                                                       "FOOTER_0": "Footer_0_text",
                                                       "BUTTON_0": "Button_0_text",
                                                       "BUTTON_1": "Button_1_text"
                                                       },
                                            to_phone_number="+1234567890",
                                            from_phone_number="+1234567890")
    print(message)
    invalid_message = Message.objects.create_message(template_name=template.name,
                                            variables={
                                                       "BODY_0": "Body_0_text",
                                                       "BODY_1": "Body_1_text",
                                                       "BODY_2": "Body_2_text",
                                                       "BODY_3": "Body_3_text",
                                                       "FOOTER_0": "Footer_0_text",
                                                       "BUTTON_0": "Button_0_text",
                                                       "BUTTON_1": "Button_1_text"
                                                       },
                                            to_phone_number="+1234567890",
                                            from_phone_number="+1234567890")
test_message_create()