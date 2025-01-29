from django.contrib import admin
from .models import Template,TemplateVersion,TemplateContent    
# Register your models here.

admin.site.register(Template)
admin.site.register(TemplateVersion)
admin.site.register(TemplateContent)
