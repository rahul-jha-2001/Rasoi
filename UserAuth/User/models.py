
from django.db import models
import uuid
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import TextChoices


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

class StoreRole(TextChoices):
    STORE_ROLE_ADMIN = 'STORE_ROLE_ADMIN', 'STORE_ROLE_ADMIN'
    STORE_ROLE_STAFF = 'STORE_ROLE_STAFF', 'STORE_ROLE_STAFF'

class UserManager(models.Manager):
    pass

class StoreManager(models.Manager):
    def get_stores(self, user_uuid, limit: int = 10, page: int = 1):
        """
        Get paginated stores for a user.
        Args:
            user_uuid (str): UUID of the user.
            limit (int): Number of items per page (1-100).
            page (int): Page number (1+).
        Returns:
            Tuple: (stores queryset, next page number, previous page number)
        """
        # Safe guards
        limit = max(1, min(limit, 100))    # allow between 1 - 100
        page = max(1, page)

        try:
            user = User.objects.get(user_uuid=user_uuid)
        except User.DoesNotExist:
            raise ValidationError(f"User with UUID {user_uuid} does not exist")

        queryset = Store.objects.filter(user=user).order_by('-created_at')
        paginator = Paginator(queryset, limit)

        try:
            paginated_data = paginator.page(page)
        except PageNotAnInteger:
            paginated_data = paginator.page(1)
        except EmptyPage:
            paginated_data = paginator.page(paginator.num_pages)

        next_page = paginated_data.next_page_number() if paginated_data.has_next() else None
        prev_page = paginated_data.previous_page_number() if paginated_data.has_previous() else None

        return paginated_data.object_list, next_page, prev_page




class User(models.Model):

    user_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firebase_uid = models.CharField(max_length=255, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, validators=[phone_validator], unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

class Store(models.Model):
    store_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    gst_number = models.CharField(max_length=15, validators=[gst_validator], unique=True, null=True, blank=True)
    is_active = models.BooleanField("Is Active",default= True)
    is_open = models.BooleanField("Is open",default=False)
    address = models.ForeignKey('Address', on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stores')
    discription = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = StoreManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['user']),
        ]


class Address(models.Model):
    address_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    address_line_1 = models.CharField(max_length=255, null=True, blank=True)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=20, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['state']),
            models.Index(fields=['country']),
        ]