#!/usr/bin/env python

import os 
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UserAuth.settings')
django.setup()

call_command("makemigrations","User")
call_command("migrate")