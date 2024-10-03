from django.urls import path,include
from .views import signup_view,login_view,logout_view
urlpatterns = [

    
    path("register/",signup_view.as_view(),name = "User_register"),
    path("login/",login_view.as_view(),name = "User_login"),
    path("logout/",logout_view.as_view(),name = "User_logout")


]
