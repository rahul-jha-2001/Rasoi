from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.views import View
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from django.contrib.auth.hashers import check_password,make_password
from django.contrib import messages
from .froms import CustomUserCreationForm,UserLoginForm


class signup_view(View):

    def get(self,request):
        form =  CustomUserCreationForm()
        return render(request,"User/user_creation_form.html",{"form":form})
    def post(self,request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse('DashBoard'))
        else:
            return render(request,"User/user_creation_form.html",{"form":form})
class login_view(View):
    
    def get(self,request):
         if request.user.is_authenticated:
             return redirect("DashBoard")
         else:
             form = AuthenticationForm()
             return render(request,"User/user_auth_form.html",{"form":form})
    def post(self,request):
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('DashBoard'))  # Redirect to dashboard or homepage after login
            else:
                messages.error(request, "Invalid email or password")
        else:
            messages.error(request, "Invalid login credentials")
            
        return render(request,"User/user_auth_form.html",{"form":form})

class logout_view(View):
    def get(self,request):
        messages.info(request,f"{request.user}")
        if request.user.is_authenticated:
            logout(request)
            return HttpResponse("Logout")
        else:
            return redirect("User_login")

