from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from decimal import Decimal
import uuid, base58
import datetime
from typing import Dict, Any


class order_manager(models.Manager):
    def get_orders(self, store_uuid: str, limit: int = 10, page: int = 1) -> tuple:
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
            paginated_data = paginator.page(paginator.num_pages)

        next_page = paginated_data.next_page_number() if paginated_data.has_next() else None
        prev_page = paginated_data.previous_page_number() if paginated_data.has_previous() else None

        return paginated_data.object_list, next_page, prev_page


class Order(models.Model):
    class order_types(models.TextChoices):
        UNSPECIFIED = "UNSPECIFIED", _("Unspecified")
        DINEIN = "DINEIN", _("DineIn")
        TAKEAWAY = "TAKEAWAY", _("TakeAway")
        DRIVETHRU = "DRIVETHRU", _("DriveThru")
    
    class order_state(models.TextChoices):
        UNSPECIFIED_STATE = "UNSPECIFIED_STATE", _("Unspecified_State")
        PAYMENT_PENDING = "PAYMENT_PENDING", _("Payment Pending")
        PLACED = "PLACED", _("Placed")
        PREPARING = "PREPARING", _("Preparing")
        READY = "READY", _("Ready")
        COMPLETED = "COMPLETED", _("Completed")
        CANCELED = "CANCELED", _("Canceled")
    
    class payment_state(models.TextChoices):
        UNSPECIFIED = "UNSPECIFIED", _("Unspecified")
        PENDING = "PENDING", _("Pending")
        COMPLETE = "COMPLETE", _("Complete")
        FAILED = "FAILED", _("Failed")
        REFUNDED = "REFUNDED", _("Refunded")

    store_uuid = models.UUIDField(db_index=True)
    order_no = models.CharField(
        max_length=16,
        unique=True,
        default=lambda: base58.b58encode(uuid.uuid4().bytes).decode()[:10],
        editable=False
    )
    cart_uuid = models.UUIDField(null=True, blank=True, verbose_name=_("Cart UUID"))
    order_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, db_index=True)
    user_phone_no = models.CharField(max_length=12, null=False, blank=False, verbose_name=_("Phone Number"))
    order_type = models.CharField(max_length=15, choices=order_types.choices, default=order_types.DINEIN, verbose_name=_("Order Type"))
    table_no = models.CharField(max_length=4, null=True, blank=True, verbose_name=_("Table No"))
    vehicle_no = models.CharField(max_length=10, null=True, blank=True, verbose_name=_("Vehicle No"))
    vehicle_description = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Vehicle Description"))
    

    coupon_code = models.CharField(max_length=20, null=True, blank=True, verbose_name=_("Coupon Code"))
    special_instructions = models.TextField(verbose_name=_("Special Instructions"), null=True, blank=True)
    
    # Order state and payment tracking
    order_status = models.CharField(max_length=20, choices=order_state.choices, default=order_state.PAYMENT_PENDING, verbose_name=_("Order Status"))
    payment_status = models.CharField(max_length=20, choices=payment_state.choices, default=payment_state.PENDING, verbose_name=_("Payment Status"))
    payment_method = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Payment Method"))
    
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
    
    @classmethod
    def create_from_cart(cls, cart):
        """
        Create an order from a cart instance
        """
        order = cls(
            store_uuid=cart.store_uuid,
            user_phone_no=cart.user_phone_no,
            order_type=cart.order_type,
            table_no=cart.table_no,
            vehicle_no=cart.vehicle_no,
            vehicle_description=cart.vehicle_description,
            coupon_code=cart.coupon_code,
            special_instructions=cart.speacial_instructions,
            subtotal_amount=cart.total_subtotal,
            discount_amount=cart.total_discount,
            price_before_tax=cart.total_price_before_tax,
            tax_amount=cart.tax_amount,
            packaging_cost=cart.packaging_cost,
            final_amount=cart.final_amount,
            cart_uuid=cart.cart_uuid
        )
        order.save()
        
        # Create order items from cart items
        for cart_item in cart.items.all():
            order_item = OrderItem(
                order=order,
                product_uuid=cart_item.product_uuid,
                product_name=cart_item.product_name,
                unit_price=cart_item.unit_price,
                quantity=cart_item.quantity,
                discount=cart_item.discount,
                tax_percentage=cart_item.tax_percentage,
                packaging_cost=cart_item.packaging_cost,
                subtotal_amount=cart_item.subtotal_amount,
                discount_amount=cart_item.discount_amount,
                price_before_tax=cart_item.price_before_tax,
                tax_amount=cart_item.tax_amount,
                final_price=cart_item.final_price
            )
            order_item.save()
            
            # Create add-ons for order items
            for cart_addon in cart_item.add_ons.all():
                order_addon = OrderItemAddOn(
                    order_item=order_item,
                    add_on_name=cart_addon.add_on_name,
                    add_on_uuid=cart_addon.add_on_uuid,
                    quantity=cart_addon.quantity,
                    unit_price=cart_addon.unit_price,
                    is_free=cart_addon.is_free,
                    subtotal=cart_addon.subtotal
                )
                order_addon.save()
        
        # If there was a coupon used, record the usage

        
        return order
    
    def clean(self):
        # Apply the same validation rules as in the cart
        if self.order_type == self.order_types.DINEIN and not self.table_no:
            raise ValueError("Table number is required for DineIn orders.")
        if self.order_type == self.order_types.DRIVETHRU and not self.vehicle_no:
            raise ValueError("Vehicle number is required for DriveThru orders.")
        if self.subtotal_amount < Decimal("0.00"):
            raise ValueError("Subtotal amount cannot be negative.")


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
    add_on_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, verbose_name=_("AddOn ID"))
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
            models.Index(fields=['add_on_uuid']),
        ]

    def __str__(self):
        return f"{self.add_on_name} ({self.quantity})"


class OrderHistory(models.Model):
    """
    Tracks order status changes for auditing purposes
    """
    history_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="history")
    previous_status = models.CharField(max_length=20, choices=Order.order_state.choices)
    new_status = models.CharField(max_length=20, choices=Order.order_state.choices)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _("Order History")
        verbose_name_plural = _("Order Histories")
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["changed_at"]),
        ]

    def __str__(self):
        return f"{self.order.order_uuid} - {self.previous_status} to {self.new_status}"


class OrderPayment(models.Model):
    """
    Tracks payment attempts and details for orders
    """
    payment_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4)


    rz_payment_id = models.CharField(max_length=50, null=True, blank=True)
    rz_order_id = models.CharField(max_length=50, null=True, blank=True)
    rz_signature = models.CharField(max_length=100, null=True, blank=True)


    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=Order.payment_state.choices)
    payment_time = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name = _("Order Payment")
        verbose_name_plural = _("Order Payments")
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["status"]),
            models.Index(fields=["payment_time"]),
        ]

    def __str__(self):
        return f"{self.order.order_uuid} - {self.amount} - {self.status}"