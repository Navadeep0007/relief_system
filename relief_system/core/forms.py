from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import UserProfile, Donation, Request, Delivery


class SignUpForm(UserCreationForm):
    role = forms.ChoiceField(choices=UserProfile.Roles.choices)

    class Meta:
        model = User
        fields = ("username", "email", "role", "password1", "password2")


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ("title", "description", "category", "quantity", "location", "is_active")


class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ("title", "description", "category", "quantity", "location", "is_fulfilled")


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ("donation", "request", "coordinator", "status", "pickup_time", "dropoff_time", "notes")


class DeliveryStatusForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ("status", "pickup_time", "dropoff_time", "notes")

