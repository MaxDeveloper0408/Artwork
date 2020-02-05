from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from .models import UserMenu,Quote


class UserMenuSerializer(ModelSerializer):

    menu = serializers.SerializerMethodField()
    menu_icon = serializers.SerializerMethodField()
    submenu = serializers.SerializerMethodField()
    submenu_icon = serializers.SerializerMethodField()

    class Meta:
        model = UserMenu
        fields = ['menu','menu_url','menu_icon','submenu','submenu_url','submenu_icon']

    def get_menu(self,obj):
        return obj.menu.name

    def get_menu_icon(self,obj):
        return obj.menu.icon

    def get_submenu(self,obj):
        try:
            return obj.submenu.name
        except:
            return None

    def get_submenu_icon(self,obj):
        try:
            return obj.submenu.icon
        except:
            return None

class QuoteSerializer(ModelSerializer):
    class Meta:
        model = Quote
        fields = ['quote']
