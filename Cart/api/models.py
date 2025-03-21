from django.db import models
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger,Page
from django.db.models import manager
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
import uuid
import datetime

from typing import Dict, Any


class coupon_manager(models.Manager):
    def get_coupons(self,store_uuid:str,limit:int=10,page:int=1) -> tuple[Page,int,int]:
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

class coupon_usage_manager(models.Manager) :
    def get_coupon_usage(self,coupon,limit:int=10,page:int=1)-> tuple[Page,int,int]:
        queryset = self.get_queryset().filter(coupon=coupon).order_by('-used_at')
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
class Cart(models.Model):
    class order_types(models.TextChoices):
        Unspecified = "UNSPECIFIED",_("Unspecified")
        DineIn ="DINEIN",_("DineIn")
        TakeAway = "TAKEAWAY",_("TakeAway")
        DriveThru = "DRIVETHRU",_("DriveThru")
    
    class cart_state(models.TextChoices):
        Unspecified_State = "UNSPECIFIED_STATE",_("Unspecified_State")
        Active = "ACTIVE",_("Active")
        Completed = "COMPLETED",_("Completed")
        Abandoned = "ABANDONED",_("Abandoned")

    store_uuid = models.UUIDField(db_index=True)
    cart_uuid = models.UUIDField(default=uuid.uuid4,db_index=True)
    user_phone_no = models.CharField(max_length = 12,null=False,blank= False,verbose_name=_("Phone Number"))
    order_type = models.CharField(max_length=15,choices=order_types.choices,default=order_types.DineIn,verbose_name=_("Order type"))
    table_no = models.CharField(max_length=4,null=True,blank=True,verbose_name=_("Table No"))
    vehicle_no = models.CharField(max_length=10,null=True,blank=True,verbose_name=_("Vehicle No"))
    vehicle_description = models.CharField(max_length=50,null=True,blank=True,verbose_name=_("Vehicle Description"))
    coupon_code = models.CharField(max_length=20,null=True,blank= True,verbose_name=_("coupone"))
    speacial_instructions = models.TextField(verbose_name="speacial instructions",null=True,blank=True)
    state = models.CharField(max_length=20,verbose_name = "State",choices = cart_state.choices,default = cart_state.Active)
    # TotalAmount = TextChoices.DecimalField(max_digits=6,decimal_places=2,blank= True,default=Decimal("0.00"),verbose_name= _("Total Amount"))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")
        unique_together = ["store_uuid","user_phone_no"]

    def __str__(self):
        return self.user_phone_no
    
    @property
    def total_subtotal(self)->Decimal:
        return Decimal(sum(item.subtotal_amount for item in self.items.all()))

    @property
    def total_discount(self) -> Decimal:
        return Decimal(sum(item.discount_amount for item in self.items.all()))

    @property
    def total_price_before_tax(self) -> Decimal:
        return Decimal(sum(item.discount_amount for item in self.items.all()))

    @property
    def tax_amount(self) -> Decimal:
        return Decimal(sum(item.discount_amount for item in self.items.all()))

    @property
    def packaging_cost(self) -> Decimal:
        return Decimal(sum(item.packing_cost for item in self.items.all()))
    
    @property
    def final_amount(self) -> Decimal:
        return Decimal(sum(item.final_price for item in self.items.all()))

    @property
    def total_items(self)->int:
        return self.items.count()
    
    def get_items(self)->models.QuerySet:
        return self.items.all()

    def apply_discount(self,discount:Decimal):
        for item in self.get_items():
            item.apply_discount(discount)

    def remove_discount(self):
        for item in self.get_items():
            item.remove_discount()        
    class Meta:
        verbose_name =  'Cart'
        verbose_name_plural = 'Carts'
        indexes = [
            models.Index(fields=["store_uuid","user_phone_no","cart_uuid"])
        ]

