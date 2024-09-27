import uuid
from django.db import models



class category_model(models.Model):


    store_uuid = models.UUIDField(null=False, blank=True)
    category_uuid = models.UUIDField(primary_key= True,default=uuid.uuid4, editable=False,unique=True)  # Auto-generated primary key
    name = models.CharField(max_length=100)
    description = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='subcategories')

    def __str__(self):
        return self.name

class product_model(models.Model):
    
    
    product_uuid = models.UUIDField( primary_key= True,default=uuid.uuid4, editable=False,unique=True)  # Auto-generated primary key
    store_id = models.UUIDField(null=False, blank=True)  #models.ForeignKey(store_model,on_delete=models.CASCADE,related_name="Products")
    name =  models.CharField(max_length= 255)
    is_available =  models.BooleanField(default=True)
    price = models.DecimalField(max_digits=6,decimal_places=2)
    category =  models.ForeignKey(category_model,on_delete=models.PROTECT,related_name="products",null=True,blank=True)
    description =  models.TextField()
    image =  models.ImageField(upload_to="products/imgs", blank=True, null=True)
    
    def __str__(self):
        return self.name

# class review_model(models.Model):

#     product_uuid =  models.ForeignKey(product_model,on_delete= models.CASCADE,related_name= "product",null = False)
#     points =  models.IntegerField()
#     reviwer = models.CharField(max_length= 255)
#     reviwer_number = models.CharField(max_length=16)
#     feedback =  models.TextField()


