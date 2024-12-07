#!/bin/sh
python manage.py makemigrations
python manage.py makemigrations Order
python manage.py migrate

exec python grpc_serve.py
