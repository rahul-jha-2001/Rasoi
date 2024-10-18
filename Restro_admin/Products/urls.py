from django.urls import path,include
from .views import ProductView,ListProductView
urlpatterns = [
    path("",ProductView.as_view(),name = "ProductView"),
     path('list/', ListProductView.as_view(), name='product-list')
]
