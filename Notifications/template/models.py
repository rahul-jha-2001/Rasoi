from django.db import models,transaction
import uuid 
# from managers import TemplateManager, TemplateVersionManager, TemplateContentManager
from django.core.exceptions import ValidationError
from utils.logger import Logger,log_operation
logger = Logger("template")

"""Managers"""
class TemplateVersionManager(models.Manager):

    def get_latest_version(self, template, template_type):
        return self.filter(
            template=template,
            type=template_type
        ).order_by('-version_number').first()
    
    @transaction.atomic
    def create_version(
        self,
        template,
        template_type: str,
        is_current: bool = False,
        status: str = 'DRAFT'
    ):
        """Creates a new template version"""
        try:
            # Get the latest version number for this template type
            latest_version = self.get_latest_version(template, template_type)
            logger.debug(f"Latest Version: {latest_version}")
            if latest_version:
                version_number = latest_version.version_number + 1
            else:
                version_number = 1
            return self.create(
                template=Template.objects.get(id=template),
                version_number=version_number,
                type=template_type,
                is_current=is_current,
                status=status
            )
        except Exception as e:
            raise ValidationError(f"Failed to create template version: {str(e)}")



class TemplateContentManager(models.Manager):
    @transaction.atomic
    def create_content(
        self,
        template_version,
        content: dict,
        variables: dict
    ):
        """Creates template content with variables"""
        try:
            template_content = self.create(
                template_version=template_version,
                header=content.get('header', ''),
                body=content.get('body', ''),
                footer=content.get('footer', ''),
                variables=variables
            )
            return template_content
        except Exception as e:
            raise ValidationError(f"Failed to create template content: {str(e)}")

class TemplateManager(models.Manager):

    
    @transaction.atomic
    def create_new_template(
        self,
        name: str,
        description: str,
        template_type: str,
        header: str,
        body: str,
        footer: str,
        variables: dict,
        version_number: int = 1,
        is_current: bool = True,
        status: str = 'DRAFT'
    ):
        """Creates a complete template with version and content"""
        try:
            # Create base template
            template = super().create(
                name=name,
                description=description,
                status=status
            )

            # Create version using VersionManager
            version = TemplateVersion.objects.create(
                template=template,
                version_number=version_number,
                type=template_type,
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

            return template

        except Exception as e:
            raise ValidationError(f"Failed to create template: {str(e)}")

    @transaction.atomic
    def create_new_version(
        self,
        template_id:str,
        template_type: str,
        header: str,
        body: str,
        footer: str,
        variables: dict,
        status: str = 'DRAFT'
    ):
        
        """Creates new version for existing template"""
        if not template_id:
            raise ValidationError("Template ID is required")
        
        template = self.get(id=template_id)
      
        # Create new version
        version = TemplateVersion.objects.create_version(
            template=template.id,
            template_type=template_type,
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

        return version


    """
    
    Models
    
    
    """

class TemplateStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'
    DELETED = 'DELETED', 'Deleted'
    DRAFT = 'DRAFT', 'Draft'
    DEPRECATED = 'DEPRECATED', 'Deprecated'

class TemplateType(models.TextChoices):
    EMAIL = 'EMAIL', 'Email'
    SMS = 'SMS', 'SMS'
    PUSH = 'PUSH', 'Push'
    INAPP = 'INAPP', 'In-App'
    WHATSAPP = 'WHATSAPP', 'Whatsapp'

class Template(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True,primary_key=True)
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField()
    status = models.CharField(max_length=10,choices=TemplateStatus.choices,default=TemplateStatus.DRAFT)
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
    type = models.CharField(max_length=10,choices=TemplateType.choices,default=TemplateType.EMAIL)
    is_current = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    changelog = models.TextField(blank=True,null=True)

    objects = TemplateVersionManager()

    def __str__(self):
        return f"{self.template.name}-{self.type} - Version {self.version_number}"

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




