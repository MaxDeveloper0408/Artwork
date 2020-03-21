from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.forms import ModelForm
from .models import Address, CreditCard, Profile


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with that email already exists.", code="unique")
        return email

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save()
        return user


class AddressForm(ModelForm):
    class Meta:
        model = Address
        fields = ['city', 'state', 'country', 'address_line1', 'address_line2']


class CreditCardForm(ModelForm):
    class Meta:
        model = CreditCard
        fields = ['number', 'exp_month', 'exp_year', 'cvv']


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['user']
