from django.contrib import admin
from django.urls import path,include
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token
from . import views

router = routers.DefaultRouter()
router.register(r'networth',views.NetWorth,base_name='networth'),
router.register(r'goals',views.GoalViewSet,base_name='goals'),
router.register(r'populartags',views.PouplarTags,base_name='populartags'),
router.register(r'latestorders',views.LatestOrders,base_name='latestorders'),
router.register(r'topbuyers',views.TopBuyers,base_name='topbuyers'),
router.register(r'countmoney',views.CountMoney,base_name='count_money'),
router.register(r'collectordasboard',views.CollecterDashboard,base_name='collectordasboard'),
router.register(r'coa',views.CertificateOfAuthenticity,base_name='coa'),
# router.register(r'payouts',views.Payouts,base_name='payouts'),
router.register(r'transactions',views.Transactions,base_name='transactions'),
router.register(r'charges',views.Charges,base_name='charges'),
router.register(r'admin',views.AdminDashboard,base_name='admin'),


urlpatterns = [
    path('test/',views.testsocket),
    path('',include(router.urls)),


]
