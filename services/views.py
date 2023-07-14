from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum
from tablib import Dataset
from xhtml2pdf import pisa
import datetime as dt
import os

from accounts.models import User, UserProfile
from accounts.forms import UserForm
from .models import Transaction, Recharge, Message, Rollback, Tariff
from .forms import RechargeForm, TransactionForm
from .utils import link_callback


@login_required(login_url="login")
def ao_dash(request):
    users = User.objects.all()
    
    total_values = {}
    for user in users:
        if user.profile.system_id:
            total_values[user.profile.system_id] = {}
            recharge = Recharge.objects.filter(user=user).last()
            message = Message.objects.filter(user=user).last()
            transactions = Transaction.objects.filter(user=user)
            try:
                total_values[user.profile.system_id]["id"] = user.id
                total_values[user.profile.system_id]["transactions"] = transactions
                total_values[user.profile.system_id]["amount"] = recharge.amount
                total_values[user.profile.system_id]["total_sms"] = recharge.sms_count
                total_values[user.profile.system_id]["recharge_date"] = recharge.recharge_date
                total_values[user.profile.system_id]["expiry_date"] = recharge.expiry_date
                total_values[user.profile.system_id]["used_sms"] = message.cur_used_sms
                total_values[user.profile.system_id]["failed_sms"] = message.cur_failed_sms
                total_values[user.profile.system_id]["forwarded_sms"] = message.forwarded_sms
                total_values[user.profile.system_id]["remaining_sms"] = recharge.sms_count - message.cur_used_sms
            except:
                total_values[user.profile.system_id]["transactions"] = None
                total_values[user.profile.system_id]["amount"] = None
                total_values[user.profile.system_id]["total_sms"] = None
                total_values[user.profile.system_id]["recharge_date"] = None
                total_values[user.profile.system_id]["expiry_date"] = None
                total_values[user.profile.system_id]["used_sms"] = None
                total_values[user.profile.system_id]["failed_sms"] = None
                total_values[user.profile.system_id]["forwarded_sms"] = None
                total_values[user.profile.system_id]["remaining_sms"] = None
            
    
    # for user in users:
    #     if user.profile.system_id:
    #         total_values[user.profile.system_id] = {}
    #         transactions = Transaction.objects.filter(user=user)
            
    #         total_values[user.profile.system_id]["to_scrubber"] = transactions.aggregate(Sum("to_scrubber"))["to_scrubber__sum"]
    #         total_values[user.profile.system_id]["scrubb_success"] = transactions.aggregate(Sum("scrubb_success"))["scrubb_success__sum"]
    #         total_values[user.profile.system_id]["to_telco"] = transactions.aggregate(Sum("to_telco"))["to_telco__sum"]
    #         total_values[user.profile.system_id]["telco_success"] = transactions.aggregate(Sum("telco_success"))["telco_success__sum"]
    #         total_values[user.profile.system_id]["to_telco_onnet"] = transactions.aggregate(Sum("to_telco_onnet"))["to_telco_onnet__sum"]
    #         total_values[user.profile.system_id]["telco_onnet_success"] = transactions.aggregate(Sum("telco_onnet_success"))["telco_onnet_success__sum"]
    #         total_values[user.profile.system_id]["to_telco_offnet"] = transactions.aggregate(Sum("to_telco_offnet"))["to_telco_offnet__sum"]
    #         total_values[user.profile.system_id]["telco_offnet_success"] = transactions.aggregate(Sum("telco_offnet_success"))["telco_offnet_success__sum"]
    #         total_values[user.profile.system_id]["dlr_waiting"] = transactions.aggregate(Sum("dlr_waiting"))["dlr_waiting__sum"]
    #         total_values[user.profile.system_id]["dlr_expire"] = transactions.aggregate(Sum("dlr_expire"))["dlr_expire__sum"]
    
    # for user in users:
    #     if user.profile.system_id:
    #         try:
    #             total_values[user.profile.system_id]["scrubb_fail"] = total_values[user.profile.system_id]["to_scrubber"] - total_values[user.profile.system_id]["scrubb_success"]
    #             total_values[user.profile.system_id]["telco_fail"] = total_values[user.profile.system_id]["to_telco"] - total_values[user.profile.system_id]["telco_success"]
    #         except:
    #             total_values[user.profile.system_id]["scrubb_fail"] = None
    #             total_values[user.profile.system_id]["telco_fail"] = None
    #         try:
    #             recharge = Recharge.objects.filter(user=user).last()
    #             total_values[user.profile.system_id]["amount"] = recharge.amount
    #             total_values[user.profile.system_id]["sms"] = recharge.sms_count
    #             total_values[user.profile.system_id]["recharge_date"] = recharge.recharge_date
    #             total_values[user.profile.system_id]["expiry_date"] = recharge.expiry_date
    #         except:
    #             total_values[user.profile.system_id]["amount"] = None
    #             total_values[user.profile.system_id]["sms"] = None
    #             total_values[user.profile.system_id]["recharge_date"] = None
    #             total_values[user.profile.system_id]["expiry_date"] = None
                
    context = {
        "total_values": total_values,
    }
    return render(request, "services/ao_dash.html", context)


