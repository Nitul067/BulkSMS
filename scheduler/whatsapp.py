from accounts.models import UserProfile
from services.models import Recharge, Rollback, Message
import pywhatkit as wk
import datetime as dt


def send_message():
    users = UserProfile.objects.filter(system_id__isnull=False)
    
    for user_profile in users:
        messages = Message.objects.get(user=user_profile.user)
        rollbacks = Rollback.objects.filter(user=user_profile.user).last()
        recharges = Recharge.objects.filter(user=user_profile.user).last()
        phone = f"+91{str(user_profile.user.phone_number)}"
        sms = recharges.sms_count + messages.forwarded_sms + rollbacks.rollback_sms
        total_sms = f"Total SMS: {str(sms)}"
        remaining_sms = f"Remaining SMS: {str(sms - messages.cur_used_sms)}"
        expiry = f"Expiry Date: {str(recharges.expiry_date)}"
        message = total_sms + "\n" + remaining_sms + "\n" + expiry
        
        now = dt.datetime.now()
        wk.sendwhatmsg(phone, message, now.hour, int(now.minute)+1, 15, True, 2)
    