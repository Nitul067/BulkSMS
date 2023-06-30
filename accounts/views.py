from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from .forms import UserForm, UserUpdateForm, UserProfileForm
from .models import User
from .utils import send_verification_email


def register(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in.")
        return redirect("home")
    elif request.method == "POST":
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
            user.save()

            # Send verification email
            mail_subject = "Please activate your account"
            email_template = "accounts/emails/account_verification_email.html"
            send_verification_email(request, user, mail_subject, email_template)
            messages.success(request, "Your account has been registered sucessfully!")
            return redirect("home")
        else:
            print(form.errors)
    else:
        form = UserForm()
    context = {
        "form": form,
    }
    return render(request, "accounts/register.html", context)


def activate(request, uidb64, token):
    # Activate the user by setting the is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Congratulation! Your account is activated.")
        return redirect("home")
    else:
        messages.error(request, "Invalid activation link")
        return redirect("home")


def login(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in.")
        return redirect("account")
    elif request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect("home")
        else:
            try:
                user_obj = User.objects.filter(email=email).first()
                if user_obj.is_active:
                    messages.error(request, "Invalid password.")
                else:
                    messages.info(request, "Please verify your email to login.")
            except:
                messages.error(request, "Email does not exist.")
            return redirect("login")
    return render(request, "accounts/login.html")


@login_required(login_url="login")
def logout(request):
    auth.logout(request)
    messages.info(request, "You are logged out.")
    return redirect("login")


@login_required(login_url="login")
def account(request):
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()
            messages.success(request, "Your account has been updated sucessfully!")
            return redirect("account")
    else:
        form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)
    context = {
        "form": form,
        "profile_form": profile_form,
    }
    return render(request, "accounts/account.html", context)


def forgot_password(request):
    if request.method == "POST":
        email = request.POST["email"]

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)

            # send reset password email
            mail_subject = "Reset Your Password"
            email_template = "accounts/emails/reset_password_email.html"
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(
                request, "Password reset link has been sent to your email address."
            )
            return redirect("login")
        else:
            messages.error(request, "Account does not exist")
            return redirect("forgot_password")
    return render(request, "accounts/forgot_password.html")


def reset_password_validate(request, uidb64, token):
    # validate the user by decoding the token and user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.info(request, "Please reset your password")
        return redirect("reset_password")
    else:
        messages.error(request, "This link has been expired!")
        return redirect("forgot_password")


def reset_password(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            pk = request.session.get("uid")
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, "Password reset successful")
            return redirect("login")
        else:
            messages.error(request, "Password do not match!")
            return redirect("reset_password")
    return render(request, "accounts/reset_password.html")


@login_required(login_url="login")
def delete_account(request):
    if request.method == "POST":
        user = User.objects.get(id=request.user.id)
        try:
            if request.POST["accountDeactivation"] == "on":
                user.delete()
                messages.success(request, "Your account has been deleted sucessfully!")
                return redirect("home")
        except:
            messages.info(
                request,
                "Check 'I confirm my account deactivation' to delete your account",
            )
            return redirect("account")

    return render(request, "errors/404.html")
