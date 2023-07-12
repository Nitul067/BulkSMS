from django.db import models
from accounts.models import User


class Recharge(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recharges')
    amount = models.FloatField()
    sms_count = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    recharge_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)

    def __str__(self) -> str:
        return self.user.email


class Transaction(models.Model):
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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    trans_date = models.DateField()
    nature = models.CharField(max_length=20, choices=NATURE_CHOICES, default='Trans')
    header = models.CharField(max_length=50, choices=HEADER_CHOICES, default='Regular')
    to_scrubber = models.IntegerField()
    scrubb_success = models.IntegerField()
    to_telco = models.IntegerField()
    telco_success = models.IntegerField()
    to_telco_onnet = models.IntegerField()
    telco_onnet_success = models.IntegerField()
    to_telco_offnet = models.IntegerField()
    telco_offnet_success = models.IntegerField()
    dlr_waiting = models.IntegerField()
    dlr_expire = models.IntegerField()
    
    def __str__(self) -> str:
        return self.user.profile.system_id


class Message(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='messages')
    pre_total_sms = models.IntegerField()
    pre_used_sms = models.IntegerField()
    pre_failed_sms = models.IntegerField()
    forwarded_sms = models.IntegerField(default=0)
    cur_total_sms = models.IntegerField()
    cur_used_sms = models.IntegerField()
    cur_failed_sms = models.IntegerField()
    rollback_sms = models.IntegerField(default=0)
    
    def __str__(self) -> str:
        return self.user.profile.system_id


class Rollback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rollbacks')
    used_sms = models.IntegerField()
    failed_sms = models.IntegerField()
    failed_sms_pct = models.FloatField(blank=True, null=True)
    rollback_sms = models.IntegerField()
    rb_from_date = models.DateField(blank=True, null=True)
    rollback_date = models.DateField(auto_now_add=True)
    
    def __str__(self) -> str:
        return self.user.profile.system_id
    

class Tariff(models.Model):
    plan = models.CharField(max_length=20, default="1000000")
    value = models.IntegerField()
    sms_count = models.IntegerField()
    validity= models.IntegerField()

    def __str__(self) -> str:
        return self.plan
