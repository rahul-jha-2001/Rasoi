from django.contrib import admin
from api.models import Cart,CartItem,Coupon,CouponUsage
# Register your models here.ad
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Coupon)
admin.site.register(CouponUsage)


