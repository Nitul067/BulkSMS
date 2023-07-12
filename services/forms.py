from django import forms
from .models import Recharge, Transaction, Tariff


tariff = Tariff.objects.all()
amount_list = [("", "Select Amount")]
for row in tariff:
    if (row.value, row.value) not in amount_list:
        amount_list.append((row.value, row.value))


class RechargeForm(forms.ModelForm):
    AMOUNT_CHOICES = tuple(amount_list)
    SMS_COUNT_CHOICES = (
        ("", "Select SMS_Count"),
    )
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )
    
    amount = forms.FloatField(widget=forms.Select(choices=AMOUNT_CHOICES, attrs={"id": "amount", "class": "form-select"}))
    sms_count = forms.IntegerField(widget=forms.Select(choices=SMS_COUNT_CHOICES, attrs={"id": "sms_count", "class": "form-select"}))
    status = forms.CharField(widget=forms.Select(choices=STATUS_CHOICES, attrs={"class": "form-select"}), initial="Completed")
    recharge_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
    
    class Meta:
        model = Recharge
        fields = [
            "amount",
            "sms_count",
            "status",
            "recharge_date",
        ]


class TransactionForm(forms.ModelForm):
    NATURE_CHOICES = (
        ('Promo', 'Promo'),
        ('Trans', 'Trans'),
    )
    HEADER_CHOICES = (
        ('Government', 'Government'),
        ('PSU', 'PSU'),
        ('Regular', 'Regular'),
        ('TRAI Exempted', 'TRAI Exempted'),
    )
    
    trans_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
    nature = forms.CharField(widget=forms.Select(choices=NATURE_CHOICES, attrs={"class": "form-select"}), initial="Trans")
    header = forms.CharField(widget=forms.Select(choices=HEADER_CHOICES, attrs={"class": "form-select"}), initial="Regular")
    to_scrubber = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "to_scrubber"}))
    scrubb_success = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "scrubb_success"}))
    to_telco = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "to_telco"}))
    telco_success = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "telco_success"}))
    to_telco_onnet = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "to_telco_onnet"}))
    telco_onnet_success = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "telco_onnet_success"}))
    to_telco_offnet = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "to_telco_offnet"}))
    telco_offnet_success = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "telco_offnet_success"}))
    dlr_waiting = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "dlr_waiting"}))
    dlr_expire = forms.IntegerField(widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "dlr_expire"}))
    
    class Meta:
        model = Transaction
        fields = "__all__"
        exclude = ["user"]

