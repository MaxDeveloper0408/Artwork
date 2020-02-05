from django.contrib import admin
from django.urls import path,include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from . import views

router = routers.DefaultRouter()

urlpatterns = [
        path('usermenu/',views.UserSettings.as_view(),name='usermenu'),
        path('quote/',views.QuoteView.as_view(),name='quote')
]
