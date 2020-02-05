from rest_framework.serializers import ModelSerializer,SerializerMethodField
from settings.models import StripeSetting
from .models import *

class UserSerializer(ModelSerializer):
    class Meta:
         model  = User
         fields = ['username','email','first_name','last_name']

class AddressSerializer(ModelSerializer):

    class Meta:
         model  = Address
         fields = ['phone','street','city','zip_code','state','country']

class CountrySerializer(ModelSerializer):
    class Meta:
         model  = Address
         fields = ['country']

class ProfileSerializer(ModelSerializer):

    username = SerializerMethodField('get_username')
    email = SerializerMethodField('get_email')
    first_name = SerializerMethodField('get_first_name')
    last_name = SerializerMethodField('get_last_name')
    platform_fees = SerializerMethodField('get_platform_fees')
    primary_address = AddressSerializer(read_only=True)

    class Meta:
         model  = Profile
         fields = ['username','email','first_name','last_name','role','primary_address','platform_fees','image']
         read_only_fields = ('image','platform_fees')

    def get_platform_fees(self,obj):
        if obj.platform_fees:
            return obj.platform_fees
        else:
            fees = StripeSetting.objects.get(name='PF')
            return fees.value()


    def get_first_name(self,obj):
        return obj.user.first_name

    def get_last_name(self,obj):
        return obj.user.last_name

    def get_username(self,obj):
        return obj.user.username

    def get_email(self,obj):
        return obj.user.email


class ProfileSerializerReadOnly(ModelSerializer):

    username = SerializerMethodField('get_username')
    first_name = SerializerMethodField('get_first_name')
    last_name = SerializerMethodField('get_last_name')

    class Meta:
         model  = Profile
         fields = ['username','first_name','last_name','image']
         read_only_fields = ['username','first_name','last_name','image']


    def get_first_name(self,obj):
        return obj.user.first_name

    def get_last_name(self,obj):
        return obj.user.last_name

    def get_username(self,obj):
        return obj.user.username

    def get_email(self,obj):
        return obj.user.email


class ProfileImageSerializer(ModelSerializer):
    class Meta:
         model  = Profile
         fields = ['image']



