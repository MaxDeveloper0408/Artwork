from .consumers import *
from django.conf .urls import url

NOTIFICATION_URLS = [
    url(r'^notifications/(?P<token>[\w.@+-]+)',NotificationConsumer)
]
