from django.contrib import admin
from .models import *
# Register your models here.


class OrderDashboard(admin.ModelAdmin):
    list_display = ['email','product','_price','slug','status','created_at']
    list_filter = ['created_at']
    ordering = ['-created_at']
    def _price(self,obj):
        return '$ '+str(obj.price)


class ProductDashboard(admin.ModelAdmin):
    list_display = ['name','_price', 'description', 'slug']

    def _price(self, obj):
        return '$ ' + str(obj.price)


admin.site.register(Product,ProductDashboard)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Order,OrderDashboard)