class CartItem(models.Model):
    
    cart_item_uuid = models.UUIDField(default=uuid.uuid4,editable=False, unique=True)
    cart = models.ForeignKey(
        "Cart", on_delete=models.CASCADE, related_name="items"
    )
    product_name = models.TextField(verbose_name="Product Name")
    product_uuid = models.UUIDField(verbose_name=_("Product UUID"), db_index=True)
    tax_percentage = models.DecimalField(
        verbose_name="Tax", max_digits=5, decimal_places=2, default=Decimal("0.00")
    )
    packaging_cost = models.DecimalField(
        verbose_name="Packing Cost", max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    discount = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100.00"))],
        verbose_name=_("Discount Percentage")
    )

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        indexes = [
            models.Index(fields=["cart"]),
            models.Index(fields=["product_uuid", "cart_item_uuid"]),
        ]

    @property
    def add_ons_total(self) -> Decimal:
        """Total price of all add-ons linked to this cart item."""
        return sum(addon.subtotal for addon in self.add_ons.all())

    @property
    def subtotal_amount(self) -> Decimal:
        """Total price before discounts, taxes, and including add-ons."""
        return (self.unit_price + self.add_ons_total ) * self.quantity 


    @property
    def discount_amount(self) -> Decimal:
        """Total discount applied to the item"""
        return (self.subtotal_amount * self.discount) / Decimal("100.00")

    @property
    def price_before_tax(self) -> Decimal:
        """Price before tax but after discount"""
        return self.subtotal_amount - self.discount_amount + self.packing_cost

    @property
    def tax_amount(self) -> Decimal:
        """Tax amount calculated on the price before tax"""
        return (self.price_before_tax * self.tax_percentage) / Decimal("100.00")

    @property
    def final_price(self) -> Decimal:
        """Final price after discount and tax"""
        return self.price_before_tax + self.tax_amount


    def add_quantity(self, increment=1):
        if increment < 1:
            raise ValueError("Increment must be positive")
        self.quantity += increment
        self.save()
    
    def remove_quantity(self,decrement = 1):
        if decrement < 1:
            raise ValueError("Decrement must be positive")
        self.quantity -= decrement
        self.save()
    
    def apply_discount(self, discount: Decimal):
        """
        Applies a discount percentage to the cart item.
        
        :param discount: Discount percentage (0-100).
        """
        if discount < Decimal("0") or discount > Decimal("100"):
            raise ValueError("Discount must be between 0 and 100")
        
        self.discount = discount
        self.save()

    def remove_discount(self):
        self.discount = Decimal("0.00")
        self.save()

    def get_add_on(self) -> models.QuerySet: 
        return self.add_ons.all()



class AddOn(models.Model):

    cart_item = models.ForeignKey(CartItem, verbose_name=_("Cart"), on_delete=models.CASCADE,related_name="add_ons")
    add_on_name = models.TextField(verbose_name="AddOn Name")
    add_on_uuid = models.UUIDField(default=uuid.uuid4,verbose_name="AddOn Id")
    quantity =  models.PositiveIntegerField(verbose_name="AddOn Quantity",default=0)
    unit_price = models.DecimalField(decimal_places=2,max_digits=6,verbose_name="AddOn Price",default=0)
    is_free = models.BooleanField(_("Is Free"),default=False)

    
    class Meta:
        verbose_name = 'Add On'
        verbose_name_plural = 'Add Ons'
        indexes = [
            models.Index(fields=['cart_item']),
            models.Index(fields=['add_on_uuid']),
        ]
    
    @property
    def subtotal(self) -> Decimal:
        if self.is_free:
            return Decimal("0.0")
        """Total price of this add-on for the given quantity."""
        return Decimal(self.unit_price * self.quantity)

class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = "PERCENTAGE",_("Percentage")
        FIXED = "FIXED",_("FIXED")
    
    coupon_uuid = models.UUIDField(default=uuid.uuid4,verbose_name = _("Coupon Uuid"))
    store_uuid = models.UUIDField()
    coupon_code = models.CharField(max_length= 10)
    discount_type = models.CharField(max_length=15,choices=DiscountType.choices,default=DiscountType.PERCENTAGE)
    valid_from = models.DateField()
    valid_to = models.DateField()
    usage_limit_per_user = models.PositiveIntegerField(default=1,verbose_name="Usage Limit Per User")
    total_usage_limit = models.PositiveIntegerField(null=True,blank=True,verbose_name= "Total Usage Limit")
    
    discount = models.DecimalField(decimal_places=2,max_digits=6,
        validators=[MinValueValidator(Decimal(0)), MaxValueValidator(Decimal(100))]
    )
    min_spend = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_discount = models.DecimalField(decimal_places=2,max_digits=6,default=Decimal("0.0"),verbose_name="Max Discount")
    is_for_new_users = models.BooleanField(default=False, verbose_name=_("Is for New Users"))
    description = models.TextField(null=True, blank=True, verbose_name=_("Coupon Description"))
    max_cart_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Max Cart Value"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    objects = coupon_manager()

    def __str__(self):
        return self.coupon_code



