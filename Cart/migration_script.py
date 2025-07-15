#!/usr/bin/env python

import os 
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Cart.settings')
django.setup()

call_command("makemigrations","api")
# call_command("migrate")