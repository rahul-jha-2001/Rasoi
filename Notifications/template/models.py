from django.db import models,transaction
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.paginator import Paginator
import uuid 
# from managers import TemplateManager, TemplateVersionManager, TemplateContentManager

from utils.logger import Logger
import requests

import urllib.parse

logger = Logger(__name__)


class TemplateManager(models.Manager):
    """
    Manager class for handling Template model operations including creation, retrieval,
    and synchronization with WhatsApp API.
    """
    @transaction.atomic
    def create_template_with_json(self, template_data):
        """
        Create a template with its associated components, parameters, and buttons from JSON data.
        
        Args:
            template_data (dict): JSON data containing template information including:
                - name (str): Template name
                - category (str): Template category (MARKETING/UTILITY/AUTHENTICATION)
                - language (str): Template language code
                - id (str): WhatsApp template ID
                - status (str): Template status
                - components (list): List of component dictionaries
                - parameter_format (str, optional): Format for parameters
                - message_send_ttl_seconds (int, optional): Time-to-live in seconds
        
        Returns:
            Template: Created template instance
        
        Raises:
            ValidationError: If template data is invalid or creation fails
        """
        logger.info(f"Creating template: {template_data['name']}")
        try:
            with transaction.atomic():
                # Validate required template fields
                required_fields = ["name", "category", "language"]
                for field in required_fields:
                    if field not in template_data:
                        raise ValidationError(f"Missing required field: {field}")

                # Create template instance
                template = self.model(
                    name=template_data["name"],
                    category=template_data["category"],
                    language=template_data["language"],
                    whatsapp_template_id=template_data["id"],
                    status=template_data["status"],
                )

                # Add optional fields if they exist
                if "parameter_format" in template_data:
                    template.parameter_format = template_data["parameter_format"]
                if "message_send_ttl_seconds" in template_data:
                    template.message_send_ttl_seconds = template_data["message_send_ttl_seconds"]

                try:
                    template.full_clean()
                    template.save()
                    logger.info(f"Created template: {template.id} - {template.name}")
                except ValidationError as ve:
                    logger.error(f"Template validation failed: {str(ve)}")
                    raise ValidationError(f"Invalid template data: {str(ve)}")

                # Create components if present
                if "components" in template_data:
                    for component_data in template_data["components"]:
                        if "type" not in component_data:
                            logger.error("Component type is required")
                            continue

                        # Handle BUTTONS component
                        if "BUTTONS" == component_data['type']:
                            self._create_buttons(template, component_data)
                            continue

                        # Handle specific component types
                        component_handler = {
                            'HEADER': self._create_header_component,
                            'BODY': self._create_body_component,
                            'FOOTER': self._create_footer_component
                        }.get(component_data['type'])

                        if component_handler:
                            try:
                                component = component_handler(template, component_data)
                                if component and component.text:
                                    self._create_parameters(component, template)
                                logger.info(f"Created {component_data['type']} component for template {template.id}")
                            except Exception as ce:
                                logger.error(f"Failed to create {component_data['type']} component: {str(ce)}")
                                continue
                        else:
                            logger.error(f"Unsupported component type: {component_data['type']}")

                logger.info(f"Successfully created template {template.id} with all components")
                return template

        except ValidationError:
            raise
        except (KeyError, TypeError) as e:
            logger.error(f"Invalid template data structure: {str(e)}")
            raise ValidationError(f"Invalid template data structure: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating template: {str(e)}")
            raise ValidationError(f"Failed to create template: {str(e)}")

    @transaction.atomic
    def update_template_with_json(self, template_data):
        """
        Update a template with its associated components, parameters, and buttons from JSON data.
        
        Args:
            template_data (dict): JSON data containing template information including:
                - name (str): Template name
                - category (str): Template category (MARKETING/UTILITY/AUTHENTICATION)
                - language (str): Template language code
                - id (str): WhatsApp template ID
                - status (str): Template status
                - components (list): List of component dictionaries
                - parameter_format (str, optional): Format for parameters
                - message_send_ttl_seconds (int, optional): Time-to-live in seconds
        
        Returns:
            Template: Updated template instance
        
        Raises:
            ValidationError: If template data is invalid or update fails
        """
        logger.info(f"Updating template: {template_data['name']}")
        try:
            with transaction.atomic():
                # Get existing template
                template = self.get(name=template_data["name"])
                # Update basic template fields
                if "category" in template_data:
                    template.category = template_data["category"]
                if "status" in template_data:
                    template.status = template_data["status"]
                
                try:
                    template.full_clean()
                    template.save()
                    logger.info(f"Updated template: {template.id} - {template.name}")
                except ValidationError as ve:
                    logger.error(f"Template validation failed: {str(ve)}")
                    raise ValidationError(f"Invalid template data: {str(ve)}")

                # Delete existing components, parameters, and buttons
                template.components.all().delete()
                template.buttons.all().delete()

                # Create new components if present
                if "components" in template_data:
                    for component_data in template_data["components"]:
                        if "type" not in component_data:
                            logger.error("Component type is required")
                            continue

                        # Handle BUTTONS component
                        if "BUTTONS" == component_data['type']:
                            self._create_buttons(template, component_data)
                            continue

                        # Handle specific component types
                        component_handler = {
                            'HEADER': self._create_header_component,
                            'BODY': self._create_body_component,
                            'FOOTER': self._create_footer_component
                        }.get(component_data['type'])

                        if component_handler:
                            try:
                                component = component_handler(template, component_data)
                                if component and component.text:
                                    self._create_parameters(component, template)
                                logger.info(f"Created {component_data['type']} component for template {template.id}")
                            except Exception as ce:
                                logger.error(f"Failed to create {component_data['type']} component: {str(ce)}")
                                continue
                        else:
                            logger.error(f"Unsupported component type: {component_data['type']}")

                logger.info(f"Successfully updated template {template.id} with all components")
                return template

        except Template.DoesNotExist:
            logger.error(f"Template with WhatsApp ID {template_data['id']} not found")
            raise ValidationError(f"Template with WhatsApp ID {template_data['id']} not found")
        except ValidationError:
            raise
        except (KeyError, TypeError) as e:
            logger.error(f"Invalid template data structure: {str(e)}")
            raise ValidationError(f"Invalid template data structure: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error updating template: {str(e)}")
            raise ValidationError(f"Failed to update template: {str(e)}")

    @transaction.atomic
    def _create_buttons(self, template, component_data):
        """Helper method to create buttons"""
        logger.info(f"Creating buttons for template {template.id}")
        logger.info(f"Component data: {component_data}")
        logger.info(f"Buttons: {component_data['buttons']}")
        for button_index, button_data in enumerate(component_data["buttons"]):
            if all(k in button_data for k in ["type", "text"]):
                try:
                    Button.objects.create(
                        template=template,
                        type=button_data["type"],
                        text=button_data["text"],
                        url=button_data.get("url"),
                        index=button_index
                    )
                except Exception as be:
                    logger.error(f"Failed to create button: {str(be)}")

    @transaction.atomic
    def _create_header_component(self, template, component_data):
        """Create header component with specific validation"""
        if "format" in component_data:
            return Component.objects.create(
                template=template,
                type=ComponentType.HEADER,
                format=component_data.get("format"),
                text=component_data.get("text")
            )
        return Component.objects.create(
            template=template,
            type=ComponentType.HEADER,
            text=component_data.get("text")
        )
    @transaction.atomic
    def _create_body_component(self, template, component_data):
        """Create body component"""
        return Component.objects.create(
            template=template,
            type=ComponentType.BODY,
            text=component_data.get("text")
        )

    @transaction.atomic
    def _create_footer_component(self, template, component_data):
        """Create footer component"""
        return Component.objects.create(
            template=template,
            type=ComponentType.FOOTER,
            text=component_data.get("text")
        )

    @transaction.atomic
    def _create_parameters(self, component, template):
        """Helper method to create parameters for a component"""
        import re
        logger.info(f"Creating parameters for component {component.text}")
        param_patterns = re.findall(r'\{\{.*?\}\}', component.text)
        logger.info(f"Found {param_patterns} parameters in component {component.id}")

        if template.parameter_format == ParameterFormat.POSITIONAL:
            for i in range(len(param_patterns)):    
                Parameters.objects.create(
                        component=component,
                        name=f"param_{i}",
                        type=ParameterType.TEXT,
                        index=i
                    )
                logger.info(f"Created parameter param_{i} for component {component.id}")
        else:
            for match in param_patterns:
                
                Parameters.objects.create(
                    component=component,
                    name=match.lstrip('{{').rstrip('}}'),
                    type=ParameterType.TEXT,
                )
                logger.info(f"Created parameter {match} for component {component.id}")
    
    def get_template_with_components(self, template_id):
        """
        Get template with all its components and related data
        """
        return self.select_related().prefetch_related(
            'components',
            'components__parameters',
            'components__buttons'
        ).get(id=template_id)

    def get_templates_by_category(self, category):
        """
        Get all templates for a specific category
        """
        return self.filter(category=category)

    def get_template_by_name(self, name):
        """
        Get all templates for a specific category
        """
        return self.get(name=name)

    def get_template_by_id(self, id):
        """
        Get template by id
        """
        return self.get(id=id)
    
    def get_template_by_whatsapp_id(self, whatsapp_id):
        """
        Get template by whatsapp id
        """
        return self.get(whatsapp_template_id=whatsapp_id)

    def get_active_templates(self):
        """
        Get all approved templates
        """
        return self.filter(status=Status.APPROVED)
    
    @transaction.atomic
    def sync_with_whatsapp(self):
        """
        Sync all templates with WhatsApp API, handling pagination via next URL.
        Will update existing templates or create new ones as needed.
        """
        base_url = f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_BUSINESS_ACCOUNT_ID}/message_templates"
        params = {
            "access_token": settings.WHATSAPP_ACCESS_TOKEN
        }
        
        current_url = base_url
        while True:
            logger.info(f"Syncing templates with WhatsApp API, current URL: {current_url}")
            rs = requests.get(current_url, params=params if current_url == base_url else None)
            response_data = rs.json()
            
            # Process current page of templates
            for template_data in response_data["data"]:
                logger.info(f"Processing template: {template_data['name']}")
                try:
                    # Try to find existing template by name
                    try:
                        existing_template = self.get(name=template_data["name"])
                        # If found, update it
                        self.update_template_with_json(template_data)
                        logger.info(f"Updated existing template: {template_data['name']}")
                    except Template.DoesNotExist:
                        # If not found, create new template
                        self.create_template_with_json(template_data)
                        logger.info(f"Created new template: {template_data['name']}")
                except Exception as e:
                    logger.error(f"Failed to sync template {template_data.get('name', 'unknown')}: {str(e)}")
            
            # Check if there are more pages using the "next" URL
            if "paging" in response_data and "next" in response_data["paging"]:
                current_url = response_data["paging"]["next"]
            else:
                break
        logger.info(f"Syncing templates with WhatsApp API completed")
        return True


    def get_templates_by_filter(self, category=None, status=None, language=None, parameter_format=None, page=1, limit=10):
        """
        Get templates by filter with pagination
        """
        filters = {}
        if category:
            filters['category'] = category
        if status:
            filters['status'] = status
        if language:
            filters['language'] = language
        if parameter_format:
            filters['parameter_format'] = parameter_format
        templates = self.filter(**filters).order_by('name')
        paginator = Paginator(templates, limit)
        next_page = paginator.page(page).next_page_number() if paginator.page(page).has_next() else None
        previous_page = paginator.page(page).previous_page_number() if paginator.page(page).has_previous() else None
        return paginator.page(page).object_list, next_page, previous_page


