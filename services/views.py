from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum
from tablib import Dataset
import datetime as dt
import os

from accounts.models import User, UserProfile
from accounts.forms import UserForm
from .models import Transaction, Recharge, Tariff
from .forms import RechargeForm, TransactionForm


def ao_dash(request):
    users = User.objects.all()
    
    total_values = {}
    for user in users:
        if user.profile.system_id:
            total_values[user.profile.system_id] = {}
            transactions = Transaction.objects.filter(user=user)
            
            total_values[user.profile.system_id]["to_scrubber"] = transactions.aggregate(Sum("to_scrubber"))["to_scrubber__sum"]
            total_values[user.profile.system_id]["scrubb_success"] = transactions.aggregate(Sum("scrubb_success"))["scrubb_success__sum"]
            total_values[user.profile.system_id]["to_telco"] = transactions.aggregate(Sum("to_telco"))["to_telco__sum"]
            total_values[user.profile.system_id]["telco_success"] = transactions.aggregate(Sum("telco_success"))["telco_success__sum"]
            total_values[user.profile.system_id]["to_telco_onnet"] = transactions.aggregate(Sum("to_telco_onnet"))["to_telco_onnet__sum"]
            total_values[user.profile.system_id]["telco_onnet_success"] = transactions.aggregate(Sum("telco_onnet_success"))["telco_onnet_success__sum"]
            total_values[user.profile.system_id]["to_telco_offnet"] = transactions.aggregate(Sum("to_telco_offnet"))["to_telco_offnet__sum"]
            total_values[user.profile.system_id]["telco_offnet_success"] = transactions.aggregate(Sum("telco_offnet_success"))["telco_offnet_success__sum"]
            total_values[user.profile.system_id]["dlr_waiting"] = transactions.aggregate(Sum("dlr_waiting"))["dlr_waiting__sum"]
            total_values[user.profile.system_id]["dlr_expire"] = transactions.aggregate(Sum("dlr_expire"))["dlr_expire__sum"]
    
    for user in users:
        if user.profile.system_id:
            try:
                total_values[user.profile.system_id]["scrubb_fail"] = total_values[user.profile.system_id]["to_scrubber"] - total_values[user.profile.system_id]["scrubb_success"]
                total_values[user.profile.system_id]["telco_fail"] = total_values[user.profile.system_id]["to_telco"] - total_values[user.profile.system_id]["telco_success"]
            except:
                total_values[user.profile.system_id]["scrubb_fail"] = None
                total_values[user.profile.system_id]["telco_fail"] = None
            try:
                recharge = Recharge.objects.filter(user=user).last()
                total_values[user.profile.system_id]["amount"] = recharge.amount
                total_values[user.profile.system_id]["sms"] = recharge.sms_count
                total_values[user.profile.system_id]["recharge_date"] = recharge.recharge_date
                total_values[user.profile.system_id]["expiry_date"] = recharge.expiry_date
            except:
                total_values[user.profile.system_id]["amount"] = None
                total_values[user.profile.system_id]["sms"] = None
                total_values[user.profile.system_id]["recharge_date"] = None
                total_values[user.profile.system_id]["expiry_date"] = None
                
    context = {
        "total_values": total_values,
    }
    return render(request, "services/ao_dash.html", context)


def create_customer(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
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
            
            system_id = request.POST["system_id"]
            profile = UserProfile.objects.get(user=user)
            profile.system_id = system_id
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
            recharge.save()
            messages.success(request, 'Recharge details added sucessfully!')
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
        messages.success(request, 'Database has been updated sucessfully!')
        return redirect("ao_dash")
    else:
        return render(request, "errors/404.html")