@login_required(login_url="login")
def create_customer(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            system_id = request.POST["system_id"]
            rollback_pct = request.POST["rollback_pct"]
            system_ids = UserProfile.objects.all().values_list("system_id")

            if (system_id, ) in list(system_ids):
                messages.info(request, "Customer already exist!")
            else:    
                first_name = form.cleaned_data["first_name"]
                last_name = form.cleaned_data["last_name"]
                username = form.cleaned_data["username"]
                email = form.cleaned_data["email"]
                phone_number = form.cleaned_data["phone_number"]
                password = form.cleaned_data["password"]
                user = User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                    phone_number=phone_number,
                    password=password,
                )
                user.is_active = True
                user.save()
                
                profile = UserProfile.objects.get(user=user)
                profile.system_id = system_id
                profile.rollback_pct = rollback_pct
                profile.save()
                
                messages.success(request, "Customer has been created sucessfully!")
                return redirect("ao_dash")
        else:
            print(form.errors)
    else:
        form = UserForm()
        
    context = {
        "form": form,
    }
    return render(request, "services/create_customer.html", context)


@login_required(login_url="login")
def add_recharge(request):
    user_profile = UserProfile.objects.all()
    pending_recharge = Recharge.objects.exclude(status="Completed")
    
    if request.method == "POST":
        user_id = request.POST["user_id"]
        user = User.objects.get(id=user_id)
        form = RechargeForm(request.POST)
        
        if form.is_valid():
            recharge = form.save(commit=False)
            recharge.user = user
            if recharge.status == "Completed":
                tariff = Tariff.objects.filter(value=recharge.amount, sms_count=recharge.sms_count).first()
                recharge.expiry_date = recharge.recharge_date + dt.timedelta(tariff.validity)
                recharge.save()
            recharge.save()
            messages.success(request, 'Recharge details added sucessfully!')
            
            recharge = Recharge.objects.filter(user=user)
            
            if len(recharge) < 2:
                sms = Message.objects.create(
                    user = user,
                    pre_total_sms = 0,
                    pre_used_sms = 0,
                    pre_failed_sms = 0,
                    forwarded_sms = 0,
                    cur_total_sms = recharge.last().sms_count,
                    cur_used_sms = 0,
                    cur_failed_sms = 0
                )
                sms.save()
            else:
                sms = Message.objects.get(user=user)
                sms.pre_total_sms = sms.cur_total_sms
                sms.pre_used_sms = sms.cur_used_sms
                sms.pre_failed_sms = sms.cur_failed_sms
                if recharge.last().recharge_date <= recharge[len(recharge)-1].expiry_date:
                    sms.forwarded_sms = sms.cur_total_sms - sms.cur_used_sms
                sms.cur_total_sms = recharge.last().sms_count
                sms.cur_used_sms = 0
                sms.cur_failed_sms = 0
                sms.save()
            
            return redirect("add_recharge")
        else:
            print(form.errors)
    else:
        form = RechargeForm()
    context = {
        "user_profile": user_profile,
        "pending_recharge": pending_recharge,
        "form": form,
    }
    return render(request, "services/recharge.html", context)


