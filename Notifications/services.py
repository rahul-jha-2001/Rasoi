from django.core.exceptions import ValidationError
from django.db import transaction
from template.models import Template, TemplateVersion, TemplateContent
from message_service.models import Message, MessageEvent
import hashlib
import jinja2

class MessageRenderingService:
    def __init__(self):
        self.jinja_env = jinja2.Environment(
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )

    def _render_content(self, content: str, variables: dict) -> str:
        """Renders content using Jinja2 templating"""
        try:
            template = self.jinja_env.from_string(content)
            return template.render(**variables)
        except Exception as e:
            raise ValidationError(f"Template rendering failed: {str(e)}")

    def _get_template_version(self, template_name: str, template_type: str) -> TemplateVersion:
        """Gets the current version of the template"""
        try:
            template = Template.objects.get(name=template_name)
            template_version = TemplateVersion.objects.filter(
                template=template,
                type=template_type,
                is_current=True,
                status='ACTIVE'
            ).first()
            
            if not template_version:
                raise ValidationError(f"No active version found for template: {template_name}")
            
            return template_version
        except Template.DoesNotExist:
            raise ValidationError(f"Template not found: {template_name}")

    def _create_message_hash(self, rendered_content: dict) -> str:
        """Creates a hash of the rendered content for tracking"""
        content_string = f"{rendered_content['header']}{rendered_content['body']}{rendered_content['footer']}"
        return hashlib.sha256(content_string.encode()).hexdigest()

    @transaction.atomic
    def render_message(self, template_name: str, variables: dict, template_type: str, 
                      from_address: str, to_address: str, topic: str) -> Message:
        """
        Renders a message using the specified template and variables
        
        Args:
            template_name (str): Name of the template to use
            variables (dict): Variables to use in template rendering
            template_type (str): Type of template (EMAIL, SMS, etc.)
            from_address (str): Sender address
            to_address (str): Recipient address
            topic (str): Message topic (AUTH, TRANSACTIONAL, etc.)
            
        Returns:
            Message: Created message object
        """
        try:
            # Create initial message event
            message_event = None
            
            # Get template version and content
            template_version = self._get_template_version(template_name, template_type)
            template_content = template_version.template_content
            
            # Validate variables against template requirements
            required_vars = set(template_content.variables.keys())
            provided_vars = set(variables.keys())
            missing_vars = required_vars - provided_vars
            
            if missing_vars:
                raise ValidationError(f"Missing required variables: {missing_vars}")
            
            # Render content
            rendered_content = {
                'header': self._render_content(template_content.header, variables),
                'body': self._render_content(template_content.body, variables),
                'footer': self._render_content(template_content.footer, variables)
            }
            
            # Create message hash
            message_hash = self._create_message_hash(rendered_content)
            
            # Create message
            message = Message.objects.create(
                template_name=template_name,
                template_version=str(template_version.version_number),
                from_address=from_address,
                to_address=to_address,
                topic=topic,
                variables=variables,
                status='QUEUED',
                message_hash=message_hash
            )
            
            # Log events
            MessageEvent.objects.create(
                message=message,
                event_type='QUEUED',
                description='Message queued for sending',
                metadata={
                    'template_version': str(template_version.version_number),
                    'template_type': template_type
                }
            )
            
            MessageEvent.objects.create(
                message=message,
                event_type='RENDERED',
                description='Template rendered successfully',
                metadata={
                    'message_hash': message_hash,
                    'rendered_content': rendered_content
                }
            )
            
            return message
            
        except Exception as e:
            if message_event:
                MessageEvent.objects.create(
                    message=message_event.message,
                    event_type='FAILED',
                    description=f'Message rendering failed: {str(e)}',
                    metadata={'error': str(e)}
                )
            raise ValidationError(f"Message rendering failed: {str(e)}") 