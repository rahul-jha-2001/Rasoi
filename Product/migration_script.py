#!/usr/bin/env python

import os 
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Product.settings')
django.setup()

call_command("makemigrations","product_app")
call_command("migrate")