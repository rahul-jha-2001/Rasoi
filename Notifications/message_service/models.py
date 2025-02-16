from django.db import models,transaction
import uuid
from template.models import Template,Status,Category,ParameterFormat
from django.utils.translation import gettext_lazy as _
from utils.logger import Logger
import json
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from typing import Optional
from django.db.models import QuerySet
from collections import defaultdict
from datetime import datetime
import re  # Add this import at the top of the file
logger = Logger(__name__)

class MessageStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    SENT = 'SENT', _('Sent')
    FAILED = 'FAILED', _('Failed')

class MessagePriority(models.IntegerChoices):
    MARKETING = 1
    UTILITY = 2
    AUTHENTICATION = 3


class MessageManager(models.Manager):
    PRIORITY_MAP = {
        Category.AUTHENTICATION: MessagePriority.AUTHENTICATION,
        Category.UTILITY: MessagePriority.UTILITY,
        Category.MARKETING: MessagePriority.MARKETING
    }
    def get_queryset(self):
        """Override default queryset to exclude soft-deleted messages"""
        return super().get_queryset().filter(is_deleted=False)

    def _validate_phone_numbers(self, to_phone_number, from_phone_number):

        # Basic phone number validation
        if not to_phone_number or not from_phone_number:
            raise ValueError("Both 'to' and 'from' phone numbers are required")
        
        # You can add more complex validation using regex
        if not (to_phone_number.startswith('+') and len(to_phone_number) >= 10):
            raise ValueError("Invalid 'to' phone number format. Must start with '+' and have at least 10 digits")
        
    def _validate_template(self, template):
        if not template:
            raise ValueError("Template is required")
        
        if not isinstance(template, Template):
            raise ValueError("Invalid template object")
        
        # Check if template is active/valid
        # if not template.status == Status.APPROVED:
        #     raise ValueError("Template is not active")

    def _validate_variables(self, template, variables):
        if not isinstance(variables, dict):
            raise ValueError("Variables must be a dictionary")

    def _validate_required_variables(self, template, variables):
        # Get required variables from template
        
        required_vars = set()
        template_data = template.to_message_format()
        for component in template_data['components']:
            if 'parameters' in component:
                for param in component['parameters']:
                    if param['type'].upper() == 'TEXT':
                        placeholder = param['text']
                        if placeholder.startswith('{{') and placeholder.endswith('}}'):
                            key = placeholder[2:-2].strip()
                            required_vars.add(key)

        # Check for missing variables
        missing_vars = required_vars - set(variables.keys())
        if missing_vars:
            raise ValueError(f"Missing required variables: {', '.join(missing_vars)}")

        # Check for extra variables that aren't in template
        extra_vars = set(variables.keys()) - required_vars
        if extra_vars:
            logger.warning(f"Extra variables provided but not used in template: {', '.join(extra_vars)}")

    def _validate_message_type(self, template):
        if not template.category:
            raise ValueError("Template category is required")
        if template.category not in [choice[0] for choice in Category.choices]:
            raise ValueError("Invalid template category")
        
    def _render_template(self, message_json: dict, variables: dict):
        logger.debug(f"Rendering the template: {message_json}")
        # Create a deep copy to avoid modifying the original template
        rendered_json = json.loads(json.dumps(message_json))
        
        for component in rendered_json['components']:
            if 'parameters' in component:
                for param in component['parameters']:
                    if param['type'].upper() == 'TEXT':
                        text = param['text']
                        # Find all placeholders in the text
                        while '{{' in text and '}}' in text:
                            start = text.find('{{')
                            end = text.find('}}') + 2
                            placeholder = text[start:end]
                            key = placeholder[2:-2].strip()
                            
                            if key in variables:
                                # Replace the placeholder with the variable value
                                text = text.replace(placeholder, str(variables[key]))
                            else:
                                logger.warning(f"Variable {key} not found in variables dict")
                    
                        param['text'] = text
        
        return rendered_json

    # def _readble_message(self, template: Template, variables: dict) -> str:

    #     def _destructure_variables(variables: dict):
    #         variable = defaultdict(list)

    #         for k, v in variables.items():
    #             if k.startswith("BODY"):
    #                 variable["BODY"].append((int(k.split("_")[1]), v))  # Convert to int for sorting
    #             elif k.startswith("HEADER"):
    #                 variable["HEADER"].append((int(k.split("_")[1]), v))
    #             elif k.startswith("BUTTON"):
    #                 variable["BUTTON"].append((int(k.split("_")[1]), v))

    #         for i in variable:
    #             variable[i] = [v for _, v in sorted(variable[i], key=lambda x: x[0])]
            
    #         return variable
    #     if template.parameter_format == ParameterFormat.POSITIONAL:
    #         variable = _destructure_variables(variables)
    #         readable_message = {}
    #         logger.info(f"Variable:{variable}")
    #         for component in template.components.all():
    #             logger.info(f"Looping through components: {component.type}")
    #             if component.type == "BODY":
    #                 logger.info(f"Variable:{variable['BODY']}")
    #                 readable_message["BODY"] = component.text.format(0,*variable["BODY"])  # Use * for positional
    #             elif component.type == "HEADER":
    #                 readable_message["HEADER"] = component.text.format(0,*variable["HEADER"])
    #             elif component.type == "BUTTON":
    #                 readable_message["BUTTON"] = component.text.format(0,*variable["BUTTON"])
    #     elif template.parameter_format == ParameterFormat.NAMED:
    #         readable_message = {}
    #         for component in template.components.all():
    #             logger.info(f"Looping through components: {component.type}")
    #             if component.type == "BODY":
    #                 readable_message["BODY"] = component.text.format(**variable["BODY"])
    #             elif component.type == "HEADER":
    #                 readable_message["HEADER"] = component.text.format(**variable["HEADER"])
    #     return readable_message
    
    @transaction.atomic
    def create_message(self, template_name: str, variables: dict, to_phone_number: str, from_phone_number: str):
        try:
            logger.info(f"Creating message for template: {template_name}")
            template = Template.objects.get(name=template_name)
            # Validate all inputs
            logger.info(f"Creating message for template: {template.name}")
            self._validate_phone_numbers(to_phone_number, from_phone_number)
            self._validate_template(template)

            self._validate_variables(template, variables)
            self._validate_required_variables(template, variables)
            self._validate_message_type(template)
            # Render the message
            message_json = template.to_message_format()
            rendered_message = self._render_template(message_json, variables)
            # readable_message = self._readble_message(template, variables)
            # Create the message
            priority = self.PRIORITY_MAP.get(template.category, MessagePriority.AUTHENTICATION)
            
            message = self.create(
                template=template,
                message_json=message_json,
                rendered_message=rendered_message,
                # readable_message=readable_message,
                variables=variables,
                to_phone_number=to_phone_number,
                from_phone_number=from_phone_number,
                status=MessageStatus.PENDING,
                message_type=template.category,
                priority=priority
            )
            logger.info(f"Message created successfully: {message}")
            return message

        except Exception as e:
            
            invalid_message = InvalidMessage.objects.create_invalid_message(template, to_phone_number, from_phone_number, str(e), variables)
            invalid_message.save()
            logger.error(f"Invalid message: {invalid_message.id}")
            raise e
    
    @transaction.atomic
    def update_message(self, message_id: str, variables: dict=None, to_phone_number: str=None, from_phone_number: str=None):
        try:
            message = self.get(id=message_id)
        except Message.DoesNotExist:
            logger.error(f"Message not found: {message_id}")
            raise e
        except Exception as e:
            logger.error(f"Failed to update message: {e}")
            raise e
        
        try:
            if message.status == MessageStatus.PENDING:
                logger.debug(f"Updating message: {message.id}")
                
                if to_phone_number is not None:
                    logger.debug(f"Updating to phone number: {to_phone_number}")
                    if to_phone_number.startswith('+') and len(to_phone_number) >= 10:
                        message.to_phone_number = to_phone_number
                        logger.info(f"Updated to phone number: {message.to_phone_number}")
                
                if from_phone_number is not None:
                    logger.debug(f"Updating from phone number: {from_phone_number}")
                    if from_phone_number.startswith('+') and len(from_phone_number) >= 10:
                        message.from_phone_number = from_phone_number
                        logger.info(f"Updated from phone number: {message.from_phone_number}")
                
                if variables is not None:
                    logger.debug(f"Updating variables: {variables}")
                    template = message.template
                    # These methods will raise exceptions if validation fails
                    self._validate_variables(template, variables)
                    self._validate_required_variables(template, variables)
                    
                    message.variables = variables
                    logger.info(f"Updated variables: {message.variables}")
                    message.rendered_message = self._render_template(message.message_json, variables)
                    logger.info(f"Updated rendered message: {message.rendered_message}")

                message.updated_at = timezone.now()
                message.save()
                logger.info(f"Updated message: {message}")
                return message
            else:
                logger.error(f"Message is not pending: {message.status}")
                return message
        except Exception as e:
            logger.error(f"Failed to update message: {e}")
            raise e

    @transaction.atomic
    def delete_message(self, message_id: str):
        try:
            message = self.get(id=message_id)
            message.delete()
            logger.info(f"Deleted message: {message_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            return False

    def get_pending_messages_by_priority(
        self,
        page: int = 1,
        batch_size: int = 10) -> tuple[QuerySet, Optional[int]]:
        """
                Retrieve pending messages ordered by priority and creation date with pagination.

            Args:
                page (int): The page number to retrieve (default: 1)
                batch_size (int): Number of items per page (default: 10)

            Returns:
                Tuple[QuerySet, Optional[int]]: A tuple containing:
                    - The page of messages
                    - The next page number, or None if there isn't one

            Raises:
                ValueError: If batch_size is less than 1
                Exception: For any other unexpected errors
            """
        if batch_size < 1:
            raise ValueError("batch_size must be at least 1")

        try:
            logger.debug(f"Fetching pending messages for page {page} with batch size {batch_size}")
            
            base_qs = self.filter(status=MessageStatus.PENDING,is_deleted=False).order_by('priority', '-created_at')
            paginator = Paginator(base_qs, batch_size)
        
            try:
                messages = paginator.page(page)
            except (EmptyPage, PageNotAnInteger):
                logger.info(f"Invalid page {page} requested, defaulting to page 1")
                messages = paginator.page(1)
        
            next_page = messages.next_page_number() if messages.has_next() else None
            
            logger.debug(f"Successfully retrieved {len(messages)} messages")
            return messages, next_page
            
        except Exception as e:
            logger.error(f"Error getting pending messages by priority: {e}")
            raise

    def get_messages_by_filter(self,
                               page: int = 1,
                               limit: int = 10,
                               **kwargs):
        logger.debug(f"Start date: {kwargs.get('start_date')}")
        logger.debug(f"End date: {kwargs.get('end_date')}")

        

        if page < 1:
            page = 1
        if limit < 1:
            limit = 10
        
        messages = self.filter(**kwargs).order_by('-created_at')
        paginator = Paginator(messages, limit)
        page_messages = paginator.page(page)
        next_page = page_messages.next_page_number() if page_messages.has_next() else None
        previous_page = page_messages.previous_page_number() if page_messages.has_previous() else None
        return page_messages, next_page, previous_page
        
        
class Message(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,primary_key=True)
    to_phone_number = models.CharField(max_length=20,null=True,blank=True)
    from_phone_number = models.CharField(max_length=20,null=True,blank=True)
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True)
    message_json = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=MessageStatus.choices, default=MessageStatus.PENDING)
    rendered_message = models.JSONField(default=dict)
    variables = models.JSONField(default=dict)
    # readable_message = models.JSONField(default=dict)
    message_type = models.CharField(max_length=20, choices=Category.choices,null=True,blank=True)
    priority = models.IntegerField(choices=MessagePriority.choices,default=MessagePriority.AUTHENTICATION)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Message {self.id} - {self.status}"

    objects = MessageManager()

    def get_rendered_message(self):
        return self.rendered_message
    
    def get_message_json(self):
        return self.message_json
    
    def get_variables(self):
        return self.variables

    def get_message_type(self):
        return self.message_type
    
    def get_status(self):
        return self.status
    
    def get_error_message(self):
        return self.error_message

    def __str__(self):
        return f"Message {self.template.name} - {self.status}-{self.message_type}-{self.to_phone_number}-{self.from_phone_number}"

    def delete(self, using=None, keep_parents=False):
        """Soft delete the message instead of actually deleting it"""
        self.is_deleted = True
        self.save()


    class Meta:
        ordering = ["priority",'status','-created_at']
        indexes = [
            models.Index(fields=['priority', 'status'])
        ]
