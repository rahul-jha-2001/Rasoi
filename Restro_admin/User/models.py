from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    user_uuid = models.UUIDField( default=uuid.uuid4, editable=False, unique=True)
    phone_no = models.CharField(max_length=16, unique=True, null=True)
    restaurant_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)
    # No need to re-define 'email', 'username', or 'password' here as they're already in AbstractUser
    # You can change USERNAME_FIELD to email if needed
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['restaurant_name', 'username']  # List of fields required during user creation

    def __str__(self):
        return self.email


class Store(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,)
    store_uuid = models.UUIDField(primary_key= True, default=uuid.uuid4, editable=False, unique=True)
    store_name = models.CharField(max_length=255,null=True)
    is_open =  models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)