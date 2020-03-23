from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from . import views

router = routers.DefaultRouter()
router.register(r'products', views.ProductViewSet, base_name='products'),
router.register(r'categories', views.CategoryViewSet, base_name='categories'),
router.register(r'bills', views.BillsViewSet, base_name='bills'),

urlpatterns = [
    path('', include(router.urls)),
]
