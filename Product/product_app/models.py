import uuid
from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import manager
from utils.logger import Logger


logger = Logger()

class ProductStatus(models.TextChoices):
        PRODUCT_STATE_DRAFT = "PRODUCT_STATE_DRAFT","PRODUCT_STATE_DRAFT"
        PRODUCT_STATE_ACTIVE = "PRODUCT_STATE_ACTIVE","PRODUCT_STATE_ACTIVE"
        PRODUCT_STATE_INACTIVE = "PRODUCT_STATE_INACTIVE","PRODUCT_STATE_INACTIVE"
        PRODUCT_STATE_OUT_OF_STOCK = "PRODUCT_STATE_OUT_OF_STOCK","PRODUCT_STATE_OUT_OF_STOCK"


class product_manager(models.Manager):

    def get_products(self,store_uuid:str,category_uuid:str|None,limit:int=10,page:int=0):
        if category_uuid:
            category  = Category.objects.get(store_uuid=store_uuid,category_uuid=category_uuid)
            queryset = self.get_queryset().filter(store_uuid=store_uuid,category = category).order_by('-created_at')
        else:
            queryset = self.get_queryset().filter(store_uuid=store_uuid).order_by('-created_at')
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

class category_manager(models.Manager):
    def get_categories(self,store_uuid:str,limit:int = 10,page:int=1):

        queryset = self.get_queryset().filter(store_uuid=store_uuid).order_by('-created_at')

        paginator = Paginator(object_list = queryset, per_page=limit)
        
        try:
            paginated_data = paginator.page(page)
        except PageNotAnInteger:
            logger.error(f"PageNotInteger")
            paginated_data = paginator.page(1)
        except EmptyPage:
            logger.error(f"Empty Page")
            paginated_data = paginator.page(paginator.num_pages)
       
        next_page = paginated_data.next_page_number() if paginated_data.has_next() else None
        prev_page = paginated_data.previous_page_number() if paginated_data.has_previous() else None

        return paginated_data.object_list, next_page, prev_page  
    
