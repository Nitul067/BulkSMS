from django.shortcuts import render, redirect
from django.contrib import messages
from tablib import Dataset
import datetime as dt
import os

from accounts.models import User, UserProfile
from .models import Transaction, Recharge
from .forms import RechargeForm


def ao_dash(request):
    return render(request, "services/ao_dash.html")


def add_recharge(request):
    user_profile = UserProfile.objects.all()
    pending_recharge = Recharge.objects.filter(status="Pending")
    
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


def update_recharge(request):
    user_profile = UserProfile.objects.all()
    
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
        "form": form,
    }
    return render(request, "services/recharge.html", context)


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

