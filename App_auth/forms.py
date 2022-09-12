from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import *


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


class ProductModelForm(forms.ModelForm):
    class Meta:
        model = ProductModel
        fields = "__all__"


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user',]



class BillingForm(forms.ModelForm):
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'User country code like (+880)'}))
    country = forms.CharField(widget=forms.TextInput(attrs={'class': "selectpicker countrypicker"}))

    class Meta:
        model = BillingAddress
        fields = ['phone_number', 'shop_address', 'zip_code', 'city_zone', 'country']

