from django.db import models
import uuid
from template.models import Template, TemplateVersion
from django.utils.translation import gettext_lazy as _
import re

class MessageManager(models.Manager):
    def get_pending_messages(self):
        return self.filter(status=Message.Status.PENDING)
    
    def get_failed_messages(self):
        return self.filter(status__in=[Message.Status.FAILED, Message.Status.FAILED_DELIVERY])
    
    def get_by_channel(self, channel):
        return self.filter(channel=channel)
    
    def get_successful_messages(self):
        return self.filter(status__in=[Message.Status.SENT, Message.Status.DELIVERED])

class Message(models.Model):
    class Channel(models.TextChoices):
        EMAIL = 'EMAIL', 'Email'
        SMS = 'SMS', 'SMS'
        PUSH = 'PUSH', 'Push'
        INAPP = 'INAPP', 'In-App'
        WHATSAPP = 'WHATSAPP', 'Whatsapp'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SENT = 'SENT', 'Sent'
        FAILED = 'FAILED', 'Failed'
        DELIVERED = 'DELIVERED', 'Delivered'
        FAILED_DELIVERY = 'FAILED_DELIVERY', 'Failed Delivery'
        RETRY = 'RETRY', 'Retry'

    class Type(models.TextChoices):
        AUTHENTICATION = 'AUTHENTICATION', 'Authentication'
        NOTIFICATION = 'NOTIFICATION', 'Notification'
        PROMOTION = 'PROMOTION', 'Promotion'
        RECOVERY = 'RECOVERY', 'Recovery'
        REWARD = 'REWARD', 'Reward'
        OTHER = 'OTHER', 'Other'

    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    to_address = models.TextField(verbose_name=_("To Address"), null=True, blank=True)
    from_address = models.TextField(verbose_name=_("From Address"), null=True, blank=True)
    channel = models.CharField(max_length=255, choices=Channel.choices)
    status = models.CharField(max_length=255, choices=Status.choices, default=Status.PENDING)
    message_content = models.TextField()
    
    # template relationships
    template = models.ForeignKey(Template, verbose_name=_("Template"), on_delete=models.DO_NOTHING)
    template_version = models.ForeignKey(TemplateVersion, verbose_name=_("Template Version"), on_delete=models.DO_NOTHING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MessageManager()

    def __str__(self):
        return f"Message {self.to_address}- {self.from_address} - {self.channel} - {self.status}"

    def is_valid(self) -> bool:
        """
        Validates if the message has all required fields properly set with enhanced validation.
        Returns True if message is valid, False otherwise.
        """
        # Check for empty required fields
        if not self.to_address or not self.from_address:
            return False
            
        if not self.message_content:
            return False
            
        if not self.channel:
            return False
            
        # Check content length limits
        if len(self.message_content) > 10000:  # Standard subject length limit
            return False
                        
        
        # Email validation
        if self.channel == self.Channel.EMAIL:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not (re.match(email_pattern, self.to_address) and 
                   re.match(email_pattern, self.from_address)):
                return False
                
        # SMS validation
        if self.channel == self.Channel.SMS:
            # International phone number format: +1234567890 or 1234567890
            phone_pattern = r'^\+?[1-9]\d{7,14}$'
            if not (re.match(phone_pattern, self.to_address) and 
                   re.match(phone_pattern, self.from_address)):
                return False
        
        # Content type validation for email
        if self.channel == self.Channel.EMAIL:
            # Check if body contains suspected HTML without proper tags
            if ('<' in self.message_content or '>' in self.message_content) and not (
                self.message_content.startswith('<!DOCTYPE html>') or 
                self.message_content.startswith('<html>')):
                return False
        
        # SMS specific validation
        if self.channel == self.Channel.SMS:
            # SMS typically has a 160 character limit for single messages
            if len(self.message_content) > 160:
                return False
            
            # Check for Unicode characters that might not be SMS-compatible
            if not all(ord(char) < 128 for char in self.message_content):
                return False
        
        return True

    class Meta:
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        ordering = ['-updated_at']