class Category(models.TextChoices):
    MARKETING = 'MARKETING', 'Marketing'
    UTILITY = 'UTILITY', 'Utility'
    AUTHENTICATION = 'AUTHENTICATION', 'Authentication'

class Status(models.TextChoices):
    PENDING = 'PENDING', 'Pending Approval'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'

class ParameterFormat(models.TextChoices):
    POSITIONAL = 'POSITIONAL', 'Positional'
    NAMED = 'NAMED', 'Named'

class ComponentType(models.TextChoices):
    HEADER = 'HEADER', 'Header'
    BODY = 'BODY', 'Body'
    FOOTER = 'FOOTER', 'Footer'

class ParameterType(models.TextChoices):
    TEXT = 'TEXT', 'Text'
    URL = 'URL', 'URL'
    CURRENCY = 'CURRENCY', 'Currency'
    MEDIA = 'MEDIA', 'Media'

class ButtonType(models.TextChoices):
    QUICK_REPLY = 'QUICK_REPLY', 'Quick Reply'
    URL = 'URL', 'URL'


class Template(models.Model):
    """
    Represents a WhatsApp message template with components, parameters, and buttons.
    
    A template consists of various components (header, body, footer) and can include
    interactive elements like buttons. Templates support both positional and named
    parameters for dynamic content.

    Attributes:
        id (UUID): Unique identifier for the template
        name (str): Template name
        category (str): Template category (from Category choices)
        status (str): Current template status (from Status choices)
        language (str): Template language code
        parameter_format (str): Format for parameters (POSITIONAL/NAMED)
        message_send_ttl_seconds (int): Message time-to-live in seconds
        whatsapp_template_id (str): Associated WhatsApp template ID
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255,unique=True)
    category = models.CharField(max_length=255, choices=Category.choices)
    status = models.CharField(max_length=255, choices=Status.choices, default=Status.PENDING)
    language = models.CharField(max_length=255)
    parameter_format = models.CharField(max_length=255, choices=ParameterFormat.choices, default=ParameterFormat.POSITIONAL)
    message_send_ttl_seconds = models.IntegerField(default=86400)
    whatsapp_template_id = models.CharField(max_length=255, null=True, blank=True, unique=True)

    objects = TemplateManager()

    def __str__(self) -> str:
        return self.name + " - " + self.category + " - " + self.status + " - " + self.language + " - " + self.parameter_format

    def to_whatsapp_format(self, name=None):
        """
        Convert template to WhatsApp API format.
        
        Args:
            name (str, optional): Template name to fetch specific template
        
        Returns:
            dict: Template data in WhatsApp API format including components and buttons
        """
        data= {}
        if name:
            template = Template.objects.get(name=name)
        else:
            template = self
        if template.name:
            data["name"]= template.name
        if template.category:
            data["category"]= template.category
        if template.language:
            data["language"]= template.language
        if template.parameter_format:
            data["parameter_format"]= template.parameter_format
        if template.message_send_ttl_seconds:
            data["message_send_ttl_seconds"]= template.message_send_ttl_seconds
        components = []
        for component in template.components.all():
            components.append(component.to_whatsapp_format())
        buttons = []
        for button in template.buttons.all():
            buttons.append(button.to_whatsapp_format())
        data["components"]= components
        if buttons:
            data["BUTTONS"]= buttons
        return data
    
    def to_message_format(self):
        """
        Convert template to message sending format.
        
        Returns:
            dict: Template data formatted for message sending including:
                - name: Template name
                - language: Language information
                - components: List of component data
        """
        template = {}
        template["name"] = self.name
        template["language"] = {"code": self.language}
        template["components"] = []
        for component in self.components.all():
            temp = component.to_message_format()
            if temp:
                template["components"].append(temp)
        buttons = self.buttons.all()
        if len(buttons) > 0:
            for button in buttons:
                template["components"].append(button.to_message_format())
        return template

class ComponentManager(models.Manager):
    def get_components_by_order(self, template):
        return self.filter(template=template).order_by('type')

class Component(models.Model):
    """
    Represents a component within a WhatsApp template (header, body, or footer).
    
    Components can contain text with parameters and are ordered based on their type.
    
    Attributes:
        id (UUID): Unique identifier for the component
        template (Template): Associated template
        type (str): Component type (HEADER/BODY/FOOTER)
        format (str): Format specification (optional)
        text (str): Component text content
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(Template, related_name='components', on_delete=models.CASCADE)
    type = models.CharField(max_length=255, choices=ComponentType.choices)
    format = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField(null=True, blank=True)

    objects = ComponentManager()

    class Meta:
        ordering = ['type']


    def __str__(self) -> str:
        return  self.template.name + " - " + self.type + " - " + self.text

    @property
    def parameters(self):
        """Get all parameters for this component"""
        return self.parameters.all()

    @property
    def ordered_parameters(self):
        """Get parameters ordered by index"""
        return self.parameters.all().order_by('index')

    def to_whatsapp_format(self):
        component_dict = {
            "type": self.type,
            "text": self.text
        }
        
        # Add format field if present
        if self.format:
            component_dict["format"] = self.format
        
        return component_dict
    def to_message_format(self):
        component = {}
        
        parameters = self.ordered_parameters
        if len(parameters) > 0:
            component["type"] = self.type
            component["parameters"] = []
            for parameter in parameters:
                temp = parameter.to_message_format()
                if temp:
                    component["parameters"].append(temp)
            return component
        else:
            return None

