from django.contrib import admin
from .models import Template,Component,Button,Parameters   
# Register your models here.

admin.site.register(Template)
admin.site.register(Component)
admin.site.register(Button)
admin.site.register(Parameters)


