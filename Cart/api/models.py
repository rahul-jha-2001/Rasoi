from django.db import models
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger,Page
from django.db.models import manager
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError,ObjectDoesNotExist
from decimal import Decimal
import uuid
import datetime
import phonenumbers
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

        return list(paginated_data.object_list), next_page, prev_page

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

class cart_manager(models.Manager):
    def filter_active_carts(self,cart_uuid:str|None = None,store_uuid:str|None = None,user_phone_no:str|None = None):

        """Returns all carts that are currently active."""
        if cart_uuid:
            return self.filter(cart_uuid=cart_uuid,state=Cart.cart_state.CART_STATE_ACTIVE)
        if store_uuid and user_phone_no:
            return self.filter(
                store_uuid=store_uuid,
                user_phone_no=user_phone_no,
                state=Cart.cart_state.CART_STATE_ACTIVE
            )
    def filter_all_carts(self,store_uuid:str|None = None):
        """Returns all carts, regardless of their state."""
        return self.filter(store_uuid = store_uuid)
    
    def get_active_cart(self,cart_uuid:str|None = None,store_uuid:str|None = None,user_phone_no:str|None = None):

        """Returns all carts that are currently active."""
        if cart_uuid:
            return self.get(cart_uuid=cart_uuid,state=Cart.cart_state.CART_STATE_ACTIVE)
        if store_uuid and user_phone_no:
            return self.get(
                store_uuid=store_uuid,
                user_phone_no=user_phone_no,
                state=Cart.cart_state.CART_STATE_ACTIVE
            )

class TableManager(models.Manager):
    """Manager for Table model to encapsulate common queries."""

    def filter_by_store(self, store_uuid: str):
        """Returns all tables for a given store."""
        return self.filter(store_uuid=store_uuid)

    def filter_active_tables(self, store_uuid: str = None):
        """Returns active tables, optionally filtered by store."""
        qs = self.filter(is_active=True)
        if store_uuid:
            qs = qs.filter(store_uuid=store_uuid)
        return qs

    def get_table(self, table_uuid: str = None, store_uuid: str = None):
        """Returns a single table by table_uuid or store_uuid (if unique)."""
        if table_uuid:
            return self.get(table_uuid=table_uuid)
        if store_uuid:
            return self.get(store_uuid=store_uuid)
        raise ObjectDoesNotExist("Must provide table_uuid or store_uuid to get a Table.")

class ServiceSessionManager(models.Manager):
    """Manager for ServiceSession model to encapsulate common queries."""

    def filter_active_sessions(
        self,
        session_uuid: str = None,
        store_uuid: str = None,
        table_uuid: str = None
    ):
        """Returns ongoing sessions, optionally filtered by identifiers."""
        qs = self.filter(service_status=ServiceSession.ServiceStatus.SERVICE_SESSION_ONGOING)
        if session_uuid:
            return qs.filter(service_session_uuid=session_uuid)
        if table_uuid:
            qs = qs.filter(table__table_uuid=table_uuid)
        if store_uuid:
            qs = qs.filter(table__store_uuid=store_uuid)
        return qs


    def get_active_session(
        self,
        session_uuid: str|None = None,
        table_uuid: str|None = None,
        store_uuid: str|None = None
    ):
        if session_uuid:
            return self.get(
                service_session_uuid=session_uuid,
                service_status__in=[
                    ServiceSession.ServiceStatus.SERVICE_SESSION_ONGOING,
                    ServiceSession.ServiceStatus.SERVICE_SESSION_PENDING
                ]
            )
        if table_uuid and store_uuid:
            return self.get(
                table__table_uuid=table_uuid,
                table__store_uuid = store_uuid,
                service_status__in=[
                    ServiceSession.ServiceStatus.SERVICE_SESSION_ONGOING,
                    ServiceSession.ServiceStatus.SERVICE_SESSION_PENDING
                ]
            )
        raise ObjectDoesNotExist(
            "Must provide session_uuid, table_uuid or store_uuid to get an active or pending ServiceSession."
        )

    def get_session(self, session_uuid: str):
        """Returns a session by its UUID regardless of status."""
        return self.get(service_session_uuid=session_uuid)

    def filter_sessions_by_table(self, table_uuid: str):
        """Returns all sessions for a given table."""
        return self.filter(table__table_uuid=table_uuid)

    def paginated_list(
        self,
        filters: dict|None = None,
        limit: int = 10,
        page: int = 1
    ) -> tuple[list[Any], int | None, int | None]:
        """
        Returns a paginated list of sessions with optional filters.

        Args:
            filters (dict): A dictionary of filters (e.g., {"store_uuid": "uuid", "service_status": "ONGOING"}).
            limit (int): Number of items per page.
            page (int): Page number.

        Returns:
            tuple: (list of sessions, next_page, prev_page)
        """
        filters = filters or {}
        queryset = self.filter(**filters).order_by('-started_at')
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

