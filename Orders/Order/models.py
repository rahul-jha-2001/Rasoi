from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import connection,transaction

from decimal import Decimal
import uuid, base58
import datetime
from typing import Dict, Any
import json



class order_types(models.TextChoices):
    ORDER_TYPE_UNSPECIFIED = "ORDER_TYPE_UNSPECIFIED", _("Unspecified")
    ORDER_TYPE_DINE_IN = "ORDER_TYPE_DINE_IN", _("DineIn")
    ORDER_TYPE_TAKE_AWAY = "ORDER_TYPE_TAKE_AWAY", _("TakeAway")
    ORDER_TYPE_DRIVE_THRU = "ORDER_TYPE_DRIVE_THRU", _("DriveThru")

class order_state(models.TextChoices):
    ORDER_STATE_UNSPECIFIED = "ORDER_STATE_UNSPECIFIED", _("Unspecified_State")
    ORDER_STATE_PAYMENT_PENDING = "ORDER_STATE_PAYMENT_PENDING", _("Payment Pending")
    ORDER_STATE_PLACED = "ORDER_STATE_PLACED", _("Placed")
    ORDER_STATE_PREPARING = "ORDER_STATE_PREPARING", _("Preparing")
    ORDER_STATE_READY = "ORDER_STATE_READY", _("Ready")
    ORDER_STATE_COMPLETED = "ORDER_STATE_COMPLETED", _("Completed")
    ORDER_STATE_CANCELED = "ORDER_STATE_CANCELED", _("Canceled")

class payment_state(models.TextChoices):
    PAYMENT_STATE_UNSPECIFIED = "PAYMENT_STATE_UNSPECIFIED", _("Unspecified")
    PAYMENT_STATE_PENDING = "PAYMENT_STATE_PENDING", _("Pending")
    PAYMENT_STATE_COMPLETE = "PAYMENT_STATE_COMPLETE", _("Complete")
    PAYMENT_STATE_FAILED = "PAYMENT_STATE_FAILED", _("Failed")
    PAYMENT_STATE_REFUNDED = "PAYMENT_STATE_REFUNDED", _("Refunded")

class payment_method(models.TextChoices):
    PAYMENT_METHOD_UNSPECIFIED = "PAYMENT_METHOD_UNSPECIFIED", _("Unspecified")
    PAYMENT_METHOD_RAZORPAY = "PAYMENT_METHOD_RAZORPAY", _("Razorpay")
    PAYMENT_METHOD_CASH = "PAYMENT_METHOD_CASH", _("Cash")
    PAYMENT_METHOD_CARD = "PAYMENT_METHOD_CARD", _("Card")
    PAYMENT_METHOD_UPI = "PAYMENT_METHOD_UPI", _("UPI")
    PAYMENT_METHOD_NETBANKING = "PAYMENT_METHOD_NETBANKING", _("Netbanking")




class order_manager(models.Manager):
    def get_store_orders(self, store_uuid: str,limit: int = 10, page: int = 1) -> tuple:
        """
        Get paginated orders for a specific store
        """
        queryset = self.get_queryset().filter(store_uuid=store_uuid).order_by('-created_at')
        paginator = Paginator(queryset, limit)
        try:
            paginated_data = paginator.page(page)
        except PageNotAnInteger:
            paginated_data = paginator.page(1)
        except EmptyPage:
            paginated_data = paginator.page(paginator.num_pages())

        next_page = paginated_data.next_page_number() if paginated_data.has_next() else None
        prev_page = paginated_data.previous_page_number() if paginated_data.has_previous() else None

        return paginated_data.object_list, next_page, prev_page

    def get_user_orders(self, store_uuid: str,user_phone_no:str,limit: int = 10, page: int = 1) -> tuple:
        """
        Get paginated orders for a specific store
        """
        queryset = self.get_queryset().filter(store_uuid=store_uuid,user_phone_no = user_phone_no).order_by('-created_at')
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


