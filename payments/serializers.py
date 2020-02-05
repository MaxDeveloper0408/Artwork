from .models import *
from arts.serializers import ProductSerializer
from rest_framework.serializers import ModelSerializer,SerializerMethodField

class OrderSerializer(ModelSerializer):

    product = ProductSerializer()

    class Meta:
        model = Order
        fields = ['id','price','status','slug','by','product']

