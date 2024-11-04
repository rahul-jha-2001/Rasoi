from django.db import models
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

from typing import Dict, Any


class Cart(models.Model):

    class OrderTypes(models.IntegerChoices):
        Unspecified = 0,_("Unspecified")
        DineIn = 1,_("DineIn")
        TakeAway = 2,_("TakeAway")
        DriveThru = 3,_("DriveThru")


    StoreUuid = models.UUIDField(db_index=True)
    UserPhoneNo = models.CharField(max_length = 12,null=False,blank= False,verbose_name=_("Phone Number"))
    OrderType = models.IntegerField(choices=OrderTypes.choices,default=OrderTypes.DineIn,verbose_name=_("Order type"))
    TableNo = models.CharField(max_length=4,null=True,blank=True,verbose_name=_("Table No"))
    VehicleNo = models.CharField(max_length=10,null=True,blank=True,verbose_name=_("Vehicle No"))
    VehicleDescription = models.CharField(max_length=50,null=True,blank=True,verbose_name=_("Vehicle Description"))
    CouponName = models.CharField(max_length=20,null=True,blank= True,verbose_name=_("coupone"))
    # TotalAmount = models.DecimalField(max_digits=6,decimal_places=2,blank= True,default=Decimal("0.00"),verbose_name= _("Total Amount"))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")
        unique_together = ["StoreUuid","UserPhoneNo"]

    def __str__(self):
        return self.UserPhoneNo
    @property
    def TotalAmounts(self)->Decimal:
        return Decimal(sum(item.subtotal for item in self.Items.all()))

    @property
    def TotalItems(self)->int:
        return self.Items.count()
    
    def GetItems(self)->models.QuerySet:
        return self.Items.all()

    
    def ApplyDiscount(self,Discount=0.00):
        #later upgrade to Discount for specific ProductUuid
        #ProdDiscount = {productUuid,Discount}
        for item in self.Items.all():
            item.Discount = Discount
            item.save()        
    

class CartItem(models.Model):
    
    Cart =  models.ForeignKey(Cart,on_delete= models.CASCADE,name="CartId",related_name="Items")
    ProductUuid =  models.UUIDField(verbose_name=_("Product UUID"),db_index=True)
    Price =  models.DecimalField(max_digits = 6,decimal_places=2)
    Quantity = models.PositiveIntegerField(default=1)
    Discount = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"),
                                validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100.00"))],
                                verbose_name=_("Discount Percentage"))
    class Meta:
        unique_together = ["CartId","ProductUuid"]
    
    @property
    def subtotal(self):
        discount_factor = (Decimal('100.00') - self.Discount) / Decimal('100.00')
        return (self.Price * self.Quantity * discount_factor) 

    def add_quantity(self, increment=1):
        if increment < 1:
            raise ValueError("Increment must be positive")
        self.Quantity += increment
        self.save()
    
    def remove_quantity(self,decrement = 1):
        if decrement < 1:
            raise ValueError("Decrement must be positive")
        self.Quantity -= decrement
        self.save()
    
class Coupon(models.Model):
    StoreUuid = models.UUIDField(db_index=True)
    CouponCode = models.CharField(max_length= 50)
    VaildFrom = models.DateField()
    VaildTo = models.DateField()
    Discount = models.DecimalField(decimal_places=2,max_digits=6,
        validators=[MinValueValidator(Decimal(0)), MaxValueValidator(Decimal(100))]
    )
    MinSpend = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    # MinQuantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.CouponCode

    def is_Vaild(self,Cart):
        import datetime
        now = datetime.datetime.now()
        CartValue = Decimal(sum(Item.Price*Item.Quantity for Item in Cart.Items.all()))
        if not self.VaildFrom < now.date():
            return (False,"The coupon is Not Valid")
        if not self.VaildTo > now.date():
            return (False,"The coupon is Has Expired")
        if not self.StoreUuid == Cart.StoreUuid:
            return (False,"The coupon is Not Valid")
        if not self.MinSpend <= CartValue:
            return (False,f"Add {self.MinSpend-CartValue} To the Cart")
        
        return (True,"Coupon Applied")
    