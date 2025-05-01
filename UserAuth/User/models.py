
from django.db import models
import uuid
from django.core.validators import RegexValidator

# Validators remain the same
phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$', 
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

gst_validator = RegexValidator(
    regex=r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$',
    message="Invalid GST Number format"
)

password_validator = RegexValidator(
    regex=r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
    message="Password must be at least 8 characters long and contain both letters and numbers."
)


class User(models.Model):

    user_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firebase_uid = models.CharField(max_length=255, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, validators=[phone_validator], unique=True, null=True, blank=True)


class Store(models.Model):
    store_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    gst_number = models.CharField(max_length=15, validators=[gst_validator], unique=True, null=True, blank=True)
    address = models.ForeignKey(address,on_delete =models.SET_NULL,related_name="address")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stores')

class address(models.Model):

    address_uuid = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=True)
    address_line_1 = models.CharField(max_length= 510,null=False,blank= True)
    address_line_2 = models.CharField(max_length= 510,null=False,blank= True)
    landmark  = models.CharField(max_length=255,null=True,blank=True)
    city = models.CharField(max_length=255,null=True)
    state = models.CharField(max_length=255,null=True)
    pincode = models.CharField(max_length=6)
    country = models.CharField(max_length= 255,blank=True,null=True)



    

