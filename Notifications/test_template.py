import os
import sys
import django
from django.core.exceptions import ValidationError
from pathlib import Path
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notifications.settings')
django.setup()

from template.models import Template,Component,Button,Parameters
from utils.logger import Logger

def test_whatsapp_sync():
    try:
        print("\nStarting WhatsApp template sync...")
        synced_templates = Template.objects.sync_from_whatsapp()
        
        print(f"\nSuccessfully synced {len(synced_templates)} templates")
        
        for template in synced_templates:
            print(f"\nTemplate Details:")
            print(f"Name: {template.name}")
            print(f"Category: {template.category}")
            print(f"Status: {template.status}")
            print(f"Language: {template.language}")
            print(f"WhatsApp Template ID: {template.whatsapp_template_id}")
            
            print("\nComponents:")
            for component in template.components.all():
                print(f"\n- Type: {component.type}")
                print(f"  Format: {component.format}")
                print(f"  Text: {component.text}")
                
                # Print buttons if they exist
                if component.buttons.exists():
                    print("  Buttons:")
                    for button in component.buttons.all():
                        print(f"    * {button.type}: {button.text}")
                        if button.url:
                            print(f"      URL: {button.url}")
                        if button.phone_number:
                            print(f"      Phone: {button.phone_number}")
                
                # Print examples if they exist
                if hasattr(component, 'examples') and component.examples.exists():
                    example = component.examples.first()
                    print("  Examples:")
                    if example.body_text:
                        print(f"    * Body Text: {example.body_text}")
                    if example.body_text_named_params:
                        print(f"    * Named Params: {example.body_text_named_params}")
                    if example.button_url_example:
                        print(f"    * Button URL Example: {example.button_url_example}")
            
            print("\n" + "="*50)

    except Exception as e:
        print(f"\nError syncing templates: {str(e)}")
        raise

