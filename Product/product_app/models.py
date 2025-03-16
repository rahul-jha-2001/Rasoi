import uuid
from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import manager
from utils.logger import Logger


logger = Logger()

class product_manager(models.Manager):

    def get_products(self,store_uuid:str,category_uuid:str,limit:int=10,page:int=0):
        queryset = self.get_queryset().filter(store_uuid=store_uuid,category_uuid=category_uuid).order_by('-created_at')
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
class BaseModel(models.Model):

    """
    Abstract base Models with common Fields for all models
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

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

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['store_uuid']),
            models.Index(fields=['category_uuid']),
        ]

class Product(BaseModel):

    class Status(models.TextChoices):
        DRAFT = "DRAFT","Draft"
        ACTIVE = "ACTIVE","Active"
        INACTIVE = "INACTIVE","Active"
    
    class DietPref(models.TextChoices):
        VEG = "VEG"
        NONVEG = "NONVEG"
        VEGAN = "VEGAN"
        JAIN = "JAIN"    
    
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
        max_length=10,
        choices=Status.choices,
        default= Status.DRAFT
    )

    is_available =  models.BooleanField(default=True)
    
    #Price To display as Discounted
    display_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)])
    
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)])

    GST_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators= [
            MinValueValidator(0),
            MaxValueValidator(100)
                     ])
    
    category = models.ForeignKey(Category, 
                                 on_delete=models.PROTECT,
                                 null= False,
                                 blank=False, 
                                 related_name="products", 
                                 verbose_name="Category")  
    
    dietary_pref = models.CharField(max_length=10,choices=DietPref.choices,default=DietPref.VEG,verbose_name="Dietary_Preference")

    image_url = models.URLField(null=True,blank=True)

    objects = product_manager()

    def __str__(self):
        return "-".join([self.name,str(self.product_uuid)]) 

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
                                        decimal_places=2)
    price = models.DecimalField(max_digits=6,
                                decimal_places=2,
                                default=0.00,
                                validators=[MinValueValidator(0)],
                                verbose_name="Additional Price")  # Extra cost
    

    def __str__(self):
        return f"{self.name} (Product: {self.product.name})"

    objects = add_on_manager()
    class Meta:
        verbose_name = "Add-On"
        verbose_name_plural = "Add-Ons"
        ordering = ["name"]
        indexes = [
            models.Index(fields=['add_on_uuid']),
            models.Index(fields=['product']),
        ]

# class review_model(models.Model):

#     product_uuid =  models.ForeignKey(product_model,on_delete= models.CASCADE,related_name= "product",null = False)
#     points =  models.IntegerField()
#     reviwer = models.CharField(max_length= 255)
#     reviwer_number = models.CharField(max_length=16)
#     feedback =  models.TextField()


