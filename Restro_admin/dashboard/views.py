from django.shortcuts import render,redirect
from django.views import View
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin

class dashboard(LoginRequiredMixin,View):
    
    login_url = reverse("User:User_login")
    redirect_field_name = None
    def get(self,request):

        # current_user = request.user
        # stores =  store_model.objects.get(user = current_user)

        return HttpResponse("Dashborad")
    
# class stores:
#     def get(self,request):


#     def post(self,request):

#     def put(self,request):

#     def delete(self,request);

# class product:
#     def get
#     def post
#     def put
#     def delete

# class 