def generate_order_no() -> str:
    """Generate a base58-encoded shortened UUID"""
    return base58.b58encode(uuid.uuid4().bytes).decode()[:10]


class Order(models.Model):

    store_uuid = models.UUIDField(db_index=True)
    order_no = models.CharField(
        max_length=16,
        unique=True,
        default=generate_order_no,  # Use the named function
        editable=False
    )
    cart_uuid = models.UUIDField(null=True, blank=True, verbose_name=_("Cart UUID"),unique=True)
    order_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, db_index=True)
    user_phone_no = models.CharField(max_length=12, null=False, blank=False, verbose_name=_("Phone Number"))
    order_type = models.CharField(max_length=30, choices=order_types.choices, default=order_types.ORDER_TYPE_DINE_IN, verbose_name=_("Order Type"))
    table_no = models.CharField(max_length=4, null=True, blank=True, verbose_name=_("Table No"))
    vehicle_no = models.CharField(max_length=10, null=True, blank=True, verbose_name=_("Vehicle No"))
    vehicle_description = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Vehicle Description"))
    

    coupon_code = models.CharField(max_length=20, null=True, blank=True, verbose_name=_("Coupon Code"))
    special_instructions = models.TextField(verbose_name=_("Special Instructions"), null=True, blank=True)
    
    # Order state and payment tracking
    order_status = models.CharField(max_length=30, choices=order_state.choices, default=order_state.ORDER_STATE_PAYMENT_PENDING, verbose_name=_("Order Status"))
    # payment_status = models.CharField(max_length=20, choices=payment_state.choices, default=payment_state.PAYMENT_STATE_PENDING, verbose_name=_("Payment Status"))
    # payment_method = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Payment Method"))
    
    # Financial tracking
    subtotal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Subtotal Amount"))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Discount Amount"))
    price_before_tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Price Before Tax"))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Tax Amount"))
    packaging_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Packaging Cost"))
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Final Amount"))
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = order_manager()

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        indexes = [
            models.Index(fields=["store_uuid", "user_phone_no", "order_uuid"]),
            models.Index(fields=["order_status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.user_phone_no} - {self.order_uuid}"
    
    @property
    def total_items(self) -> int:
        return self.items.count()
    
    def clean(self):
        # Apply the same validation rules as in the cart
        if self.order_type == order_types.ORDER_TYPE_DINE_IN and not self.table_no:
            raise ValueError("Table number is required for DineIn orders.")
        if self.order_type == order_types.ORDER_TYPE_DRIVE_THRU and not self.vehicle_no:
            raise ValueError("Vehicle number is required for DriveThru orders.")
        if self.subtotal_amount < Decimal("0.00"):
            raise ValueError("Subtotal amount cannot be negative.")

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        with connection.cursor() as cursor:
            channel_name = f'order_updates_{self.store_uuid}'.replace("-","_")
            payload = json.dumps({'order_uuid': str(self.order_uuid), 'action': 'created' if is_new else 'updated'})
            cursor.execute(f"NOTIFY {channel_name}, %s", [payload])

        print("Notification sent")
  

class OrderItem(models.Model):
    item_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_name = models.TextField(verbose_name=_("Product Name"))
    product_uuid = models.UUIDField(verbose_name=_("Product UUID"), db_index=True)
    
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Unit Price"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Quantity"))
    discount = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100.00"))],
        verbose_name=_("Discount Percentage")
    )
    tax_percentage = models.DecimalField(
        verbose_name=_("Tax"), max_digits=5, decimal_places=2, default=Decimal("0.00")
    )
    packaging_cost = models.DecimalField(
        verbose_name=_("Packaging Cost"), max_digits=10, decimal_places=2, default=Decimal("0.00")
    )
    
    # Pre-calculated amounts to avoid recalculation
    subtotal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Subtotal Amount"))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Discount Amount"))
    price_before_tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Price Before Tax"))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Tax Amount"))
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Final Price"))
    add_ons_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"), verbose_name=_("Add On Total"))
    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["product_uuid"]),
        ]

    def __str__(self):
        return f"{self.product_name} ({self.quantity})"


