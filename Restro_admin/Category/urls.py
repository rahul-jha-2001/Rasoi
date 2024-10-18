from django.urls import path,include
from .views import CategoryView,ListCategoryView

urlpatterns = [
    path("",CategoryView.as_view(),name = "Category"),
    path("list",ListCategoryView.as_view(),name = "ListCategory")
]