class add_on_manager(models.Manager):
    def get_add_ons(self,product,limit:int = 10,page:int=1):

        queryset = self.get_queryset().filter(product=product).order_by('-created_at')
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
class diet_pref_manager(models.Manager):
    def get_dietary_prefs(self,store_uuid,limit:int = 10,page:int=1):

        queryset = self.get_queryset().filter(store_uuid=store_uuid).order_by('-created_at')
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
class BaseModel(models.Model):

    """
    Abstract base Models with common Fields for all models
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True
class DietaryPreference(BaseModel):
    
    store_uuid = models.UUIDField(null=False, blank=True)
    diet_pref_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50,blank=False)
    description = models.TextField(blank=True)
    icon_url = models.URLField(null=True, blank=True)

    objects = diet_pref_manager()

    def __str__(self):
        return self.name

    def  clean(self):
        if self.store_uuid is None:
            raise ValidationError("Store UUID cannot be null.")
        if self.name is None or self.name == "":
            raise ValidationError("Name cannot be null.")
        if self.description is None or self.description == "":
            raise ValidationError("Description cannot be null.")
        return super().clean()
    def save(self, *args, **kwargs):
        # Run full validation before saving
        self.full_clean()  # <-- this calls `clean()` and field validators
        super().save(*args, **kwargs)  # Call the real save() method
    class Meta:
        verbose_name = 'Dietary Preference'
        verbose_name_plural = 'Dietary Preferences'
        ordering = ['name']
        indexes = [
            models.Index(fields=['diet_pref_uuid']),
            models.Index(fields=['store_uuid']),
            models.Index(fields=['name']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['store_uuid', 'name'], name='unique_store_uuid_name')
        ]

class Category(BaseModel):

    """
    Simple category model for restaurant menu sections
    """
    category_uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    store_uuid = models.UUIDField(null=False, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Order in which category appears in menu"
    )
    is_available = models.BooleanField(
        default=True,
        help_text="Whether this category is currently available"
    )

    objects = category_manager()

    def clean(self):
        if self.store_uuid is None:
            raise ValidationError("Store UUID cannot be null.")
        if self.name is None or self.name == "":
            raise ValidationError("Name cannot be null.")
        if self.description is None or self.description == "":
            raise ValidationError("Description cannot be null.")
        if self.display_order is None or self.display_order < 0:
            raise ValidationError("Display order Invalid.")
        return super().clean()
    def save(self, *args, **kwargs):
        # Run full validation before saving
        self.full_clean()  # <-- this calls `clean()` and field validators
        super().save(*args, **kwargs)  # Call the real save() method
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['store_uuid']),
            models.Index(fields=['category_uuid']),
        ]
        constraints = [
        models.UniqueConstraint(
            fields=['store_uuid', 'display_order'],
            name='unique_display_order_per_store'
        ),
    ]

class Product(BaseModel):    
    product_uuid = models.UUIDField(
        primary_key= True,
        default=uuid.uuid4,
        editable=False,
        unique=True)  # Auto-generated primary key
    store_uuid = models.UUIDField(
        null=False,
        blank=True)  #models.ForeignKey(store_model,on_delete=models.CASCADE,related_name="Products")
    name =  models.CharField(max_length= 255)
    description =  models.TextField()
    status = models.CharField(
        max_length=30,
        choices = ProductStatus.choices,
        default = ProductStatus.PRODUCT_STATE_DRAFT
    )

    dietary_prefs = models.ManyToManyField(DietaryPreference, related_name="products")

    is_available =  models.BooleanField(default=True)
    
    display_price = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        validators=[MinValueValidator(0)])
    
    price = models.DecimalField(
        max_digits=6,
        decimal_places=3,
        validators=[MinValueValidator(0)])

    GST_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators= [
            MinValueValidator(0),
            MaxValueValidator(100)
                     ])
    
    packaging_cost = models.DecimalField(default=0.00,
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)])
    
    category = models.ForeignKey(Category, 
                                 on_delete=models.CASCADE,
                                 null= False,
                                 blank=False, 
                                 related_name="products", 
                                 verbose_name="Category")  
    image_url = models.URLField(null=True,blank=True)

    objects = product_manager()

    def __str__(self):
        return "-".join([self.name,str(self.product_uuid)]) 

    def clean(self):
        if self.store_uuid is None:
            raise ValidationError("Store UUID cannot be null.")
        if self.name is None or self.name == "":
            raise ValidationError("Name cannot be null.")
        if self.description is None or self.description == "":
            raise ValidationError("Description cannot be null.")
        if self.price is None or self.price < 0:
            raise ValidationError("Price Invalid.")
        if self.GST_percentage is None or self.GST_percentage < 0 or self.GST_percentage > 100:
            raise ValidationError("GST percentage Invalid.")
        return super().clean()

    def save(self, *args, **kwargs):
        # Run full validation before saving
        self.full_clean()  # <-- this calls `clean()` and field validators
        super().save(*args, **kwargs)  # Call the real save() method
    class Meta:
        verbose_name = "Product",
        verbose_name_plural = "Products"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=['product_uuid']),
            models.Index(fields=['store_uuid']), 
            models.Index(fields=['category']),
            models.Index(fields=['name', 'description']),
            models.Index(fields=['status', 'is_available']),
        ]

class Add_on(BaseModel):
    
    """
    Product Add-Ons

    """

    add_on_uuid = models.UUIDField(primary_key=True,
                                  default=uuid.uuid4,
                                  editable=False,
                                  unique=True)  
    product = models.ForeignKey('product',
                                on_delete=models.CASCADE,
                                related_name="add_on",
                                verbose_name="Product")
    name = models.CharField(max_length=100,
                            verbose_name="Customization Name")  # e.g., "Extra Cheese", "Spicy Sauce"
    is_available = models.BooleanField(default=True,
                                      verbose_name="Available")  # Can be disabled if not available
    
    max_selectable = models.IntegerField(default=1,
                                        verbose_name="Max Selectable")  # e.g., max 2 toppings of this type
    
    GST_percentage = models.DecimalField(max_digits=5,
                                        decimal_places=3,
                                        default=0.00,
                                        validators=[MinValueValidator(0)])
    price = models.DecimalField(max_digits=6,
                                decimal_places=3,
                                default=0.00,
                                validators=[MinValueValidator(0)],
                                verbose_name="Additional Price")  # Extra cost
    is_free = models.BooleanField(default=False,
                                verbose_name="Is Free")  # If True, price is ignored

    def __str__(self):
        return f"{self.name} (Product: {self.product.name})"

    def clean(self):
        if self.product is None:
            raise ValidationError("Product cannot be null.")
        if self.name is None or self.name == "":
            raise ValidationError("Name cannot be null.")
        if self.is_available is None:
            raise ValidationError("Availability cannot be null.")
        if self.max_selectable is None or self.max_selectable < 0:
            raise ValidationError("Max selectable Invalid.")
        if self.price is None or self.price < 0:
            raise ValidationError("Price Invalid.")
        if self.GST_percentage is None or self.GST_percentage < 0 or self.GST_percentage > 100:
            raise ValidationError("GST percentage Invalid.")
        if self.is_free and self.price > 0:
            raise ValidationError("Price cannot be greater than 0 if is_free is True.")
        return super().clean()
    
    def save(self, *args, **kwargs):
        # Run full validation before saving
        self.full_clean()  # <-- this calls `clean()` and field validators
        super().save(*args, **kwargs)  # Call the real save() method

    objects = add_on_manager()
    class Meta:
        verbose_name = "Add-On"
        verbose_name_plural = "Add-Ons"
        ordering = ["name"]
        indexes = [
            models.Index(fields=['add_on_uuid']),
            models.Index(fields=['product']),
        ]


