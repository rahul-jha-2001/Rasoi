from django.db import models,transaction
import uuid
from template.models import Template,Status,Category
from django.utils.translation import gettext_lazy as _
from utils.logger import Logger
import json

logger = Logger(__name__)

class MessageStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    SENT = 'SENT', _('Sent')
    FAILED = 'FAILED', _('Failed')



class MesssageManager(models.Manager):
    def _validate_phone_numbers(self, to_phone_number, from_phone_number):
        # Basic phone number validation
        if not to_phone_number or not from_phone_number:
            raise ValueError("Both 'to' and 'from' phone numbers are required")
        
        # You can add more complex validation using regex
        if not (to_phone_number.startswith('+') and len(to_phone_number) >= 10):
            raise ValueError("Invalid 'to' phone number format. Must start with '+' and have at least 10 digits")
        
        if not (from_phone_number.startswith('+') and len(from_phone_number) >= 10):
            raise ValueError("Invalid 'from' phone number format. Must start with '+' and have at least 10 digits")

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
        logger.info(f"Rendering the template: {message_json}")
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

    @transaction.atomic
    def create_message(self, template_name: str, variables: dict, to_phone_number: str, from_phone_number: str):
        try:

            template = Template.objects.get(name=template_name)
            # Validate all inputs
            logger.info(f"Creating message for template: {template.name}")
            self._validate_phone_numbers(to_phone_number, from_phone_number)
            self._validate_template(template)
            self._validate_variables(template, variables)
            self._validate_required_variables(template, variables)
            self._validate_message_type(template)
            logger.info(f"All validations passed")
            # Render the message
            message_json = template.to_message_format()
            rendered_message = self._render_template(message_json, variables)
            logger.info(f"Rendered message: {rendered_message}")
            # Create the message
            message = self.create(
                template=template,
                message_json=message_json,
                rendered_message=rendered_message,
                variables=variables,
                to_phone_number=to_phone_number,
                from_phone_number=from_phone_number,
                status=MessageStatus.PENDING,
                message_type=template.category
            )
            logger.info(f"Message created successfully: {message}")
            return message

        except Exception as e:
            invalid_message = InvalidMessage.objects.create_invalid_message(template_name, to_phone_number, from_phone_number, str(e), variables)
            logger.error(f"Error creating message: {str(e)}")
            logger.error(f"Invalid message: {invalid_message.id}")
            raise

class Message(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,primary_key=True)
    to_phone_number = models.CharField(max_length=20,null=True,blank=True)
    from_phone_number = models.CharField(max_length=20,null=True,blank=True)
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True)
    message_json = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=MessageStatus.choices, default=MessageStatus.PENDING)
    rendered_message = models.JSONField(default=dict)
    variables = models.JSONField(default=dict)
    message_type = models.CharField(max_length=20, choices=Category.choices,null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Message {self.id} - {self.status}"

    objects = MesssageManager()
    # def _get_template_variables(self, template):
    #     required_vars = set()
    #     for component in template['components']:
    #         if 'parameters' in component:
    #             for param in component['parameters']:
    #                 if param['type'].upper() == 'TEXT':
    #                     placeholder = param['text']
    #                     if placeholder.startswith('{{') and placeholder.endswith('}}'):
    #                         key = placeholder[2:-2].strip()  # Remove {{ and }} and whitespace
    #                         required_vars.add(key)
    #     return required_vars

    # def _render_template(self, template):
    #     # Check if all required variables are provided
    #     required_vars = self._get_template_variables(template)
    #     missing_vars = required_vars - set(self.variables.keys())
        
    #     if missing_vars:
    #         raise ValueError(f"Missing required variables: {', '.join(missing_vars)}")

    #     rendered = json.loads(json.dumps(template))  # Create a deep copy
    #     values = self.variables

    #     for component in rendered['components']:
    #         if 'parameters' in component:
    #             for param in component['parameters']:
    #                 if param['type'].upper() == 'TEXT':
    #                     placeholder = param['text']
    #                     if placeholder.startswith('{{') and placeholder.endswith('}}'):
    #                         key = placeholder[2:-2].strip()  # Remove {{ and }}
    #                         param['text'] = values[key]
    #     return rendered

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

    class Meta:
        ordering = ["message_type",'status','-created_at']
        indexes = [
            models.Index(fields=['message_type', 'status'])
        ]
class InvalidMessageManager(models.Manager):
    def create_invalid_message(self, template:Template, to_phone_number:str, from_phone_number:str, error_message: str, variables: dict):
        return self.create(template=template, to_phone_number=to_phone_number, from_phone_number=from_phone_number, error_message=error_message, variables=variables)

class InvalidMessage(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,primary_key=True)
    to_phone_number = models.CharField(max_length=20)
    from_phone_number = models.CharField(max_length=20)
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
    