def test_template_creation():
    template_data =[
        {
            "name": "delivery_update_1",
            "message_send_ttl_seconds": 10800,
            "parameter_format": "NAMED",
            "components": [
                {
                    "type": "BODY",
                    "text": "{{user_name}}, your order is being prepared and should arrive soon. \n\nEstimated delivery is {{time_to_delivery}} minutes. \n\nWe will provide an update when your order is delivered.",
                    "example": {
                        "body_text_named_params": [
                            {
                                "param_name": "user_name",
                                "example": "Jhon Doe"
                            },
                            {
                                "param_name": "time_to_delivery",
                                "example": "30"
                            }
                        ]
                    }
                },
                {
                    "type": "BUTTONS",
                    "buttons": [
                        {
                            "type": "URL",
                            "text": "Track order",
                            "url": "https://www.example.com/{{1}}",
                            "example": [
                                "https://rasoi.io/storeId/order_id"
                            ]
                        }
                    ]
                }
            ],
            "language": "en_US",
            "status": "APPROVED",
            "category": "UTILITY",
            "id": "1124617022729569"
        },
        {
            "name": "delivery_update_2",
            "message_send_ttl_seconds": 10800,
            "parameter_format": "NAMED",
            "components": [
                {
                    "type": "BODY",
                    "text": "{{user_name}}, your order is being prepared and should arrive soon. \n\nEstimated delivery is {{time_to_delivery}} minutes. \n\nWe will provide an update when your order is delivered."
                }
            ],
            "language": "en_US",
            "status": "REJECTED",
            "category": "UTILITY",
            "id": "936711235302800"
        },
        {
            "name": "test_utility_template_1",
            "parameter_format": "NAMED",
            "components": [
                {
                    "type": "HEADER",
                    "format": "TEXT",
                    "text": "header with varibles {{test_1}}"
                },
                {
                    "type": "BODY",
                    "text": "Test Body with 2 variables {{test_1}} + {{test_2}}"
                },
                {
                    "type": "FOOTER",
                    "text": "header with varibles"
                },
                {
                    "type": "BUTTONS",
                    "buttons": [
                        {
                            "type": "QUICK_REPLY",
                            "text": "Unsubcribe"
                        },
                        {
                            "type": "URL",
                            "text": "Button witt url",
                            "url": "https://example.com/?field={{1}}"
                        }
                    ]
                }
            ],
            "language": "en",
            "status": "REJECTED",
            "category": "UTILITY",
            "id": "609270861966538"
        },
        {
            "name": "test_marketing_template_2",
            "parameter_format": "NAMED",
            "components": [
                {
                    "type": "HEADER",
                    "format": "TEXT",
                    "text": "header with varibles {{test_1}}"
                },
                {
                    "type": "BODY",
                    "text": "Test Body with 2 variables {{test_1}} + {{test_2}}"
                },
                {
                    "type": "FOOTER",
                    "text": "header with varibles"
                },
                {
                    "type": "BUTTONS",
                    "buttons": [
                        {
                            "type": "QUICK_REPLY",
                            "text": "Unsubcribe"
                        },
                        {
                            "type": "URL",
                            "text": "Button witt url",
                            "url": "https://example.com/?field={{1}}"
                        }
                    ]
                }
            ],
            "language": "en",
            "status": "REJECTED",
            "category": "MARKETING",
            "id": "2397232717279548"
        },
        {
            "name": "delivery_confirmation_1",
            "message_send_ttl_seconds": 3600,
            "parameter_format": "NAMED",
            "components": [
                {
                    "type": "HEADER",
                    "format": "TEXT",
                    "text": "Order Placed"
                },
                {
                    "type": "BODY",
                    "text": "{{user_name}}, your order was successfully placed! \n\nYou can track your order and manage your order below.",
                    "example": {
                        "body_text_named_params": [
                            {
                                "param_name": "user_name",
                                "example": "Rahul"
                            }
                        ]
                    }
                },
                {
                    "type": "BUTTONS",
                    "buttons": [
                        {
                            "type": "URL",
                            "text": "Manage order",
                            "url": "https://rasoi.onilne/?order_id={{1}}",
                            "example": [
                                "https://rasoi.onilne/?order_id=%7B%7B1%7D"
                            ]
                        }
                    ]
                }
            ],
            "language": "en_US",
            "status": "PENDING",
            "category": "UTILITY",
            "id": "1124638896002332"
        },
        {
            "name": "delivery_confirmation_2",
            "parameter_format": "POSITIONAL",
            "components": [
                {
                    "type": "HEADER",
                    "format": "TEXT",
                    "text": "Order Placed"
                },
                {
                    "type": "BODY",
                    "text": "{{1}}, your order was successfully placed! \n\nYou can track your order and manage your order below."
                },
                {
                    "type": "BUTTONS",
                    "buttons": [
                        {
                            "type": "URL",
                            "text": "Manage order",
                            "url": "https://www.example.com/"
                        }
                    ]
                }
            ],
            "language": "en_US",
            "status": "APPROVED",
            "category": "UTILITY",
            "id": "1639594023429631"
        },
        {
            "name": "seasonal_promotion",
            "parameter_format": "POSITIONAL",
            "components": [
                {
                    "type": "HEADER",
                    "format": "TEXT",
                    "text": "Our {{1}} is on!",
                    "example": {
                        "header_text": [
                            "Summer Sale"
                        ]
                    }
                },
                {
                    "type": "BODY",
                    "text": "Shop now through {{1}} and use code {{2}} to get {{3}} off of all merchandise.",
                    "example": {
                        "body_text": [
                            [
                                "the end of August",
                                "25OFF",
                                "25%"
                            ]
                        ]
                    }
                },
                {
                    "type": "FOOTER",
                    "text": "Use the buttons below to manage your marketing subscriptions"
                },
                {
                    "type": "BUTTONS",
                    "buttons": [
                        {
                            "type": "QUICK_REPLY",
                            "text": "Unsubcribe from Promos"
                        },
                        {
                            "type": "QUICK_REPLY",
                            "text": "Unsubscribe from All"
                        }
                    ]
                }
            ],
            "language": "en",
            "status": "APPROVED",
            "category": "MARKETING",
            "id": "625268136668489"
        },
        {
            "name": "one_time_password",
            "message_send_ttl_seconds": 300,
            "parameter_format": "POSITIONAL",
            "components": [
                {
                    "type": "BODY",
                    "text": "*{{1}}* is your verification code. For your security, do not share this code.",
                    "add_security_recommendation": True,
                    "example": {
                        "body_text": [
                            [
                                "123456"
                            ]
                        ]
                    }
                },
                {
                    "type": "FOOTER",
                    "text": "This code expires in 5 minutes.",
                    "code_expiration_minutes": 5
                },
                {
                    "type": "BUTTONS",
                    "buttons": [
                        {
                            "type": "URL",
                            "text": "Copy code",
                            "url": "https://www.whatsapp.com/otp/code/?otp_type=COPY_CODE&code_expiration_minutes=5&code=otp{{1}}",
                            "example": [
                                "https://www.whatsapp.com/otp/code/?otp_type=COPY_CODE&code_expiration_minutes=5&code=otp123456"
                            ]
                        }
                    ]
                }
            ],
            "language": "en",
            "status": "APPROVED",
            "category": "AUTHENTICATION",
            "id": "2098153577272618"
        },
        {
            "name": "order_pick_up_1",
            "parameter_format": "NAMED",
            "components": [
                {
                    "type": "HEADER",
                    "format": "TEXT",
                    "text": "Ready for pick up!"
                },
                {
                    "type": "BODY",
                    "text": "{{user_name}}, your order is ready for pick up at {{store_name}} take it from the counter.\n\nThank you for ordering.",
                    "example": {
                        "body_text_named_params": [
                            {
                                "param_name": "user_name",
                                "example": "Rahul"
                            },
                            {
                                "param_name": "store_name",
                                "example": "Rasoi"
                            }
                        ]
                    }
                }
            ],
            "language": "en_US",
            "status": "APPROVED",
            "category": "UTILITY",
            "id": "994382215847012"
        },
        {
            "name": "hello_world",
            "parameter_format": "POSITIONAL",
            "components": [
                {
                    "type": "HEADER",
                    "format": "TEXT",
                    "text": "Hello World"
                },
                {
                    "type": "BODY",
                    "text": "Welcome and congratulations!! This message demonstrates your ability to send a WhatsApp message notification from the Cloud API, hosted by Meta. Thank you for taking the time to test with us."
                },
                {
                    "type": "FOOTER",
                    "text": "WhatsApp Business Platform sample message"
                }
            ],
            "language": "en_US",
            "status": "APPROVED",
            "category": "UTILITY",
            "id": "554585010880536"
        }
    ]
    try:
        for template_data in template_data:
            template = Template.objects.create_template_with_json(
                template_data
            )
            print(f"Template created successfully: {template.name}")
    except Exception as e:
        print(f"Error creating template: {str(e)}")
        raise

def test_template_to_message_format():
    objects = Template.objects.all()
    for object in objects:
        template = object.to_message_format() 
        print(json.dumps(template, indent=4))

def test_template_to_whatsapp_format(): 
    objects = Template.objects.all()
    for object in objects:
        template = object.to_whatsapp_format() 
        print(json.dumps(template, indent=4))

if __name__ == "__main__":
    # test_template_creation()
    # test_template_to_whatsapp_format()
    #test_whatsapp_sync()
    # test_template_creation()
    test_template_to_message_format()

