import os
import sys
import django
from django.core.exceptions import ValidationError
from pathlib import Path
import json
import requests
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
    objects = Template.objects.get(name = "seasonal_promotion")
    template = objects.to_message_format() 
    print(json.dumps(template, indent=4))

def test_template_to_whatsapp_format(): 
    objects = Template.objects.all()
    for object in objects:
        template = object.to_whatsapp_format() 
        print(json.dumps(template, indent=4))

def test_sync_with_whatsapp():
    objects = Template.objects.sync_with_whatsapp()
    print(objects)

if __name__ == "__main__":
    # test_template_creation()
    # test_template_to_whatsapp_format()
    #test_whatsapp_sync()
    # test_template_creation()
    test_template_to_message_format()
    # test_sync_with_whatsapp()

