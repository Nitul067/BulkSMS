from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from .models import Recharge


class RechargeForm(forms.ModelForm):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )
    
    amount = forms.FloatField(widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Amount"}))
    sms_count = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "No. of SMS"}))
    status = forms.CharField(widget=forms.Select(choices=STATUS_CHOICES, attrs={"class": "form-control"}))
    recharge_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
    
    class Meta:
        model = Recharge
        fields = [
            "amount",
            "sms_count",
            "status",
            "recharge_date",
        ]

