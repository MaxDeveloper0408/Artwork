from django.contrib import admin
from .models import *
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string

class StripeSettingDashboard(admin.ModelAdmin):

    list_display = ('name','data','data_type','value')
    list_editable = ('data','data_type',)


class MenuDashboard(admin.ModelAdmin):
    list_display = ('view','menu','menu_url','submenu','submenu_url')
    list_editable = ('menu','menu_url','submenu','submenu_url')
    ordering = ('menu',)
    list_filter = ('role',)
    change_list_template = 'admin/usermenu.html'

    def view(self,obj):
        return f'{obj.id}'

class QuoteDashboard(admin.ModelAdmin):
    list_display = ['quote','created_at','default']
    list_editable = ['default']

admin.site.register(StripeSetting,StripeSettingDashboard)
admin.site.register(UserMenu,MenuDashboard)
admin.site.register(Menu)
admin.site.register(Quote,QuoteDashboard)

