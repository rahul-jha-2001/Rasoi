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

def test_update_template_with_json():
    objects = Template.objects.get(name="seasonal_promotion")
    objects = Template.objects.update_template_with_json(objects.to_whatsapp_format())
    print(objects)

def test_template_render():
    template = Template.objects.get(name="seasonal_promotion")
    template_format = template.to_message_format()
    
    # Example values to replace the placeholders
    values = {
        "HEADER_0": "Special Season Sale! 🎉",
        "BODY_0": "Get amazing discounts",
        "BODY_1": "up to 50% off",
        "BODY_2": "on selected items",
        "button_0": "Shop Now",
        "button_1": "View Catalog"
    }
    
    # Render the template
    rendered_template = render_template(template_format, values)
    print("\nRendered Message Format:")
    print_formatted_message(rendered_template)

def render_template(template, values):
    rendered = json.loads(json.dumps(template))  # Create a deep copy
    
    for component in rendered['components']:
        if 'parameters' in component:
            for param in component['parameters']:
                if param['type'].upper() == 'TEXT':
                    placeholder = param['text']
                    if placeholder.startswith('{{') and placeholder.endswith('}}'):
                        key = placeholder[2:-2]  # Remove {{ and }}
                        if key in values:
                            param['text'] = values[key]
    print(json.dumps(rendered, indent=4))
    return rendered

def print_formatted_message(template):
    formatted_message = {
        'header': '',
        'body': '',
        'buttons': []
    }
    
    for component in template['components']:
        if component['type'] == 'HEADER':
            if 'parameters' in component:
                formatted_message['header'] = component['parameters'][0]['text']
        
        elif component['type'] == 'BODY':
            if 'parameters' in component:
                body_texts = [param['text'] for param in component['parameters'] if param['type'] == 'TEXT']
                formatted_message['body'] = ' '.join(body_texts)
        
        elif component['type'] == 'button':
            if formatted_message["buttons"] == []:
                formatted_message['buttons'] =  [Parameter["text"] for Parameter in component["parameters"]]
            else:
                formatted_message['buttons'] = formatted_message['buttons'] + [Parameter["text"] for Parameter in component["parameters"]]
    
    # Print the formatted message
    print(f"Header: {formatted_message['header']}")
    print(f"Body: {formatted_message['body']}")
    print(f"Buttons: {formatted_message['buttons']}")

if __name__ == "__main__":
    # test_update_template_with_json()
    # test_template_creation()
    # test_template_to_whatsapp_format()
    #test_whatsapp_sync()
    # test_template_creation()
    test_template_render()
    # test_sync_with_whatsapp()

