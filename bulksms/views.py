from django.shortcuts import render
from accounts.models import User


def home(request):
    if request.user.is_authenticated:
        user = User.objects.get(id=request.user.id)
        context = {
            "user": user,
        }
    context = {}
    return render(request, "index.html", context)
    