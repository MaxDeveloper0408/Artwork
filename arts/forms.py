from django.forms import ModelForm
from payments.models import ProductPayment
from .models import Order


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['email','product','price','address',]




class ProductPaymentForm(ModelForm):
    class Meta:
        model = ProductPayment
        fields = '__all__'