class Table(models.Model):
    class PaymentType(models.TextChoices):
        PAYMENT_TYPE_UNSPECIFIED = "PAYMENT_TYPE_UNSPECIFIED"
        PAYMENT_TYPE_POSTPAID = "PAYMENT_TYPE_POSTPAID"  # pay at the end
        PAYMENT_TYPE_PREPAID = "PAYMENT_TYPE_PREPAID"      # pay before order is processed

    table_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store_uuid = models.UUIDField(db_index=True)
    table_number = models.CharField(max_length=10, db_index=True)
    area_name = models.CharField(max_length=50, blank=True, null=True)  # e.g., Indoor, Outdoor, Rooftop
    payment_type = models.CharField(
        max_length=30,
        choices=PaymentType.choices,
        default=PaymentType.PAYMENT_TYPE_POSTPAID,
    )
    no_of_sitting = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TableManager()

    class Meta:
        unique_together = ('store_uuid', 'table_number')
        indexes = [models.Index(fields=['store_uuid', 'table_number'])]


class ServiceSession(models.Model):
    class ServiceStatus(models.TextChoices):
        SERVICE_SESSION_UNSPECIFIED = "SERVICE_SESSION_UNSPECIFIED"
        SERVICE_SESSION_PENDING = "SERVICE_SESSION_PENDING"        # Reserved but not started
        SERVICE_SESSION_ONGOING = "SERVICE_SESSION_ONGOING"        # Actively taking orders
        SERVICE_SESSION_ENDED = "SERVICE_SESSION_ENDED"           # Completed and closed
        SERVICE_SESSION_CANCELLED = "SERVICE_SESSION_CANCELLED"  # Aborted manually

    
    service_session_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name="sessions")
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    service_status = models.CharField(
        max_length=30,
        choices=ServiceStatus.choices,
        default=ServiceStatus.SERVICE_SESSION_ONGOING,
        db_index=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['table'],
                condition=Q(service_status="SERVICE_SESSION_ONGOING"),
                name='unique_ongoing_session_per_table'
            )
        ]
        ordering = ['started_at']  # Order by started_at
        indexes = [
            models.Index(fields=['table']),  # Add index for table
        ]

    def end_session(self):
        self.ended_at = datetime.datetime.now()
        self.service_status = self.ServiceStatus.SERVICE_SESSION_ENDED
        self.save(update_fields=["ended_at", "service_status"])

    @property
    def is_active(self):
        return self.service_status == self.ServiceStatus.SERVICE_SESSION_ONGOING

    objects = ServiceSessionManager()


