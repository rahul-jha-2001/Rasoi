import os
import sys
import django
from django.core.exceptions import ValidationError

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Notifications.settings')
django.setup()

from message_service.models import Message
from template.models import Template, TemplateVersion
from utils.logger import Logger

def create_test_template():
    """Helper function to create test template and version"""
    template = Template.objects.first()
    if not template:
        template = Template.objects.create(
            name="Test Template",
            description="Test template for messages"
        )
    
    template_version = TemplateVersion.objects.filter(template=template).first()
    if not template_version:
        template_version = TemplateVersion.objects.create(
            template=template,
            version_number=1
        )
    return template, template_version

def test_valid_email_message():
    """Test creating a valid email message"""
    template, template_version = create_test_template()
    
    message = Message(
        channel=Message.Channel.EMAIL,
        status=Message.Status.PENDING,
        message_content="Hello {{user_name}}, welcome to our platform!",
        to_address="recipient@example.com",
        from_address="sender@example.com",
        template=template,
        template_version=template_version
    )
    
    if message.is_valid():
        message.save()
        print("\n✅ Valid email message created successfully!")
        print(f"Message ID: {message.message_id}")
        print(f"Content: {message.message_content}")
        return True
    else:
        print("\n❌ Email message validation failed")
        return False

def test_invalid_email_message():
    """Test creating an invalid email message"""
    template, template_version = create_test_template()
    
    message = Message(
        channel=Message.Channel.EMAIL,
        status=Message.Status.PENDING,
        message_content="Hello {{user_name}}, welcome to our platform!",
        to_address="invalid-email",  # Invalid email format
        from_address="sender@example.com",
        template=template,
        template_version=template_version
    )
    
    if not message.is_valid():
        print("\n✅ Invalid email correctly detected")
        return True
    else:
        print("\n❌ Validation failed to catch invalid email")
        return False

def test_valid_sms_message():
    """Test creating a valid SMS message"""
    template, template_version = create_test_template()
    
    message = Message(
        channel=Message.Channel.SMS,
        status=Message.Status.PENDING,
        message_content="Welcome to our platform!",  # Short message for SMS
        to_address="+12345678901",
        from_address="+19876543210",
        template=template,
        template_version=template_version
    )
    
    if message.is_valid():
        message.save()
        print("\n✅ Valid SMS message created successfully!")
        print(f"Message ID: {message.message_id}")
        print(f"Content: {message.message_content}")
        return True
    else:
        print("\n❌ SMS message validation failed")
        return False

def test_invalid_sms_message():
    """Test creating an invalid SMS message"""
    template, template_version = create_test_template()
    
    message = Message(
        channel=Message.Channel.SMS,
        status=Message.Status.PENDING,
        message_content="This is a very long SMS message that exceeds the 160 character limit. It should fail validation because SMS messages need to be concise and within the standard SMS length restrictions.",
        to_address="invalid-phone",  # Invalid phone format
        from_address="+19876543210",
        template=template,
        template_version=template_version
    )
    
    if not message.is_valid():
        print("\n✅ Invalid SMS correctly detected")
        return True
    else:
        print("\n❌ Validation failed to catch invalid SMS")
        return False

def display_all_messages():
    """Display all messages in the database"""
    try:
        messages = Message.objects.all()
        print("\nAll Messages:")
        for msg in messages:
            print(f"\nMessage ID: {msg.message_id}")
            print(f"Channel: {msg.channel}")
            print(f"Status: {msg.status}")
            print(f"To: {msg.to_address}")
            print(f"From: {msg.from_address}")
            print(f"message_content: {msg.message_content}")
            print(f"Template: {msg.template.name}")
            print(f"Template Version: {msg.template_version.version_number}")
    except Exception as e:
        print(f"\nError getting messages: {str(e)}")
        raise

def run_all_tests():
    """Run all test cases"""
    try:
        print("\n🏃 Running all message tests...")
        
        tests = [
            ("Valid Email Test", test_valid_email_message()),
            ("Invalid Email Test", test_invalid_email_message()),
            ("Valid SMS Test", test_valid_sms_message()),
            ("Invalid SMS Test", test_invalid_sms_message())
        ]
        
        print("\n📊 Test Results:")
        for test_name, result in tests:
            print(f"{test_name}: {'✅ PASSED' if result else '❌ FAILED'}")
        
        print("\n📝 Current Database State:")
        display_all_messages()
        
    except Exception as e:
        print(f"\n❌ Error during tests: {str(e)}")
        raise

if __name__ == "__main__":
    run_all_tests()