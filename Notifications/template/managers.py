from django.db import models, transaction
from django.core.exceptions import ValidationError


class TemplateVersionManager(models.Manager):
    @transaction.atomic
    def create_version(
        self,
        template,
        template_type: str,
        version_number: int = 1,
        is_current: bool = False,
        status: str = 'DRAFT'
    ):
        """Creates a new template version"""
        try:
            #     # Set all other versions of this type to not current if this is current
            #     if is_current:
            #         self.filter(
            #             template=template,
            #             type=template_type
            #         ).update(is_current=False)

            # Get the latest version number for this template type
            latest_version = self.get_latest_version(template, template_type)
            if latest_version:
                version_number = latest_version.version_number + 1

            return self.create(
                template=template,
                version_number=version_number,
                template_type=template_type,
                is_current=is_current,
                status=status
            )
        except Exception as e:
            raise ValidationError(f"Failed to create template version: {str(e)}")

    def get_latest_version(self, template, template_type):
        return self.filter(
            template=template,
            template_type=template_type
        ).order_by('-version_number').first()

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
    def create_template_with_version_and_content(
        self,
        name: str,
        description: str,
        template_type: str,
        content: dict,
        variables: list,
        version_number: int = 1,
        is_current: bool = True,
        status: str = 'DRAFT'
    ):
        """Creates a complete template with version and content"""
        from models import TemplateVersion, TemplateContent
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
                header=content.get('header', ''),
                body=content.get('body', ''),
                footer=content.get('footer', ''),
                variables=variables
            )

            return template

        except Exception as e:
            raise ValidationError(f"Failed to create template: {str(e)}")

    def create_new_version(
        self,
        template_id,
        template_type: str,
        content: dict,
        variables: list
    ):
        
        """Creates new version for existing template"""
        template = self.get(id=template_id)
        
        # Get latest version number
        latest_version = template.template_version.get_latest_version(
            template=template,
            template_type=template_type
        )
        new_version_number = (latest_version.version_number + 1) if latest_version else 1

        # Create new version
        version = TemplateVersion.objects.create_version(
            template=template,
            template_type=template_type,
            version_number=new_version_number,
            is_current=True
        )

        # Create content
        content = TemplateContent.objects.create(
            template_version=version,
            content=content,
            variables=variables
        )

        return version