class Cart(models.Model):
    class order_types(models.TextChoices):
        ORDER_TYPE_UNSPECIFIED = "ORDER_TYPE_UNSPECIFIED",_("ORDER_TYPE_UNSPECIFIED")
        ORDER_TYPE_DINE_IN ="ORDER_TYPE_DINE_IN",_("ORDER_TYPE_DINE_IN")
        ORDER_TYPE_TAKE_AWAY = "ORDER_TYPE_TAKE_AWAY",_("ORDER_TYPE_TAKE_AWAY")
        ORDER_TYPE_DRIVE_THRU = "ORDER_TYPE_DRIVE_THRU",_("ORDER_TYPE_DRIVE_THRU")
    
    class cart_state(models.TextChoices):
        CART_STATE_UNSPECIFIED_STATE = "CART_STATE_UNSPECIFIED_STATE",_("Unspecified_State")
        CART_STATE_ACTIVE = "CART_STATE_ACTIVE",_("Active")
        CART_STATE_LOCKED = "CART_STATE_LOCKED",_("Completed")
        CART_STATE_ABANDONED = "CART_STATE_ABANDONED",_("Abandoned")

    store_uuid = models.UUIDField(db_index=True)
    cart_uuid = models.UUIDField(primary_key= True,default=uuid.uuid4,db_index=True)
    user_phone_no = models.CharField(max_length = 15,null=True,blank= True,verbose_name=_("Phone Number"))
    order_type = models.CharField(max_length=30,choices=order_types.choices,default=order_types.ORDER_TYPE_DINE_IN,verbose_name=_("Order type"))
    # table_no = models.CharField(max_length=4,null=True,blank=True,verbose_name=_("Table No"))
    vehicle_no = models.CharField(max_length=13,null=True,blank=True,verbose_name=_("Vehicle No"))
    vehicle_description = models.CharField(max_length=50,null=True,blank=True,verbose_name=_("Vehicle Description"))
    coupon_code = models.CharField(max_length=20,null=True,blank= True,verbose_name=_("coupone"))
    special_instructions = models.TextField(verbose_name="special instructions",null=True,blank=True)
    state = models.CharField(max_length=30,verbose_name = "State",choices = cart_state.choices,default = cart_state.CART_STATE_ACTIVE)
    # TotalAmount = TextChoices.DecimalField(max_digits=6,decimal_places=2,blank= True,default=Decimal("0.00"),verbose_name= _("Total Amount"))

    table = models.ForeignKey(
        "Table",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="carts"
    )

    service_session = models.ForeignKey(
        "ServiceSession",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="carts"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"
        indexes = [
            models.Index(fields=["store_uuid", "user_phone_no", "cart_uuid"])
        ]


    objects = cart_manager()


    @property
    def is_active(self):
        return self.state == self.cart_state.CART_STATE_ACTIVE

    @property
    def sub_total(self)->Decimal:
        return Decimal(sum(item.sub_total for item in self.items.all()))

    @property
    def total_discount(self) -> Decimal:
        return Decimal(sum(item.discount_amount for item in self.items.all()))

    @property
    def total_price_before_tax(self) -> Decimal:
        return Decimal(sum(item.price_before_tax for item in self.items.all()))

    @property
    def tax_amount(self) -> Decimal:
        return Decimal(sum(item.tax_amount for item in self.items.all()))

    @property
    def packaging_cost(self) -> Decimal:
        if self.order_type == self.order_types.ORDER_TYPE_DINE_IN:
            return Decimal(0.00)
        return Decimal(sum(item.packaging_cost for item in self.items.all()))
    
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

    def lock_cart(self):
        """Locks the cart and prevents further modifications."""
        self.state = self.cart_state.CART_STATE_LOCKED  
        super().save(update_fields=["state"])  # Save only the state field     

    def clean(self):
        # Normalize and validate phone number
        if self.user_phone_no:
            try:
                parsed = phonenumbers.parse(self.user_phone_no, "IN")
                if not phonenumbers.is_valid_number(parsed):
                    raise ValidationError("Invalid phone number.")
                self.user_phone_no = phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.E164
                )
            except phonenumbers.NumberParseException:
                raise ValidationError("Invalid phone number format.")

            # Prevent duplicate active cart
            existing = Cart.objects.filter(
                store_uuid=self.store_uuid,
                user_phone_no=self.user_phone_no,
                state=self.cart_state.CART_STATE_ACTIVE
            ).exclude(pk=self.pk).first()
            if existing:
                raise ValidationError("An active cart already exists for this phone number in this store.")

        # Order type specific validation
        if self.order_type == self.order_types.ORDER_TYPE_DINE_IN:
            if not self.table:
                raise ValidationError("Dine-In orders must have a table.")
            if not self.service_session:
                raise ValidationError("Dine-In orders must be part of a service session.")
            self.vehicle_no = ""
            self.vehicle_description = ""

        elif self.order_type == self.order_types.ORDER_TYPE_DRIVE_THRU:
            if not self.vehicle_no:
                raise ValidationError("Vehicle number is required for Drive-Thru orders.")
            self.table = None
            self.service_session = None

        # Financial sanity checks
        if hasattr(self, 'items') and self.items.exists() and self.sub_total < Decimal("0.00"):
            raise ValidationError("Subtotal cannot be negative.")
        if self.final_amount < Decimal("0.00"):
            raise ValidationError("Final amount cannot be negative.")

    def save(self, *args, **kwargs):
        if self.pk:
            existing_cart = Cart.objects.filter(pk=self.pk).first()
            if existing_cart and existing_cart.state == self.cart_state.CART_STATE_LOCKED:
                raise ValidationError("Cannot modify a locked cart.")
        self.clean()
        super().save(*args, **kwargs)


    def delete(self, *args, **kwargs):
        if self.state == self.cart_state.CART_STATE_LOCKED:
            raise ValidationError("Locked carts cannot be deleted.")
        return super().delete(*args, **kwargs)


