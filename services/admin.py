from django.contrib import admin
from .models import Recharge, Transaction, Message, Rollback, Tariff


class CustomRecharge(admin.ModelAdmin):
    list_display = ("user", "amount", "sms_count", "recharge_date")
    ordering = ("id",)


class CustomTransaction(admin.ModelAdmin):
    list_display = ("user", "trans_date", "nature", "header", "to_scrubber", 
                    "scrubb_success", "to_telco", "telco_success", "to_telco_onnet", 
                    "telco_onnet_success", "to_telco_offnet", "telco_offnet_success", 
                    "dlr_waiting", "dlr_expire")
    ordering = ("-id",)
    filter_horizontal = ()
    list_filter = ("user", )
    list_per_page = 50


class CustomMessage(admin.ModelAdmin):
    list_display = ("user", "pre_total_sms", "pre_used_sms", "pre_failed_sms", "forwarded_sms", 
                    "cur_total_sms", "cur_used_sms", "cur_failed_sms")
    ordering = ("-id",)


class CustomRollback(admin.ModelAdmin):
    list_display = ("user", "used_sms", "failed_sms", "failed_sms_pct", "rollback_sms", "rollback_date")
    ordering = ("-id",)


class CustomTariff(admin.ModelAdmin):
    list_display = ("plan", "value", "sms_count", "validity")
    ordering = ("id",)
    

admin.site.register(Recharge, CustomRecharge)
admin.site.register(Transaction, CustomTransaction)
admin.site.register(Message, CustomMessage)
admin.site.register(Rollback, CustomRollback)
admin.site.register(Tariff, CustomTariff)