class InvalidMessageManager(models.Manager):
    @transaction.atomic
    def create_invalid_message(self, template:Template, to_phone_number:str, from_phone_number:str, error_message: str, variables: dict):
        logger.error(f"Creating Invalid Message: {error_message}")
        invalid_message = self.create(template=template, to_phone_number=to_phone_number, from_phone_number=from_phone_number, error_message=error_message, variables=variables)
        logger.error(f"Invalid Message created: {invalid_message}")
        return invalid_message
    
    def get_messages_by_filter(self,
                               page: int = 1,
                               limit: int = 10,
                               **kwargs):
        logger.debug(f"Start date: {kwargs.get('start_date')}")
        logger.debug(f"End date: {kwargs.get('end_date')}")

        

        if page < 1:
            page = 1
        if limit < 1:
            limit = 10
        
        messages = self.filter(**kwargs).order_by('-created_at')
        paginator = Paginator(messages, limit)
        page_messages = paginator.page(page)
        next_page = page_messages.next_page_number() if page_messages.has_next() else None
        previous_page = page_messages.previous_page_number() if page_messages.has_previous() else None
        return page_messages, next_page, previous_page
    
class InvalidMessage(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,primary_key=True)
    to_phone_number = models.CharField(max_length=20,null=True,blank=True)
    from_phone_number = models.CharField(max_length=20,null=True,blank=True)
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True)
    message_json = models.JSONField(default=dict)
    rendered_message = models.JSONField(default=dict)
    variables = models.JSONField(default=dict)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = InvalidMessageManager()

    def __str__(self):
        return f"Invalid Message {self.id} - {self.error_message}"
    
    def get_invalid_message(self):
        return self.error_message
    
    def get_invalid_message_json(self):
        return self.message_json
    
    def get_invalid_message_rendered(self):
        return self.rendered_message
    
    def get_invalid_message_variables(self):
        return self.variables
    
    