@login_required(login_url="login")
def update_recharge(request, id):
    recharge = Recharge.objects.get(id=id)
    pending_recharge = Recharge.objects.exclude(status="Completed")
    
    if request.method == "POST":
        form = RechargeForm(request.POST, instance=recharge)
        
        if form.is_valid():
            form.save()
            
            recharge = Recharge.objects.get(id=id)
            if recharge.status == "Completed":
                tariff = Tariff.objects.filter(value=recharge.amount, sms_count=recharge.sms_count).first()
                recharge.expiry_date = recharge.recharge_date + dt.timedelta(tariff.validity)
                recharge.save()
            messages.success(request, 'Recharge details updated sucessfully!')
            return redirect("update_recharge", id)
        else:
            messages.error(request, form.errors)
    else:
        form = RechargeForm(instance=recharge)
        
    context = {
        "form": form,
        "recharge": recharge,
        "pending_recharge": pending_recharge,
    }
    return render(request, "services/update_recharge.html", context)


@login_required(login_url="login")
def add_transaction(request):
    user_profile = UserProfile.objects.all()
    
    if request.method == "POST":
        user_id = request.POST["user_id"]
        user = User.objects.get(id=user_id)
        form = TransactionForm(request.POST)
        
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = user
            transaction.save()
            messages.success(request, 'Transaction details added sucessfully!')
            
            sms = Message.objects.get(user=user)
            failed_sms = transaction.to_scrubber - transaction.telco_success
            sms.cur_used_sms += transaction.to_scrubber
            sms.cur_failed_sms += failed_sms
            
            # if (sms.forwarded_sms != 0) and (sms.cur_used_sms >= sms.forwarded_sms):
            #     diff_sms = sms.cur_used_sms - sms.forwarded_sms
            #     total_failed_sms = sms.pre_failed_sms + sms.cur_failed_sms
            #     failed_submission = round((total_failed_sms / sms.pre_total_sms) * 100, 2)
            #     if failed_submission > 15:
            #         sms.rollback_sms = round(((failed_submission - 15) / 100) * sms.pre_total_sms)
            #         sms.cur_total_sms += sms.rollback_sms
            #     sms.cur_used_sms = diff_sms
            #     sms.pre_used_sms += sms.forwarded_sms
            #     sms.pre_failed_sms = total_failed_sms
            #     sms.cur_failed_sms = 0
            #     sms.forwarded_sms = 0
            sms.save()
            
            return redirect("add_trans")
        else:
            messages.error(request, form.errors)
    else:
        form = TransactionForm()
    
    context = {
        "user_profile": user_profile,
        "form": form,
    }
    return render(request, "services/add_transaction.html", context)


