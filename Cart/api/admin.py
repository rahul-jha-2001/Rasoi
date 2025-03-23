from django.contrib import admin
from api.models import Cart,CartItem,Coupon,CouponUsage,AddOn
# Register your models here.ad
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Coupon)
admin.site.register(CouponUsage)
admin.site.register(AddOn)