class CouponUsage(models.Model):

    usage_uuid = models.UUIDField(default=uuid.uuid4,verbose_name="Usage Uuid")
    coupon = models.ForeignKey(Coupon, on_delete=models.DO_NOTHING, related_name="usages")
    user_phone_no = models.CharField(max_length=12, verbose_name=_("User Phone Number"))
    used_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Used At"))
    order_uuid = models.UUIDField(_("Order id"),null=False,blank=True)
        
    objects = coupon_usage_manager()    
    class Meta:
        unique_together = ["coupon", "user_phone_no", "order_uuid"]  # Prevent duplicate usage by user for a single order
        indexes = [
                models.Index(fields=["user_phone_no","coupon","order_uuid"])
        ]

    def __str__(self):
        return f"{self.coupon.coupon_code} used by {self.user_phone_no} on {self.used_at}"
    

class Coupon_Validator:
    
    @staticmethod
    def has_been_used(coupon: Coupon, cart: Cart) -> bool:
        """
        Checks if the user has used the coupon at the store before.
        
        Args:
            coupon: The Coupon instance
            cart: The Cart instance with user information
            
        Returns:
            bool: True if the coupon has been used by this user, False otherwise
        """
        count = CouponUsage.objects.filter(
            coupon=coupon,
            user_phone_no=cart.user_phone_no
            ).count()
        
        return count > 0
    

    @staticmethod
    def has_reached_usage_limit(coupon: Coupon, cart: Cart) -> tuple[bool, str]:
        """
        Checks if the user has reached the usage limit for this coupon.
        
        Args:
            coupon: The Coupon instance
            cart: The Cart instance with user information
            
        Returns:
            tuple: (has_reached_limit, message)
        """
        user_usage_count = CouponUsage.objects.filter(
            coupon=coupon,
            user_phone_no=cart.user_phone_no
            ).count()
        
        if user_usage_count >= coupon.usage_limit_per_user:
            return True, f"You have already used this coupon {user_usage_count} times (limit: {coupon.usage_limit_per_user})"
        
        # Also check total usage limit if it's set
        if coupon.total_usage_limit:
            total_usage_count = CouponUsage.objects.filter(coupon=coupon).count()
            if total_usage_count >= coupon.total_usage_limit:
                return True, "This coupon has reached its maximum usage limit"
        
        return False, ""
    
    @staticmethod
    def validate(coupon:Coupon,cart:Cart):
        """
    Validates if a coupon is applicable to the given cart.
    
    Args:
        cart: The Cart instance to validate against
        
    Returns:
        tuple: (is_valid, message)
    """
        now = datetime.datetime.now().date()
        
        # Calculate cart value
        cart_value = cart.TotalAmount
        
        # Basic validation
        if not coupon.is_active:
            return (False, "This coupon is not active")
            
        if not (coupon.valid_from <= now <= coupon.valid_to):
            if now < coupon.valid_from:
                return (False, "This coupon is not yet valid")
            else:
                return (False, "This coupon has expired")
        
        if coupon.store_uuid != cart.store_uuid:
            return (False, "This coupon is not valid for this store")
        
        # Cart value validation
        if coupon.min_spend > cart_value:
            difference = coupon.min_spend - cart_value
            return (False, f"Add {difference:.2f} to your cart to use this coupon")
        
        if coupon.max_cart_value and cart_value > coupon.max_cart_value:
            return (False, "Your cart value exceeds the maximum allowed for this coupon")
        
        # User validation
        if coupon.is_for_new_users:
            # Logic to check if user is new
            if Coupon_Validator.has_been_used(coupon,cart):
                return(False,"This Coupon Has Been Used")
        
        if coupon.usage_limit_per_user:
            flag,msg = Coupon_Validator.has_reached_usage_limit(coupon,cart)
            if flag:
                return (False,msg)
            
        return (True, "Coupon applied successfully")