@login_required(login_url="login")
def upload_transactions(request):
    if request.method == "POST":
        dataset = Dataset()
        transactions = request.FILES["my_file"]
        ext = os.path.splitext(transactions.name)[1]
        imported_data = dataset.load(transactions.read(), format=ext[1:])
        
        for data in imported_data:
            user_profile = UserProfile.objects.filter(system_id=data[1]).first()
            
            trans = Transaction(
                user = user_profile.user,
                trans_date = dt.datetime.strptime(data[0], "%Y-%m-%d").date(),
                nature = data[2] if data[2] else 0,
                header = data[3] if data[2] else 0,
                to_scrubber = data[4] if data[4] else 0,
                scrubb_success = data[5] if data[5] else 0,
                to_telco = data[9] if data[9] else 0,
                telco_success = data[10] if data[10] else 0,
                to_telco_onnet = data[12] if data[12] else 0,
                telco_onnet_success = data[13] if data[13] else 0,
                to_telco_offnet = data[14] if data[14] else 0,
                telco_offnet_success = data[15] if data[15] else 0,
                dlr_waiting = data[16] if data[16] else 0,
                dlr_expire = data[17] if data[17] else 0,
            )
            trans.save()
            
            sms = Message.objects.get(user=trans.user)
            failed_sms = trans.to_scrubber - trans.telco_success
            sms.cur_used_sms += trans.to_scrubber
            sms.cur_failed_sms += failed_sms
            sms.save()
            
        messages.success(request, 'Database has been updated sucessfully!')
        return redirect("ao_dash")
    else:
        return render(request, "errors/404.html")


@login_required(login_url="login")
def rollback(request, id, save):
    user = User.objects.get(id=id)
    rollbacks = Rollback.objects.filter(user=user)
    rb = rollbacks.last()
    
    if rb:
        transactions = Transaction.objects.filter(user=user, trans_date__gt=rb.rollback_date)
    else:
        transactions = Transaction.objects.filter(user=user)
        
    if transactions:
        used_sms = transactions.aggregate(Sum("to_scrubber"))["to_scrubber__sum"]
        failed_sms = used_sms - transactions.aggregate(Sum("telco_success"))["telco_success__sum"]
        failed_pct = round((failed_sms / used_sms) * 100, 5)
        rb_pct_limit = user.profile.rollback_pct
        if failed_pct > rb_pct_limit:
            rollback_sms = round((failed_pct - rb_pct_limit) * used_sms / 100)
        else:
            rollback_sms = 0
        
        new_rb = None
        if save:
            new_rb = Rollback.objects.create(
                user=user,
                used_sms=used_sms,
                failed_sms_pct=failed_pct,
                failed_sms=failed_sms,
                rb_from_date = transactions.last().trans_date,
                rollback_sms=rollback_sms,
            )
            new_rb.save()
        
        context = {
            "user_info": user,
            "rb_id": new_rb.id if new_rb else 0,
            "msg": "Rollback SMS Summary",
            "from_date": transactions.last().trans_date,
            "to_date": dt.date.today(),
            "used_sms": used_sms,
            "failed_sms": failed_sms,
            "failed_pct": failed_pct,
            "rb_pct_limit": rb_pct_limit,
            "rollback_sms": rollback_sms,
            "rollbacks": rollbacks,
        }
    else:
        rb = Rollback.objects.filter(user=user).last()
        context = {
            "user_info": user,
            "rb_id": rb.id,
            "error": "No transaction found for this period.",
            "from_date": rb.rb_from_date,
            "to_date": dt.date.today(),
            "used_sms": rb.used_sms,
            "failed_sms": rb.failed_sms,
            "failed_pct": rb.failed_sms_pct,
            "rb_pct_limit": user.profile.rollback_pct,
            "rollback_sms": rb.rollback_sms,
            "rollbacks": rollbacks,
        }
    return render(request, "services/rollback.html", context)


@login_required(login_url="login")
def customer_trans(request, id):
    user = User.objects.get(id=id)
    transactions = Transaction.objects.filter(user=user)
    
    context = {
        "user": user,
        "transactions": transactions,
    }
    return render(request, "services/customer_trans.html", context)


@login_required(login_url="login")
def customer_recharge(request, id):
    user = User.objects.get(id=id)
    recharges = Recharge.objects.filter(user=user)
    
    context = {
        "user": user,
        "recharges": recharges,
    }
    return render(request, "services/customer_recharge.html", context)


