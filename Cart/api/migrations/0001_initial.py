# Generated by Django 5.1.1 on 2025-03-22 14:41

import django.core.validators
import django.db.models.deletion
import uuid
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('coupon_uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, verbose_name='Coupon Uuid')),
                ('store_uuid', models.UUIDField()),
                ('coupon_code', models.CharField(max_length=10)),
                ('discount_type', models.CharField(choices=[('PERCENTAGE', 'Percentage'), ('FIXED', 'FIXED')], default='PERCENTAGE', max_length=15)),
                ('valid_from', models.DateField()),
                ('valid_to', models.DateField()),
                ('usage_limit_per_user', models.PositiveIntegerField(default=1, verbose_name='Usage Limit Per User')),
                ('total_usage_limit', models.PositiveIntegerField(blank=True, null=True, verbose_name='Total Usage Limit')),
                ('discount', models.DecimalField(decimal_places=2, max_digits=6, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('100'))])),
                ('min_spend', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('max_discount', models.DecimalField(decimal_places=2, default=Decimal('0.0'), max_digits=6, verbose_name='Max Discount')),
                ('is_for_new_users', models.BooleanField(default=False, verbose_name='Is for New Users')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Coupon Description')),
                ('max_cart_value', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Max Cart Value')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('store_uuid', models.UUIDField(db_index=True)),
                ('cart_uuid', models.UUIDField(db_index=True, default=uuid.uuid4, primary_key=True, serialize=False)),
                ('user_phone_no', models.CharField(max_length=12, verbose_name='Phone Number')),
                ('order_type', models.CharField(choices=[('UNSPECIFIED', 'Unspecified'), ('DINEIN', 'DineIn'), ('TAKEAWAY', 'TakeAway'), ('DRIVETHRU', 'DriveThru')], default='DINEIN', max_length=15, verbose_name='Order type')),
                ('table_no', models.CharField(blank=True, max_length=4, null=True, verbose_name='Table No')),
                ('vehicle_no', models.CharField(blank=True, max_length=10, null=True, verbose_name='Vehicle No')),
                ('vehicle_description', models.CharField(blank=True, max_length=50, null=True, verbose_name='Vehicle Description')),
                ('coupon_code', models.CharField(blank=True, max_length=20, null=True, verbose_name='coupone')),
                ('speacial_instructions', models.TextField(blank=True, null=True, verbose_name='speacial instructions')),
                ('state', models.CharField(choices=[('UNSPECIFIED_STATE', 'Unspecified_State'), ('ACTIVE', 'Active'), ('COMPLETED', 'Completed'), ('ABANDONED', 'Abandoned')], default='ACTIVE', max_length=20, verbose_name='State')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Cart',
                'verbose_name_plural': 'Carts',
                'indexes': [models.Index(fields=['store_uuid', 'user_phone_no', 'cart_uuid'], name='api_cart_store_u_d9705b_idx')],
            },
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('cart_item_uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('product_name', models.TextField(verbose_name='Product Name')),
                ('product_uuid', models.UUIDField(db_index=True, verbose_name='Product UUID')),
                ('tax_percentage', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, verbose_name='Tax')),
                ('packaging_cost', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10, verbose_name='Packaging Cost')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('discount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('100.00'))], verbose_name='Discount Percentage')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='api.cart')),
            ],
            options={
                'verbose_name': 'Cart Item',
                'verbose_name_plural': 'Cart Items',
            },
        ),
        migrations.CreateModel(
            name='AddOn',
            fields=[
                ('add_on_name', models.TextField(verbose_name='AddOn Name')),
                ('add_on_uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, verbose_name='AddOn Id')),
                ('quantity', models.PositiveIntegerField(default=0, verbose_name='AddOn Quantity')),
                ('unit_price', models.DecimalField(decimal_places=2, default=0, max_digits=6, verbose_name='AddOn Price')),
                ('is_free', models.BooleanField(default=False, verbose_name='Is Free')),
                ('cart_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='add_ons', to='api.cartitem', verbose_name='Cart')),
            ],
            options={
                'verbose_name': 'Add On',
                'verbose_name_plural': 'Add Ons',
            },
        ),
        migrations.CreateModel(
            name='CouponUsage',
            fields=[
                ('usage_uuid', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, verbose_name='Usage Uuid')),
                ('user_phone_no', models.CharField(max_length=12, verbose_name='User Phone Number')),
                ('used_at', models.DateTimeField(auto_now_add=True, verbose_name='Used At')),
                ('order_uuid', models.UUIDField(blank=True, verbose_name='Order id')),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='usages', to='api.coupon')),
            ],
        ),
        migrations.AddIndex(
            model_name='cartitem',
            index=models.Index(fields=['cart'], name='api_cartite_cart_id_516016_idx'),
        ),
        migrations.AddIndex(
            model_name='cartitem',
            index=models.Index(fields=['product_uuid', 'cart_item_uuid'], name='api_cartite_product_8550e2_idx'),
        ),
        migrations.AddIndex(
            model_name='addon',
            index=models.Index(fields=['cart_item'], name='api_addon_cart_it_8c6aff_idx'),
        ),
        migrations.AddIndex(
            model_name='addon',
            index=models.Index(fields=['add_on_uuid'], name='api_addon_add_on__c47b86_idx'),
        ),
        migrations.AddIndex(
            model_name='couponusage',
            index=models.Index(fields=['user_phone_no', 'coupon', 'order_uuid'], name='api_couponu_user_ph_80eb7b_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='couponusage',
            unique_together={('coupon', 'user_phone_no', 'order_uuid')},
        ),
    ]
