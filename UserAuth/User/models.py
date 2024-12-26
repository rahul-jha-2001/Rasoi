from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db import models
import uuid
from django.core.validators import RegexValidator

# Add phone number validation
phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$', 
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

# Add GST validation
gst_validator = RegexValidator(
    regex=r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$',
    message="Invalid GST Number format"
)
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self,email,password = None,**extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)

        user = self.model(email = email,**extra_fields)
        user.set_password(password)
        user.save(using = self._db)
        return user
    
    def create_superuser(self,email, password = None , **extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        return self.create_user(email,password,**extra_fields)


class Store(AbstractBaseUser,PermissionsMixin):

    StoreUuid = models.UUIDField(
                                primary_key=True, 
                                editable=False, 
                                unique=True,
                                default= uuid.uuid4)


    email = models.EmailField(_("Email"),
                              max_length=254,
                              unique=True)

    PhoneNo = models.CharField(
                                _("Phone Number"),
                                max_length= 13,
                                unique=True,
                                validators = [phone_validator])

    StoreName = models.CharField(
                                _("Store Name"),
                                max_length= 254)
    StoreAddress = models.TextField(_("Address"))
    GST = models.CharField(
                            _("GST Number"),
                            max_length= 15,
                            validators = [gst_validator]
                            )

    is_staff = models.BooleanField(
                                    _("is_staff"),
                                    default = False
                                    )
    is_superuser = models.BooleanField(
                                        _("is_superuser"),
                                        default = False
                                    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    def __str__(self):
        return self.StoreName

class Customer(models.Model):

    CustomUuid = models.UUIDField(null=False,blank= False,default=uuid.uuid4,unique=True)

    Name = models.CharField(
                            _("Username"),
                            max_length= 254)
    
    PhoneNo = models.CharField(
                                _("Phone Number"),
                                max_length= 13)

    logged_in_stores = models.ManyToManyField(Store, 
                                              through='CustomerLogin',
                                              related_name="customers")

    def __str__(self):
        return self.Name

class CustomerLogin(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    
    login_time = models.DateTimeField(auto_now_add=True)  # Timestamp of login


    def __str__(self):
        return f"{self.customer.Name} - {self.store.StoreName}" 
    
    


