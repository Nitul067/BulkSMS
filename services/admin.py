from django.contrib import admin
from .models import Recharge, Transaction, Tariff


class CustomTariff(admin.ModelAdmin):
    list_display = ("plan", "value", "sms_count", "validity")
    ordering = ("id",)

admin.site.register(Recharge)
admin.site.register(Transaction)
admin.site.register(Tariff, CustomTariff)