@login_required(login_url="login")
def pnl(request, id):
    user = User.objects.get(id=id)
    recharge = Recharge.objects.filter(user=user).last()
    transactions = Transaction.objects.filter(user=user)
    
    used_sms = transactions.aggregate(Sum("to_scrubber"))["to_scrubber__sum"]
    success_sms = transactions.aggregate(Sum("telco_success"))["telco_success__sum"]
    fail_sms = used_sms - success_sms
    success_sms_rate = round((success_sms / used_sms) * 100, 5)
    
    dot_rate = 15
    tanla_rate = 30
    licence_offnet_rate = 12.35
    licence_onnet_rate = 12.35
    rollback_rate = user.profile.rollback_pct 
    amount = recharge.amount

    sms_count = recharge.sms_count                              # X
    base_rate = round(amount / sms_count * 100, 5)              # A
    without_gst = round(base_rate / 1.18, 5)                    # B
    iuc_charge = 7                                              # C
    after_iuc = round(without_gst - iuc_charge, 5)              # D
    scrubbing_charge = 1                                        # E
    dot_charge = round(scrubbing_charge * dot_rate / 100, 5)                # F
    final_scrubbing_charge = round(scrubbing_charge - dot_charge, 5)        # G
    tanla_charge = round(final_scrubbing_charge * tanla_rate / 100, 5)      # H
    bsnl_revenue = scrubbing_charge - dot_charge - tanla_charge             # I
    licence_fee_offnet = round((after_iuc + bsnl_revenue) * licence_offnet_rate / 100, 5)       # J1
    licence_fee_onnet = round((without_gst + bsnl_revenue) * licence_onnet_rate / 100, 5)       # J2
    offnet_pnl_per_sms = after_iuc - dot_charge - tanla_charge - licence_fee_offnet             # K1
    onnet_pnl_per_sms = without_gst - dot_charge - tanla_charge - licence_fee_onnet             # K2
    offnet_market_share = 95                                    # L1
    onnet_market_share = 100 - offnet_market_share              # L2
    # success_sms_rate = 60                                       # M1
    fail_sms_rate = 100 - success_sms_rate                      # M2
    # success_sms = round(sms_count * success_sms_rate / 100)     # N
    offnet_success = round(success_sms * offnet_market_share / 100)                             # O1
    onnet_success = round(success_sms * onnet_market_share / 100)                               # O2
    offnet_pnl = round(offnet_success * offnet_pnl_per_sms / 100)                               # P1
    onnet_pnl = round(onnet_success * onnet_pnl_per_sms / 100)                                  # P2
    success_sms_pnl = offnet_pnl + onnet_pnl                                                    # Q
    # fail_sms = round(sms_count * fail_sms_rate / 100)                                           # R
    rollback_sms = round(sms_count * (fail_sms_rate - rollback_rate) / 100)                     # S
    fail_sms_cost_to_customer = fail_sms - rollback_sms                                         # T
    fail_sms_pnl = round(fail_sms_cost_to_customer * onnet_pnl_per_sms / 100)                   # U
    bsnl_pnl = success_sms_pnl + fail_sms_pnl                                                   # Z
    
    pnl_pct = round(bsnl_pnl / amount * 100, 2)
    
    context = {
        "user_info": user,
        "amount": amount,
        "pnl": bsnl_pnl,
        "pnl_pct": pnl_pct,
    }
    return render(request, "services/pnl.html", context)


@login_required(login_url="login")
def generate_pdf(request, id):
    rb = Rollback.objects.get(id=id)
    
    template_path = "services/generate_pdf.html"
    context = {
        "email": request.user,
        "rollback": rb,
    }
     
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="rollback_{rb.user.profile.system_id}-{rb.id}.pdf"'
    
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def ajax_sms_data(request):
    amount = request.GET.get('amount')
    if amount:
        tariff = Tariff.objects.filter(value=amount)
        sms_count = list(tariff.values_list("sms_count", flat=True))
        context = {
            "sms_count": sms_count
        }
    else:
        context = {
            "sms_count": None
        }
    return render(request, "services/sms_count_dropdown.html", context)

