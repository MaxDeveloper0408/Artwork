from accounts.models import Profile
from .models import *
from arts.serializers import ProductSerializer
from rest_framework.serializers import ModelSerializer, SerializerMethodField


class OrderSerializer(ModelSerializer):
    product_name = SerializerMethodField('get_product_name')
    product_image = SerializerMethodField('get_product_image')
    collector_name = SerializerMethodField('get_collector_name')
    collector_image = SerializerMethodField('get_collector_image')

    class Meta:
        model = Order
        fields = ['id', 'currency', 'price', 'fees', 'net', 'status', 'time',
                  'product_name', 'product_image', 'collector_name', 'collector_image']

    def get_product_name(self, obj):
        return obj.product.name

    def get_product_image(self, obj):
        return obj.product.image.url

    def get_collector_name(self, obj):
        name = obj.collector.first_name + obj.collector.last_name
        if not name:
            name = obj.collector.username
        return name

    def get_collector_image(self, obj):
        return Profile.objects.get(user=obj.collector).image.url


class PaymentMethodSerializer(ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'method', 'method_data']
