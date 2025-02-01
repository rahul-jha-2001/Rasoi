from django.db import models,transaction
import uuid
from template.models import Template, TemplateVersion,TemplateContent
from django.utils.translation import gettext_lazy as _
import re
from proto.Notifications_pb2 import NotificationMessage,Channel
from utils.logger import Logger
logger = Logger(__name__)
class MessageManager(models.Manager):
    def get_pending_messages(self):
        return self.filter(status=Message.Status.PENDING)
    
    def get_failed_messages(self):
        return self.filter(status__in=[Message.Status.FAILED, Message.Status.FAILED_DELIVERY])
    
    def get_by_channel(self, channel):
        return self.filter(channel=channel)
    
    def get_successful_messages(self):
        return self.filter(status__in=[Message.Status.SENT, Message.Status.DELIVERED])

    def get_by_message_id(self, message_id):
        return self.filter(message_id=message_id).first()
    
    def get_by_template_id(self, template_id):
        return self.filter(template_id=template_id)
    
    def get_by_template_version_id(self, template_version_id):
        return self.filter(template_version_id=template_version_id)

    def _render_message(self, template_version:TemplateVersion, variables:dict):
        """
        Renders the template with the provided variables
        Returns the rendered message content
        """
        try:
            template_content = TemplateContent.objects.get(template_version=template_version)
            content = template_content.header
            content += template_content.body
            content += template_content.footer
            
            # Simple variable replacement
            for key, value in variables.items():
                content = content.replace(f"{{{{{key}}}}}", str(value))
            
            return content
        except Exception as e:
            self._create_invalid_message(
                template_version,
                InvalidMessage.FailureReason.RENDERING_ERROR,
                str(e)
            )
            logger.error(f"Error rendering template: {str(e)}")
            raise

    def check_variable_exists(self, template_version:TemplateVersion, variables:dict):
        """
        Checks if all variables in the template are present in the variables dictionary
        and that no extra variables are provided
        Returns True if all variables match exactly, False otherwise
        """
        try:
            template_content = TemplateContent.objects.get(template_version=template_version)
            template_variables = set(template_content.variables)
            provided_variables = set(variables.keys())
            
            # Check if there are any missing or extra variables
            return template_variables == provided_variables
        except Exception as e:
            self._create_invalid_message(
                template_version,
                InvalidMessage.FailureReason.VALIDATION_ERROR,
                f"Error checking variables: {str(e)}"
            )
            logger.error(f"Error checking template variables: {str(e)}")
            raise

    def _create_invalid_message(self, notification:NotificationMessage, failure_reason, error_message:str):
        """
        Helper method to create an InvalidMessage record
        """
        logger.error(f"Creating invalid message: {error_message}")
        return InvalidMessage.objects.create(
            raw_data=notification,
            failure_reason=failure_reason,
            error_message=error_message
        )

    
    @transaction.atomic
    def create_from_notification(self, notification:NotificationMessage):
        """
        Creates a message record from a notification object with validation
        Returns tuple of (message_id: Optional[str], error: Optional[str])
        """
        try:
            
            # Get template and its latest version
            try:
                template = Template.objects.get(name=notification.template_name)
            except Template.DoesNotExist:
                logger.error(f"Template {notification.template_name} not found")
                self._create_invalid_message(
                    notification,
                    InvalidMessage.FailureReason.OTHER,
                    "Template not found"
                )
                return None, "Template not found"
            
            # Get template version  
            try:
                template_version = TemplateVersion.objects.get_latest_active_version(
                    template, 
                    Channel.Name(notification.channel)
                )
            except TemplateVersion.DoesNotExist:
                logger.error(f"No active version found for template {notification.template_name}")
                self._create_invalid_message(
                    notification,
                    InvalidMessage.FailureReason.VALIDATION_ERROR,
                    "No active version found for template"
                )
                return None, "No active version found for template"
            
            # Get template content
            if not self.check_variable_exists(template_version, notification.variables):
                self._create_invalid_message(
                    notification,
                    InvalidMessage.FailureReason.VALIDATION_ERROR,
                    "Missing variables in the template"
                )
                return None, "Missing variables in the template"

            # Render the template
            rendered_content = self._render_message(template_version, notification.variables)

            # Create and validate the message
            message = self.create(
                to_address=notification.to_address,
                from_address=notification.from_address,
                channel=template_version.channel,
                status=Message.Status.PENDING,
                template=template,
                template_version=template_version,
                message_content=rendered_content
            )

            if not message.is_valid():
                error = message.get_validation_error()
                message.status = Message.Status.FAILED
                message.save()
                
                self._create_invalid_message(
                    notification,
                    InvalidMessage.FailureReason.VALIDATION_ERROR,
                    error
                )

                return None, error

            return str(message.message_id), None

        except Exception as e:
            logger.error(f"Error creating message record: {str(e)}")
            self._create_invalid_message(
                notification,
                InvalidMessage.FailureReason.OTHER,
                str(e)
            )
            return None, str(e)

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
    template = models.ForeignKey(Template, verbose_name=_("Template"), on_delete=models.SET_NULL, null=True, blank=True)
    template_version = models.ForeignKey(TemplateVersion, verbose_name=_("Template Version"), on_delete=models.SET_NULL, null=True, blank=True)

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
        logger.debug(f"Validating message {self.message_id}")
        # Initialize validation error message
        self.validation_error = None

        # Check for empty required fields
        if not self.to_address:
            self.validation_error = "Missing recipient address"
            logger.error(f"Message {self.message_id} validation failed: {self.validation_error}")
            return False
        if not self.from_address:
            self.validation_error = "Missing sender address"
            logger.error(f"Message {self.message_id} validation failed: {self.validation_error}")
            return False
        if not self.message_content:
            self.validation_error = "Missing message content"
            logger.error(f"Message {self.message_id} validation failed: {self.validation_error}")
            return False
        if not self.channel:
            self.validation_error = "Missing channel"
            logger.error(f"Message {self.message_id} validation failed: {self.validation_error}")
            return False
            
        # Check content length limits
        if len(self.message_content) > 10000:
            self.validation_error = "Message content exceeds 10000 characters"
            logger.error(f"Message {self.message_id} validation failed: {self.validation_error}")
            return False
                        
        # Email validation
        if self.channel == self.Channel.EMAIL:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, self.to_address):
                self.validation_error = "Invalid recipient email address"
                logger.error(f"Message {self.message_id} validation failed: {self.validation_error}")
                return False
            if not re.match(email_pattern, self.from_address):
                self.validation_error = "Invalid sender email address"
                logger.error(f"Message {self.message_id} validation failed: {self.validation_error}")
                return False
                
        # SMS validation
        if self.channel == self.Channel.SMS:
            phone_pattern = r'^\+?[1-9]\d{7,14}$'
            if not re.match(phone_pattern, self.to_address):
                self.validation_error = "Invalid recipient phone number"
                logger.error(f"Message {self.message_id} validation failed: {self.validation_error}")
                return False
            if not re.match(phone_pattern, self.from_address):
                self.validation_error = "Invalid sender phone number"
                logger.error(f"Message {self.message_id} validation failed: {self.validation_error}")
                return False
        
        # Content type validation for email
        if self.channel == self.Channel.EMAIL:
            if ('<' in self.message_content or '>' in self.message_content) and not (
                self.message_content.startswith('<!DOCTYPE html>') or 
                self.message_content.startswith('<html>')):
                self.validation_error = "HTML content detected without proper HTML tags"
                logger.error(f"Message {self.message_id} validation failed: {self.validation_error}")
                return False
        
        # SMS specific validation
        if self.channel == self.Channel.SMS:
            if len(self.message_content) > 160:
                self.validation_error = "SMS content exceeds 160 characters"
                logger.error(f"Message {self.message_id} validation failed: {self.validation_error}")
                return False
            
            if not all(ord(char) < 128 for char in self.message_content):
                self.validation_error = "SMS contains unsupported Unicode characters"
                logger.error(f"Message {self.message_id} validation failed: {self.validation_error}")
                return False
        
        logger.info(f"Message {self.message_id} validation successful")
        return True

    def get_validation_error(self):
        """Returns the validation error message if it exists, otherwise returns None."""
        error = getattr(self, 'validation_error', None)
        if error:
            logger.debug(f"Retrieving validation error for message {self.message_id}: {error}")
        return error

    class Meta:
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        ordering = ['-updated_at']

class InvalidMessage(models.Model):
    class FailureReason(models.TextChoices):
        INVALID_TEMPLATE = 'INVALID_TEMPLATE', 'Template Not Found'
        INVALID_FORMAT = 'INVALID_FORMAT', 'Invalid Message Format'
        VALIDATION_ERROR = 'VALIDATION_ERROR', 'Validation Error'
        RENDERING_ERROR = 'RENDERING_ERROR', 'Template Rendering Error'
        OTHER = 'OTHER', 'Other Error'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    raw_data = models.TextField(verbose_name=_("Raw Notification Data"))
    failure_reason = models.CharField(
        max_length=50, 
        choices=FailureReason.choices,
        default=FailureReason.OTHER
    )
    error_message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Invalid Message")
        verbose_name_plural = _("Invalid Messages")
        ordering = ['-created_at']

    def __str__(self):
        return f"Invalid Message {self.id} - {self.failure_reason}"

