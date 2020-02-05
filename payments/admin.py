from django.contrib import admin
from .models import *

class ProductPaymentDashboard(admin.ModelAdmin):
    list_display = ['order','status','payment_id','uid']
    list_filter = ['status']
    list_editable = ['status']

admin.site.register(ProductPayment,ProductPaymentDashboard)
admin.site.register(PaymentMethod)
