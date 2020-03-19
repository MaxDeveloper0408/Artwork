from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import *
from payments.models import Order


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TagSerializer(ModelSerializer):
    sold = SerializerMethodField('get_sold')
    earned = SerializerMethodField('get_earned')

    class Meta:
        model = Tag
        fields = ['name', 'sold', 'earned']  # sold & earned returns Available in Tags API if not called by Tags API

    def get_sold(self, obj):
        return getattr(obj, 'sold', 'Available in Tags API')

    def get_earned(self, obj):
        return getattr(obj, 'earned', 'Available in Tags API')


class ProductSerializer(ModelSerializer):

    # adding authenticated user to user field
    def to_internal_value(self, data):
        mutable_dict = data.copy()
        mutable_dict['user'] = self.context['request'].user.id
        return super(ProductSerializer, self).to_internal_value(mutable_dict)

    class Meta:
        model = Product
        fields = '__all__'
