from django.db import models,transaction
import uuid 
# from managers import TemplateManager, TemplateVersionManager, TemplateContentManager
from django.core.exceptions import ValidationError
from utils.logger import Logger

logger = Logger(__name__)
"""Managers"""
class TemplateVersionManager(models.Manager):

    def get_latest_version(self, template, channel):
        logger.debug(f"Getting latest version for template {template} and channel {channel}")
        version = self.filter(
            template=template,
            channel=channel
        ).order_by('-version_number').first()
        logger.debug(f"Latest version found: {version}")
        return version
    def get_latest_active_version(self, template, channel):
        logger.debug(f"Getting latest version for template {template} and channel {channel}")
        version = self.filter(
            template=template,
            channel=channel,
            status='ACTIVE',
            is_current=True
        ).order_by('-version_number').first()
        logger.debug(f"Latest active version found: {version}")
        return version
    
    @transaction.atomic
    def create_version(
        self,
        template,
        channel: str,
        is_current: bool = False,
        status: str = 'DRAFT'
    ):
        logger.info(f"Creating new version for template {template} with channel {channel}")
        """Creates a new template version"""
        try:
            # Get the latest version number for this template type
            latest_version = self.get_latest_version(template, channel)
            logger.debug(f"Latest Version: {latest_version}")
            if latest_version:
                version_number = latest_version.version_number + 1
            else:
                version_number = 1
            version = self.create(
                template=Template.objects.get(id=template),
                version_number=version_number,
                channel=channel,
                is_current=is_current,
                status=status
            )
            logger.info(f"Successfully created template version {version_number} for template {template}")
            return version
        except Exception as e:
            logger.error(f"Failed to create template version: {str(e)}")
            raise ValidationError(f"Failed to create template version: {str(e)}")



class TemplateContentManager(models.Manager):
    @transaction.atomic
    def create_content(
        self,
        template_version,
        content: dict,
        variables: dict
    ):
        logger.info(f"Creating content for template version {template_version}")
        """Creates template content with variables"""
        try:
            template_content = self.create(
                template_version=template_version,
                header=content.get('header', ''),
                body=content.get('body', ''),
                footer=content.get('footer', ''),
                variables=variables
            )
            logger.info(f"Successfully created template content for version {template_version}")
            return template_content
        except Exception as e:
            logger.error(f"Failed to create template content: {str(e)}")
            raise ValidationError(f"Failed to create template content: {str(e)}")

class TemplateManager(models.Manager):

    
    @transaction.atomic
    def create_new_template(
        self,
        name: str,
        description: str,
        category: str,
        channel: str,
        header: str,
        body: str,
        footer: str,
        variables: dict,
        version_number: int = 1,
        is_current: bool = True,
        status: str = 'DRAFT'
    ):
        logger.info(f"Creating new template with name: {name}")
        """Creates a complete template with version and content"""
        try:
            # Create base template
            template = super().create(
                name=name,
                description=description,
                category=category,
                status=status
            )

            # Create version using VersionManager
            version = TemplateVersion.objects.create(
                template=template,
                version_number=version_number,
                channel=channel,
                is_current=is_current,
                status=status
            )

        
            # Create content using ContentManager
            content = TemplateContent.objects.create(
                template_version=version,
                header=header,
                body=body,
                footer=footer,
                variables=variables
            )

            logger.info(f"Successfully created template {template.id} with initial version")
            return template

        except Exception as e:
            logger.error(f"Failed to create template: {str(e)}")
            raise ValidationError(f"Failed to create template: {str(e)}")

    @transaction.atomic
    def create_new_version(
        self,
        template_id:str,
        channel: str,
        header: str,
        body: str,
        footer: str,
        variables: dict,
        status: str = 'DRAFT'
    ):
        logger.info(f"Creating new version for template {template_id}")
        """Creates new version for existing template"""
        if not template_id:
            logger.error("Template ID is required")
            raise ValidationError("Template ID is required")
        
        try:
            template = self.get(id=template_id)
      
            # Create new version
            version = TemplateVersion.objects.create_version(
                template=template.id,
                channel=channel,
                is_current=True,
                status=status
            )

            # Create content
            content = TemplateContent.objects.create(
                template_version=version,
                header=header,
                body=body,
                footer=footer,   
                variables=variables
            )

            logger.info(f"Successfully created new version {version.version_number} for template {template_id}")
            return version
        except Exception as e:
            logger.error(f"Failed to create new version: {str(e)}")
            raise ValidationError(f"Failed to create new version: {str(e)}")


    """
    
    Models
    
    
    """

class TemplateStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'
    DELETED = 'DELETED', 'Deleted'
    DRAFT = 'DRAFT', 'Draft'
    DEPRECATED = 'DEPRECATED', 'Deprecated'

class TemplateChannel(models.TextChoices):
    EMAIL = 'EMAIL', 'Email'
    SMS = 'SMS', 'SMS'
    PUSH = 'PUSH', 'Push'
    INAPP = 'INAPP', 'In-App'
    WHATSAPP = 'WHATSAPP', 'Whatsapp'

class TemplateCategory(models.TextChoices):
    AUTHENTICATION = 'AUTHENTICATION', 'Authentication'
    PROMOTIONAL = 'PROMOTIONAL', 'Promotional'
    TRANSACTIONAL = 'TRANSACTIONAL', 'Transactional'

class Template(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,primary_key=True)
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField()
    status = models.CharField(max_length=225,choices=TemplateStatus.choices,default=TemplateStatus.DRAFT)
    category = models.CharField(max_length=225,choices=TemplateCategory.choices,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TemplateManager()

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']

class TemplateVersion(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,primary_key=True)
    template = models.ForeignKey(Template,on_delete=models.CASCADE,related_name="template_version")
    version_number = models.PositiveIntegerField()
    status = models.CharField(max_length=10,choices=TemplateStatus.choices,default=TemplateStatus.DRAFT)
    channel = models.CharField(max_length=10,choices=TemplateChannel.choices,default=TemplateChannel.EMAIL)
    is_current = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    changelog = models.TextField(blank=True,null=True)

    objects = TemplateVersionManager()

    def __str__(self):
        return f"{self.template.name}-{self.channel} - Version {self.version_number}"

    class Meta:
        ordering = ['-created_at']

class TemplateContent(models.Model):
    
    template_version = models.OneToOneField(TemplateVersion,on_delete=models.CASCADE,related_name="template_content")
    header = models.TextField()
    body = models.TextField()
    footer = models.TextField()
    variables = models.JSONField(default=dict,help_text= "JSON object with variable names as keys and descriptions as values")
    

    objects = TemplateContentManager()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return f"{self.template_version.template.name} - Version {self.template_version.version_number}"




