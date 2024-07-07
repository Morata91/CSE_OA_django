from django.urls import path
from . import views

urlpatterns = [
    path('stocks', views.ProductView.as_view()),
    path('stocks/<str:name>', views.ProductView.as_view()),
    path('sales', views.SalesView.as_view()),
]
