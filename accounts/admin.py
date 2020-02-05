from django.contrib import admin
from .models import *
# Register your models here.

class ProfileDashboard(admin.ModelAdmin):
    list_display = ('user','role','platform_fees')
    list_editable = ('platform_fees',)

admin.site.register(Profile,ProfileDashboard)
admin.site.register(Address)

