import os
import sys
import django
from django.core.exceptions import ValidationError
from pathlib import Path


# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notifications.settings')
django.setup()

from template.models import Template, TemplateVersion, TemplateContent
from utils.logger import Logger


def create_template():
    # Create a complete template
    template = Template.objects.create_new_template(
        name="Welcome Email",
        description="Welcome email for new users",
        channel="EMAIL",
        category="AUTHENTICATION",
        header="Welcome {{user_name}}!",
        body="Thank you for joining.",
        footer="Best regards",
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

def create_new_version(template_id) -> Template:
    # Create a complete template
    template = Template.objects.create_new_version(
        template_id=template_id,
        channel="SMS",
        header="Welcome {{user_name}}!",
        body="Thank you for joining.",
        footer="Best regards",
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
    except ValidationError as e:
        template = Template.objects.all()[0]
    except Exception as e:
        print(f"\nError creating template: {str(e)}")
    try:
        new_version = create_new_version(template.id)
        print(f"\nNew Version: {new_version}")
    except Exception as e:
        print(f"\nError creating new version: {str(e)}")
        raise
    try:
        template_versions = TemplateVersion.objects.all()
        print(f"\nTemplate Versions: {template_versions}")
        for version in template_versions:
            print(f"Version {version.version_number} of template {version.template.name} ({version.channel})")
            content = TemplateContent.objects.get(template_version=version)
            print(f"Content: Header={content.header}, Body={content.body}, Footer={content.footer}")
    except Exception as e:
        print(f"\nError getting templates: {str(e)}")
        raise

if __name__ == "__main__":
    test_template()