class ParametersManager(models.Manager):
    def get_parameters_by_order(self, component):
        return self.filter(component=component).order_by('index')

class Parameters(models.Model):
    """
    Represents a parameter within a template component.
    
    Parameters allow for dynamic content insertion in templates and can be
    either positional or named.
    
    Attributes:
        id (UUID): Unique identifier for the parameter
        component (Component): Associated component
        name (str): Parameter name
        type (str): Parameter type (TEXT/URL/CURRENCY/MEDIA)
        text_value (str): Default text value (optional)
        index (int): Position index for ordered parameters (optional)
    """
    id =  models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    component = models.ForeignKey(Component, related_name='parameters', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=ParameterType.choices)
    text_value = models.TextField(null=True, blank=True)
    index = models.IntegerField(null=True, blank=True)

    objects = ParametersManager()
    def to_whatsapp_format(self):
        dict = {}
        if self.name:
            dict["name"]= self.name
        if self.type:
            dict["type"]= self.type
        if self.text_value:
            dict["text_value"]= self.text_value
        if self.index:
            dict["index"]= self.index
        return dict
    def to_message_format(self):
        data = {}
        if self.index is not None:
            data["type"] = self.type
            data["text"] = f"{{{{{self.component.type+"_"+str(self.index)}}}}}"
        else:
            data["parameter_name"] = self.name
            data["type"] = self.type
            data["text"] = f"{{{{{self.name}}}}}"
        return data
    def __str__(self) -> str:
        return self.component.template.name + " - " + self.component.type + " - " + self.name + " - " + self.type
    class Meta:
        ordering = ['name']
        verbose_name = 'Parameter'
        verbose_name_plural = 'Parameters'

