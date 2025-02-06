from django.contrib import admin

# Register your models here.
from .models import Message,InvalidMessage

admin.site.register(Message)

admin.site.register(InvalidMessage)

