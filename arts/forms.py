from django.forms import ModelForm
from payments.models import ProductPayment
from .models import Order


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = '__all__'


class ProductPaymentForm(ModelForm):
    class Meta:
        model = ProductPayment
        fields = '__all__'


class ProductForm(ModelForm):
    class Meta:
        fields = '__all__'