class Button(models.Model):
    """
    Represents an interactive button in a WhatsApp template.
    
    Templates can have up to 3 buttons of either QUICK_REPLY or URL type.
    
    Attributes:
        id (UUID): Unique identifier for the button
        template (Template): Associated template
        type (str): Button type (QUICK_REPLY/URL)
        text (str): Button text
        url (str): URL for URL-type buttons (optional)
        index (int): Button position index (optional)
    
    Note:
        - Maximum 3 buttons per template
        - URL buttons require a valid URL
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(Template, related_name='buttons', on_delete=models.CASCADE)  # Changed from component to template
    type = models.CharField(max_length=255, choices=ButtonType.choices)
    text = models.CharField(max_length=255)
    url = models.URLField(null=True, blank=True)  # Only for URL type buttons
    index = models.IntegerField(null=True, blank=True)
    # example = models.JSONField(null=True, blank=True)
    def clean(self):
        """
        Validate button data before saving.
        
        Raises:
            ValidationError: If validation fails for:
                - Maximum button count exceeded
                - Missing URL for URL-type buttons
        """
        # Add validation for button limits per template
        button_count = self.template.buttons.count()
        if button_count >= 3:  # WhatsApp typically limits to 3 buttons
            raise ValidationError("Maximum number of buttons reached for this template")
        
        # URL is required for URL type buttons
        if self.type == ButtonType.URL and not self.url:
            raise ValidationError("URL is required for URL type buttons")


    def to_message_format(self):
        button = {}
        button["type"] = "button"
        button["sub_type"] = self.type
        button["index"] = self.index
        button["parameters"] = [{
            "type": "text",
            "text": f"{{{{{"BUTTON_"+str(self.index)}}}}}"
        }]
        return button

    def to_whatsapp_format(self):
        dict = {}
        if self.type == ButtonType.URL:
            
            dict["type"]= self.type
            dict["text"]= self.text
            dict["url"]= self.url
        else:
            dict["type"]= self.type
            dict["text"]= self.text 
        return dict     

    def __str__(self) -> str:
        return self.template.name + " - " + self.type + " - " + self.text
    

    class Meta:
        indexes = [
            models.Index(fields=['template', 'index']),
        ]


