#!/bin/sh

python manage.py migrate

exec python serve.py
