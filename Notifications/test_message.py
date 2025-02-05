import os
import sys
import django
from django.core.exceptions import ValidationError

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notifications.settings')
django.setup()

from template.models import Template
from utils.logger import Logger
def convert_to_whatsapp_body(template_data, recipient_number=None):
    """
    Convert any template data into WhatsApp API message body format
    
    Args:
        template_data (dict): Template data containing name, components, etc.
        recipient_number (str, optional): Recipient's phone number
        
    Returns:
        dict: Formatted WhatsApp API message body
    """
    # Initialize the base structure
    whatsapp_body = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "type": "template",
        "template": {
            "name": template_data.get("name", ""),
            "language": {
                "code": "en"  # Default to English, can be made parameter if needed
            },
            "components": []
        }
    }
    
    # Add recipient number if provided
    if recipient_number:
        whatsapp_body["to"] = recipient_number

    # Process components
    for component in template_data.get("components", []):
        formatted_component = {}
        component_type = component.get("type", "").lower()
        
        # Handle BODY type
        if component_type == "body":
            formatted_component = {
                "type": "body",
                "parameters": []
            }
            
            # Extract parameters from example if available
            if "example" in component and "body_text_named_params" in component["example"]:
                for param in component["example"]["body_text_named_params"]:
                    formatted_component["parameters"].append({
                        "type": "text",
                        "text": f"{{{{ {param['param_name']} }}}}"
                    })
            
        # Handle BUTTONS type
        elif component_type == "buttons":
            for idx, button in enumerate(component.get("buttons", [])):
                if button.get("type") == "URL":
                    formatted_component = {
                        "type": "button",
                        "sub_type": "url",
                        "index": str(idx),
                        "parameters": [{
                            "type": "text",
                            "text": button.get("url", "")
                        }]
                    }
        
        # Add the formatted component if not empty
        if formatted_component:
            whatsapp_body["template"]["components"].append(formatted_component)
    
    return whatsapp_body

# Example usage
if __name__ == "__main__":
    # Your original template data
    template_data = Template.objects.get(name="delivery_update_1").to_whatsapp_format()
    
    # Convert to WhatsApp API format
    whatsapp_body = convert_to_whatsapp_body(
        template_data,
        recipient_number="1234567890"  # Optional
    )
    
    # Print the result
    import json
    print(json.dumps(whatsapp_body, indent=2))