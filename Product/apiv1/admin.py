from django.contrib import admin

# Register your models here.
from .models import product_model,category_model

admin.site.register(product_model)
admin.site.register(category_model)