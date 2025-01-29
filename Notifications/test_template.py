import os
import sys
import django
from pathlib import Path
import logging

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notifications.settings')
django.setup()

from template.models import Template, TemplateVersion, TemplateContent

def create_template():
    # Create a complete template
    template = Template.objects.create_template_with_version_and_content(
        name="Welcome Email",
        description="Welcome email for new users",
        template_type="EMAIL",
        content={
            "header": "Welcome {{user_name}}!",
            "body": "Thank you for joining.",
            "footer": "Best regards"
        },
        variables=[
            {
                "name": "user_name",
                "description": "User's full name",
                "type": "STRING",
                "required": True
            }
        ],
        status='DRAFT'  # Added status parameter
    )
    return template

def test_template():
    try:
        template = create_template()
        print("\nTemplate created successfully!")
        print(f"Template: {template}")
        print(f"Template Versions: {TemplateVersion.objects.filter(template=template)}")
        print(f"Template Content: {TemplateContent.objects.filter(template_version__template=template)}")
    except Exception as e:
        print(f"\nError creating template: {str(e)}")
        raise


if __name__ == "__main__":
    test_template()
