from django.contrib import admin
from User import models
from User.models import Store,CustomerLogin
# Register your models here.

class StoreAdmin(admin.ModelAdmin):
    list_display = ('display_uuid', 'StoreName', 'email', 'PhoneNo')
    readonly_fields = ('StoreUuid',)
    
    def display_uuid(self, obj):
        return str(obj.StoreUuid)
    display_uuid.short_description = 'Store UUID'

class CustomerLoginAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'store_name', 'formatted_login_time')
    
    def customer_name(self, obj):
        return obj.customer.Name
    customer_name.short_description = 'Customer'
    
    def store_name(self, obj):
        return obj.store.StoreName
    store_name.short_description = 'Store'
    
    def formatted_login_time(self, obj):
        return obj.login_time.strftime('%Y-%m-%d %H:%M:%S')
    formatted_login_time.short_description = 'Login Time'
    

admin.site.register(CustomerLogin, CustomerLoginAdmin)

admin.site.register(Store, StoreAdmin)
admin.site.register(models.Customer)

