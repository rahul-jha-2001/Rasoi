from django.urls import path,include
from .views import LoginView,RegisterView,UserView
urlpatterns = [
    path("register/",RegisterView.as_view(),name = "User_register"),
    path("login/",LoginView.as_view(),name = "User_login"),
    path("<str:Email>",UserView.as_view(),name = "User")
    # path("logout/",logout_view.as_view(),name = "User_logout")
]
