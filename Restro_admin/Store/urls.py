from django.urls import path,include
from .views import StoreView
urlpatterns = [
    path("",StoreView.as_view(),name = "StoreGet"),
    path("<str:StoreUuid>",StoreView.as_view(),name = "StorePatch")
]
