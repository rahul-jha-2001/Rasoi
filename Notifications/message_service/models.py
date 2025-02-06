from django.db import models,transaction
import uuid
from template.models import Template
from django.utils.translation import gettext_lazy as _
import re
from proto.Notifications_pb2 import NotificationMessage,Channel
from utils.logger import Logger
from django.utils import timezone
import json

logger = Logger(__name__)

class Status(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    SENT = 'SENT', _('Sent')
    FAILED = 'FAILED', _('Failed')



class Message(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    template = models.ForeignKey(Template, on_delete=models.SET_NULL)
    message_json = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    rendered_message = models.JSONField(default=dict)
    variables = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Message {self.id} - {self.status}"
    
    def _render_template(self, template):
        rendered = json.loads(json.dumps(template))  # Create a deep copy
        values = self.variables

        for component in rendered['components']:
            if 'parameters' in component:
                for param in component['parameters']:
                    if param['type'].upper() == 'TEXT':
                        placeholder = param['text']
                        if placeholder.startswith('{{') and placeholder.endswith('}}'):
                            key = placeholder[2:-2]  # Remove {{ and }}
                            if key in values:
                                param['text'] = values[key]
            return rendered

    def render_message(self):
        return self._render_template(self.template.to_message_format())