class OrderItemAddOn(models.Model):
    order_item_addOn_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, verbose_name=_("Order Item AddOn ID"))
    add_on_uuid = models.UUIDField(null= True,blank=True, verbose_name=_("AddOn ID"))
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="add_ons")
    add_on_name = models.TextField(verbose_name=_("AddOn Name"))
    quantity = models.PositiveIntegerField(verbose_name=_("AddOn Quantity"), default=0)
    unit_price = models.DecimalField(decimal_places=2, max_digits=6, verbose_name=_("AddOn Price"), default=0)
    is_free = models.BooleanField(_("Is Free"), default=False)
    subtotal_amount = models.DecimalField(decimal_places=2, max_digits=10, verbose_name=_("Subtotal"), default=Decimal("0.00"))

    class Meta:
        verbose_name = _('Order Item Add On')
        verbose_name_plural = _('Order Item Add Ons')
        indexes = [
            models.Index(fields=['order_item']),
            models.Index(fields=['order_item_addOn_uuid']),
        ]

    def __str__(self):
        return f"{self.add_on_name} ({self.quantity})"


# class OrderHistory(models.Model):
#     """
#     Tracks order status changes for auditing purposes
#     """
#     history_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="history")
#     previous_status = models.CharField(max_length=20, choices=Order.order_state.choices)
#     new_status = models.CharField(max_length=20, choices=Order.order_state.choices)
#     changed_at = models.DateTimeField(auto_now_add=True)
#     changed_by = models.CharField(max_length=100, null=True, blank=True)
#     notes = models.TextField(null=True, blank=True)

#     class Meta:
#         verbose_name = _("Order History")
#         verbose_name_plural = _("Order Histories")
#         indexes = [
#             models.Index(fields=["order"]),
#             models.Index(fields=["changed_at"]),
#         ]

#     def __str__(self):
#         return f"{self.order.order_uuid} - {self.previous_status} to {self.new_status}"


class OrderPayment(models.Model):
    """
    Tracks payment attempts and details for orders
    """
    payment_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)


    rz_payment_id = models.CharField(max_length=50, null=True, blank=True)
    rz_order_id = models.CharField(max_length=50, null=True, blank=True)
    rz_signature = models.CharField(max_length=100, null=True, blank=True)


    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(verbose_name=_("Payment Method"),max_length=30,choices=payment_method.choices,default=payment_method.PAYMENT_METHOD_CASH)
    status = models.CharField(verbose_name=_("Payment Status"),max_length=30, choices=payment_state.choices,default=payment_state.PAYMENT_STATE_PENDING)
    time = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name = _("Order Payment")
        verbose_name_plural = _("Order Payments")
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["status"]),
            models.Index(fields=["time"]),
        ]

    def __str__(self):
        return f"{self.order.order_uuid} - {self.amount} - {self.status}"
    
    @transaction.atomic
    def update_status(self,new_payment_state):
        if new_payment_state not in [choice[0] for choice in payment_state.choices]:
            raise ValueError(f"Invalid payment state: {new_payment_state}")
    
        # Update payment status
        old_status = self.status
        self.status = new_payment_state
        self.save()
        
        # Always update the order to trigger notification
        # Even if no visible fields change, updating updated_at and triggering save() notification
        order = self.order
        
        # Update corresponding order status if payment state requires it
        if new_payment_state == payment_state.PAYMENT_STATE_COMPLETE and order.order_status == order_state.ORDER_STATE_PAYMENT_PENDING:
            order.order_status = order_state.ORDER_STATE_PLACED
        elif new_payment_state == payment_state.PAYMENT_STATE_REFUNDED:
            order.order_status = order_state.ORDER_STATE_CANCELED