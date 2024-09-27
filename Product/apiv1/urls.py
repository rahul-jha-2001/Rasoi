from django.urls import path,include
from .views import product_view,category_view
urlpatterns = [
    path("product",product_view.as_view(),name="Product"),
    path("category",category_view.as_view(),name="Category")
    ]