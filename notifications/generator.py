# Notification Generators
from .models import Notifications
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from Aartcy.utils import get_or_none
from Aartcy.utils.codes import *
from arts.serializers import ProductSerializer
import json

channel_layer = get_channel_layer()

class NotificationGenerator:

    def __init__(self,**kwargs):

        self.kwargs = kwargs
        self.socket = 'notify'


    def payment_status_notification(self):

        email =  self.kwargs['email']
        self.product = self.kwargs['product']
        collector = get_or_none(User,email=email)
        artist = self.kwargs['user']


        self.status = self.kwargs['status']
        self.uid = self.kwargs['status']

        if collector:  #if collector found
            token = get_or_none(Token,user=collector)

            if token: # if collector has token send socket notification and create notification
                self.token = f'SOCKET-{token.key}'
                self.context = {"new": True}
                self.code = 'CO'
                self.reciever = collector
                self.notification_creator()


        token = get_or_none(Token, user=artist)
        if token:
            self.token = f'SOCKET-{token.key}'
            self.context = {"new": True}
            self.code = 'AO'
            self.reciever = artist
            self.notification_creator()


    def notification_creator(self):
        data = {}
        self.context['message'] = codes[self.code].get(self.status)
        self.context['status'] = self.status
        self.context['product'] = ProductSerializer(instance=self.product).data
        notification = Notifications.objects.create(user=self.reciever,message=data)
        notification.save()

        self.send_notification()
        return notification


    def send_notification(self):
        context = {"type": self.socket}
        context['text']= self.context
        async_to_sync(channel_layer.group_send)(self.token, context)
