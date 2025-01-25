# Create your models here.
from django.db import models
from django.utils.timezone import now

class MessageTemplate(models.Model):
    TEMPLATE_TYPES = [
        ('Text', 'Text'),
        ('Media', 'Media'),
        ('Button', 'Button'),
    ]

    TemplateId = models.CharField(max_length=255, unique=True)
    Name = models.CharField(max_length=255)
    Body = models.TextField()  # Supports placeholders like {{1}}, {{2}}, etc.
    Language = models.CharField(max_length=10, default='en')  # e.g., 'en', 'es'
    HeaderType = models.CharField(max_length=50, choices=TEMPLATE_TYPES, default='text')
    Buttons = models.JSONField(blank=True, null=True)  # Optional for buttons in templates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    IsActive = models.BooleanField(default=True)  # Soft delete support

    def __str__(self):
        return self.name
    
class MessageLog(models.Model):
    STATUS_CHOICES = models.TextChoices([
        ('Pending', 'Pending'),
        ('Sent', 'Sent'),
        ('Failed', 'Failed'),
        ('Cancelled', 'Cancelled'),
    ])

    PRIORITY_CHOICES =  models.TextChoices([
        ('High', 'High'),
        ('Normal', 'Normal'),
        ('Low', 'Low'),
    ])

    MessageId = models.CharField(max_length=255, unique=True)
    Template = models.ForeignKey(MessageTemplate, on_delete=models.CASCADE, related_name='messages')
    Recipient = models.CharField(max_length=50)  # e.g., phone number, email
    PlaceHolders = models.JSONField()  # Stores placeholders for the template
    Status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    Priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    Response = models.JSONField(blank=True, null=True)  # Stores the API response or error message
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Message {self.message_id} to {self.recipient}"