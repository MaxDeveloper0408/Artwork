from .models import ProductPayment
from django.forms import ModelForm


class ProductPaymentForm(ModelForm):
    class Meta:
        model = ProductPayment
        fields = '__all__'