class CartItem(models.Model):
    
    cart_item_uuid = models.UUIDField(primary_key= True,default=uuid.uuid4,editable=False, unique=True)
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items"
    )
    product_name = models.TextField(verbose_name="Product Name")
    product_uuid = models.UUIDField(verbose_name=_("Product UUID"), db_index=True)
    tax_percentage = models.DecimalField(
        verbose_name="Tax", max_digits=5, decimal_places=2, default=Decimal("0.00")
    )
    packaging_cost = models.DecimalField(
        verbose_name="Packaging Cost", max_digits=10, decimal_places=2, default=Decimal("0.00")
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

    def clean(self):
        """Validate the cart item data."""
        if self.unit_price < Decimal("0.00"):
            raise ValidationError("Unit price cannot be negative.")
        
        if self.quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        
        if not (Decimal("0.00") <= self.tax_percentage <= Decimal("100.00")):
            raise ValidationError("Tax percentage must be between 0 and 100.")
        
        if not (Decimal("0.00") <= self.discount <= Decimal("100.00")):
            raise ValidationError("Discount percentage must be between 0 and 100.")
        
        if self.packaging_cost < Decimal("0.00"):
            raise ValidationError("Packaging cost cannot be negative.")
        
        if self.cart.state == Cart.cart_state.CART_STATE_LOCKED:
            raise ValidationError("Cannot modify items in a locked cart.")

        return super().clean()

    def save(self, *args, **kwargs):
        """Prevent modifications if the cart is locked."""
        if self.cart.state == Cart.cart_state.CART_STATE_LOCKED:
            raise ValidationError("Cannot modify items in a locked cart.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Prevent deletion of items in a locked cart."""
        if self.cart.state == Cart.cart_state.CART_STATE_LOCKED:
            raise ValidationError("Cannot delete items from a locked cart.")
        
        return super().delete(*args, **kwargs)


    @property
    def add_ons_total(self) -> Decimal:
        """Total price of all add-ons linked to this cart item."""
        return Decimal(sum(addon.sub_total for addon in self.add_ons.all()))

    @property
    def sub_total(self) -> Decimal:
        """Total price before discounts, taxes, and including add-ons."""
        return (self.unit_price + self.add_ons_total ) * self.quantity 


    @property
    def discount_amount(self) -> Decimal:
        """Total discount applied to the item"""
        return (self.sub_total * self.discount) / Decimal("100.00")

    @property
    def price_before_tax(self) -> Decimal:
        """Price before tax but after discount"""
        return (self.sub_total - self.discount_amount + self.packaging_cost) if self.cart.order_type == Cart.order_types.ORDER_TYPE_DRIVE_THRU else (self.sub_total - self.discount_amount)

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

    cart_item = models.ForeignKey(CartItem, verbose_name=_("Cart"), on_delete=models.CASCADE, related_name="add_ons")
    add_on_name = models.TextField(verbose_name="AddOn Name")
    add_on_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, verbose_name="AddOn Id")
    quantity = models.PositiveIntegerField(verbose_name="AddOn Quantity", default=0)
    unit_price = models.DecimalField(decimal_places=2, max_digits=6, verbose_name="AddOn Price", default=0)
    is_free = models.BooleanField(_("Is Free"), default=False)
    max_selectable = models.PositiveIntegerField(default=1, verbose_name="Max Selection")

    class Meta:
        verbose_name = 'Add On'
        verbose_name_plural = 'Add Ons'
        indexes = [
            models.Index(fields=['cart_item']),
            models.Index(fields=['add_on_uuid']),
        ]

    def clean(self):
        """Validate the add-on data."""
        if self.unit_price < Decimal("0.00"):
            raise ValidationError("Unit price cannot be negative.")
        
        if self.quantity < 0:
            raise ValidationError("Quantity cannot be negative.")
        
        if self.is_free:
            if self.unit_price > Decimal("0.00"):
                raise ValidationError("Free add-ons cannot have a price greater than zero.")
            if self.quantity > 0:
                raise ValidationError("Free add-ons cannot have a quantity greater than zero.")
        
        if hasattr(self, 'cart_item') and self.cart_item and self.cart_item.cart.state == Cart.cart_state.CART_STATE_LOCKED:
            raise ValidationError("Cannot modify add-ons in a locked cart.")

        super().clean()

    def save(self, *args, **kwargs):
        
        self.clean()  # Call the clean method to validate the data
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Prevent deletion of addons in a locked cart."""
        if self.cart_item.cart.state == Cart.cart_state.CART_STATE_LOCKED:
            raise ValidationError("Cannot delete addons from a locked cart.")
        return super().delete(*args, **kwargs)

    @property
    def sub_total(self) -> Decimal:
        if self.is_free:
            return Decimal("0.0")
        """Total price of this add-on for the given quantity."""
        return Decimal(self.unit_price * self.quantity)
    
    def add_quantity(self, increment=1):
        if increment < 1:
            raise ValueError("Increment must be positive")
        if self.quantity + increment > self.max_selectable:
            raise ValueError(f"Cannot exceed max selectable quantity of {self.max_selectable}")
        self.quantity += increment
        self.save()
    
    def remove_quantity(self,decrement = 1):
        if decrement < 1:
            raise ValueError("Decrement must be positive")
        if self.quantity - decrement < 0:
            raise ValueError("Quantity cannot be negative")
        self.quantity -= decrement
        self.save()
 
            
class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        DISCOUNT_TYPE_UNSPCIFIED = "DISCOUNT_TYPE_UNSPCIFIED",_("DISCOUNT_TYPE_UNSPCIFIED")
        DISCOUNT_TYPE_PERCENTAGE = "DISCOUNT_TYPE_PERCENTAGE",_("DISCOUNT_TYPE_PERCENTAGE")
        DISCOUNT_TYPE_FIXED = "DISCOUNT_TYPE_FIXED",_("DISCOUNT_TYPE_FIXED")
    
    coupon_uuid = models.UUIDField(primary_key= True,default=uuid.uuid4,verbose_name = _("Coupon Uuid"))
    store_uuid = models.UUIDField()
    coupon_code = models.CharField(max_length= 10)
    discount_type = models.CharField(max_length=30,choices=DiscountType.choices,default=DiscountType.DISCOUNT_TYPE_PERCENTAGE)
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

    def clean(self):
        if self.discount <= Decimal("0.00"):
            raise ValueError("Discount must be greater than zero.")
        if self.min_spend < Decimal("0.00"):
            raise ValueError("Minimum spend cannot be negative.")
        if self.max_cart_value and self.max_cart_value < self.min_spend:
            raise ValueError("Maximum cart value must be greater than or equal to minimum spend.")
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class CouponUsage(models.Model):

    usage_uuid = models.UUIDField(primary_key= True,default=uuid.uuid4,verbose_name="Usage Uuid")
    coupon = models.ForeignKey(Coupon, on_delete=models.DO_NOTHING, related_name="usages")
    user_phone_no = models.CharField(max_length=12, verbose_name=_("User Phone Number"))
    used_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Used At"))
    cart_uuid = models.UUIDField(_("Order id"),null=False,blank=True)
        
    objects = coupon_usage_manager()    
    class Meta:
        unique_together = ["coupon", "user_phone_no", "cart_uuid"]  # Prevent duplicate usage by user for a single order
        indexes = [
                models.Index(fields=["user_phone_no","coupon","cart_uuid"])
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
    def validate(coupon: Coupon, cart: Cart):
        """
        Validates if a coupon is applicable to the given cart.

        Args:
            coupon: The Coupon instance to validate
            cart: The Cart instance to validate against

        Returns:
            tuple: (is_valid, message)
        """
        now = datetime.datetime.now().date()

        # Ensure coupon valid_from and valid_to are date objects
        valid_from = coupon.valid_from
        valid_to = coupon.valid_to
        if isinstance(valid_from, datetime.datetime):
            valid_from = valid_from.date()
        if isinstance(valid_to, datetime.datetime):
            valid_to = valid_to.date()

        cart_value = cart.sub_total

        if not coupon.is_active:
            return (False, "This coupon is not active.")

        if not (valid_from <= now <= valid_to):
            if now < valid_from:
                return (False, "This coupon is not yet valid.")
            else:
                return (False, "This coupon has expired.")

        if coupon.store_uuid != cart.store_uuid:
            return (False, "This coupon is not valid for this store.")

        if coupon.min_spend and cart_value < coupon.min_spend:
            difference = coupon.min_spend - cart_value
            return (False, f"Add ₹{difference:.2f} more to your cart to use this coupon.")

        if coupon.max_cart_value and cart_value > coupon.max_cart_value:
            return (False, "Your cart value exceeds the maximum allowed for this coupon.")

        if coupon.is_for_new_users:
            if Coupon_Validator.has_been_used(coupon, cart):
                return (False, "This coupon has already been used by you.")

        if coupon.usage_limit_per_user:
            flag, msg = Coupon_Validator.has_reached_usage_limit(coupon, cart)
            if flag:
                return (False, msg)

        return (True, "Coupon applied successfully.")