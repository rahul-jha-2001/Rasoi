import uuid
from django.db import models



class Category(models.Model):


    StoreUuid = models.UUIDField(null=False, blank=True)
    CategoryUuid = models.UUIDField(primary_key= True,default=uuid.uuid4, editable=False,unique=True)  # Auto-generated primary key
    Name = models.CharField(max_length=100)
    Description = models.TextField()
    Parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='subcategories', verbose_name="Parent Category")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.Name

    class Meta:
        indexes = [
            models.Index(fields=['StoreUuid']),
            models.Index(fields=['CategoryUuid']),
        ]

class Product(models.Model):
    
    
    ProductUuid = models.UUIDField( primary_key= True,default=uuid.uuid4, editable=False,unique=True)  # Auto-generated primary key
    StoreUuid = models.UUIDField(null=False, blank=True)  #models.ForeignKey(store_model,on_delete=models.CASCADE,related_name="Products")
    Name =  models.CharField(max_length= 255)
    IsAvailable =  models.BooleanField(default=True)
    Price = models.DecimalField(max_digits=6,decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT,null= False,blank=False, related_name="products", verbose_name="Category")  
    Description =  models.TextField()
    ImageUrl = models.CharField(max_length=255,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




    def __str__(self):
        return self.Name
    class Meta:
        indexes = [
            models.Index(fields=['ProductUuid']),  # Faster queries when filtering by store
            models.Index(fields=['StoreUuid'])  # For quick lookup of categories by UUID
        ]

# class review_model(models.Model):

#     product_uuid =  models.ForeignKey(product_model,on_delete= models.CASCADE,related_name= "product",null = False)
#     points =  models.IntegerField()
#     reviwer = models.CharField(max_length= 255)
#     reviwer_number = models.CharField(max_length=16)
#     feedback =  models.TextField()


