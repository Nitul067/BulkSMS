from django import forms
from .models import User, UserProfile
from .validators import allow_only_images_validator


class UserForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First Name"}
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Last Name"}
        )
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"})
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Phone Number"}
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email Address"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        )
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm Password"}
        )
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "password",
        ]

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Password does not match!")


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={"class": "account-file-input"}),
        validators=[allow_only_images_validator],
    )

    class Meta:
        model = UserProfile
        fields = [
            "profile_picture",
        ]


class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First Name"}
        )
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Last Name"}
        )
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username"})
    )
    phone_number = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Phone Number"}
        )
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email Address"}
        )
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "phone_number"]
