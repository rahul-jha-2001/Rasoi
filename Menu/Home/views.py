from django.shortcuts import render, redirect
from .forms import userDetailFormDineIn
from django.core.cache import cache
from django.views import View
from django.http import request,response,HttpResponse
import random





class Home(View):
    
    def get(self,request,storeId):
        #self.store_id = request.POST.get('storeId')
        self.order_type = request.POST.get('orderType')
        self.table_no = request.POST.get('table_no', None)  # Only for dine-in

        if 'user_name' not in request.session or 'phone_number' not in request.session:
            form = userDetailFormDineIn()
            return render(request, 'Home/user_details.html', {'form': form})
        
        return HttpResponse(f"User logedin at {storeId}")
    def post(self,request,storeId):
        form = userDetailFormDineIn(request.POST)
        
        #self.store_id = request.GET.get('storeId')
        self.order_type = request.GET.get('orderType')
        self.table_no = request.GET.get('table_no', None)  # Only for dine-in
        if form.is_valid():
            # Extract form data
            name = form.cleaned_data['name']
            phone_number = form.cleaned_data['phoneNo']
            otp = form.cleaned_data['otp']

            # Verify OTP
            # if verify_otp(phone_number, otp):
            #     # Save user details in session
            request.session['user_name'] = name
            request.session['phone_number'] = phone_number
                # Redirect to same page to reload with session data
            return redirect(f"/?store_id={storeId}&type={self.order_type}&table_no={self.table_no}")
        else:
                # OTP is invalid, render the form with error message
            return render(request, 'Home/user_details.html', {'form': form, 'error': 'Invalid OTP'})
# Create your views here.
