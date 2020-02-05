from django.contrib import admin
from django.urls import path,include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from . import views

router = routers.DefaultRouter()

urlpatterns = [
    # path('',include(router.urls)),
    path('oauth-link/',views.oauth_link,name='ouath_link'),
    path('connect-stripe/',views.ConnectStripe.as_view(),name='connect_stripe'),
    path('checkout/',views.Checkout.as_view(),name='checkout'),
    path('link-checkout/<uid>/',views.CheckoutViaLink.as_view(),name='chceckout_via_mail')



]
