from django import forms

from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'restaurant_name', 'phone_no', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already taken.")
        return email

    def clean_phone_no(self):
        phone_no = self.cleaned_data.get('phone_no')
        if phone_no and User.objects.filter(phone_no=phone_no).exists():
            raise forms.ValidationError("This phone number is already registered.")
        return phone_no


# forms.py

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')
