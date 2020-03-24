from django.urls import path
from rest_framework import routers
from django.views.decorators.csrf import csrf_exempt
from . import views

router = routers.DefaultRouter()

urlpatterns = [
    # path('',include(router.urls)),
    path('oauth-link/', views.oauth_link, name='ouath_link'),
    path('connect-stripe/', views.ConnectStripe.as_view(), name='connect_stripe'),
    path('save_payment/', views.SavePayment.as_view(), name='checkout'),
    path('payment_intent/', views.PaymentIntent.as_view(), name='payment_intent'),
    path('link-checkout/<uid>/', views.CheckoutViaLink.as_view(), name='chceckout_via_mail')
]
