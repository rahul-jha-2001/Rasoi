from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    UserUuid = models.UUIDField( default=uuid.uuid4, editable=False, unique=True)
    PhoneNo = models.CharField(max_length=16, unique=True, null=True)
    RestaurantName = models.CharField(max_length=255, blank=True)
    Email = models.EmailField(unique=True,null=True)
    # No need to re-define 'email', 'username', or'password' here as they're already in AbstractUser
    # You can change USERNAME_FIELD to email if needed
    USERNAME_FIELD = 'Email'
    REQUIRED_FIELDS = ['PhoneNo']  # List of fields required during user creation

    def __str__(self):
        return str(self.Email)
    def get_Uuid(self):
        return self.UserUuid
