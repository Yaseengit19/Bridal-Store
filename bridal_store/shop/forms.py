from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    address = forms.CharField(max_length=250)
    phone = forms.CharField(max_length=20)
    
    class Meta:
        model = Order
        fields = []  # We're handling the Order fields manually