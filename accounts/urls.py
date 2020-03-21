from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from . import views

router = routers.DefaultRouter()
router.register(r'signup', views.Signup, base_name='signup'),
router.register(r'login', views.Login, base_name='login'),
router.register(r'forgot-password', views.ForgotPassword, base_name='forgot_password'),
router.register(r'profile', views.ProfileViewSet, base_name='profile'),
router.register(r'reset-password', views.ResetPassword, base_name='reset_password'),
router.register(r'role', views.RoleViewSet, base_name='role'),
router.register(r'list', views.UserViewSet, base_name='list'),

urlpatterns = [
    path('', include(router.urls)),
    path('activate/<secret>', views.activate, name='activate'),
    # path('reset-password/<secret>', views.ResetPassword.as_view(), name='reset_password'),
    path('twitter/login-url', views.twitter_login_url),
]
