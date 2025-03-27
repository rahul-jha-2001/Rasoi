from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext as _
from decimal import Decimal
import uuid
from typing import Dict, Any
# Create your models here.
class Order(models.Model):
    class OrderTypes(models.IntegerChoices):
        ORDER_TYPE_UNSPECIFIED = 0,_("ORDER_TYPE_UNSPECIFIED")
        ORDER_TYPE_DINE_IN = 1,_("ORDER_TYPE_DINE_IN")
        ORDER_TYPE_TAKE_AWAY = 2,_("ORDER_TYPE_TAKE_AWAY")
        ORDER_TYPE_DRIVE_THRU = 3,_("ORDER_TYPE_DRIVE_THRU")
    class OrderState(models.IntegerChoices):
        ORDER_STATE_UNSPECIFIED = 0,_("ORDER_STATE_UNSPECIFIED")
        ORDER_STATE_PAYMENT_PENDING = 1,_("ORDER_STATE_PAYMENT_PENDING")
        ORDER_STATE_COMPLETE = 2,_("ORDER_STATE_COMPLETE")
        ORDER_STATE_CANCELED = 3,_("ORDER_STATE_CANCELED")
        ORDER_STATE_PLACED = 4,_("ORDER_STATE_PLACED")
    class PaymentState(models.IntegerChoices):
        PAYMENT_STATE_UNSPECIFIED = 0,_("PAYMENT_STATE_UNSPECIFIED")
        PAYMENT_STATE_COMPLETE = 1,_("PAYMENT_STATE_COMPLETE")
        PAYMENT_STATE_FAILED = 2,_("PAYMENT_STATE_FAILED")
        PAYMENT_STATE_PENDING = 3,_("PAYMENT_STATE_PENDING")
    #Data Present in CartResponse 

    OrderUuid = models.UUIDField(db_index=True,default=uuid.uuid4)
    StoreUuid = models.UUIDField(name="StoreUuid",db_index=True)
    UserPhoneNo = models.CharField(max_length = 12,null=False,blank= False,verbose_name=_("Phone Number"))
    OrderType = models.IntegerField(choices=OrderTypes.choices,default=OrderTypes.ORDER_TYPE_DINE_IN,verbose_name=_("Order type"))
    TableNo = models.CharField(max_length=4,null=True,blank=True,verbose_name=_("Table No"))
    VehicleNo = models.CharField(max_length=10,null=True,blank=True,verbose_name=_("Vehicle No"))
    VehicleDescription = models.CharField(max_length=50,null=True,blank=True,verbose_name=_("Vehicle Description"))
    CouponName = models.CharField(max_length=20,null=True,blank= True,verbose_name=_("coupone"))
    TotalAmount = models.DecimalField(max_digits=6,decimal_places=2,blank= True,default=Decimal("0.00"),verbose_name= _("Total Amount"))
    DiscountAmount = models.DecimalField(max_digits=6,decimal_places=2,blank= True,default=Decimal("0.00"),verbose_name= _("Discounted Amount"))
    FinalAmount = models.DecimalField(max_digits=6,decimal_places=2,blank= True,default=Decimal("0.00"),verbose_name= _("Final Amount"))

    PaymentStatus = models.IntegerField(choices=PaymentState.choices,default=PaymentState.PAYMENT_STATE_PENDING,verbose_name=_("Payment Status"))
    PaymentMethod = models.CharField(max_length=50, verbose_name=_("Payment Method"))

    SpecialInstruction = models.TextField(null=True, blank=True, verbose_name=_("Special Instructions"))
    #EstimatedDeliveryTime = models.DateTimeField(null=True, blank=True, verbose_name=_("Estimated Delivery Time"))

    OrderStatus = models.IntegerField(choices=OrderState.choices,default=OrderState.ORDER_STATE_PAYMENT_PENDING,verbose_name=_("Order Status"))


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        unique_together = ("StoreUuid", "UserPhoneNo", "OrderUuid")  # Unique for StoreUuid, UserPhoneNo, and OrderUuid

    def __str__(self):
        return f"{self.UserPhoneNo}/{self.StoreUuid}/{self.OrderStatus}"
    
        

class OrderItem(models.Model):
    Order = models.ForeignKey(Order,on_delete= models.CASCADE,name="Order",related_name="Items")
    ProductUuid = models.UUIDField(name=_("ProductUuid"))
    Price = models.DecimalField(max_digits=6,decimal_places=2,name=_("Price"),default=Decimal("0.00"),blank=True)
    Quantity = models.IntegerField(default=1,blank=True)
    Discount = models.DecimalField(max_digits=5,decimal_places = 2,default=Decimal("0.00"),
                                validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100.00"))],
                                verbose_name=_("Discount Percentage"))
    Tax = models.DecimalField(max_digits=5,decimal_places=2,default=Decimal("0.00"),
                              validators=[MinValueValidator(Decimal("0")),
                                          MaxValueValidator(Decimal("100.00"))],
                                verbose_name=_("Discount Percentage"))
    Subtotal = models.DecimalField(verbose_name=_("Subtotal"),max_digits=6,decimal_places=2,default=Decimal("0.00"))
    TaxedAmount = models.DecimalField(verbose_name=_("TaxedAmount"),max_digits=6,decimal_places=2,default=Decimal("0.00"))
    DiscountAmount = models.DecimalField(verbose_name=_("DiscountAmount"),max_digits=6,decimal_places=2,default=Decimal("0.00"))
    class Meta:
        unique_together = ["Order","ProductUuid"]
