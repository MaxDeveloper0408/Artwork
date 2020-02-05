from django.conf .urls import url
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import  AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator,OriginValidator
from .consumers.notifications.routers import NOTIFICATION_URLS

ALLURLS = []
ALLURLS.extend(NOTIFICATION_URLS)

application = ProtocolTypeRouter({
                 # checks for Allowed hosts
    'websocket': AllowedHostsOriginValidator(
        # # Same as Login Required
        AuthMiddlewareStack(
            URLRouter(ALLURLS)
        )
    )
})
