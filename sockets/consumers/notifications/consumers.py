import asyncio
import json
from django.contrib.auth.models import User
from channels.consumer import AsyncConsumer
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async

__all__ = ['NotificationConsumer']

class NotificationConsumer(AsyncConsumer):

    async def websocket_connect(self,event): # on connection
        await self.send({'type':'websocket.accept'})
        token = self.scope['url_route']['kwargs']['token']
        suid = 'SOCKET-'+token
        self.suid = suid
        await self.channel_layer.group_add(suid,self.channel_name) #creating group for notification
        await self.send({"type": "websocket.send"}) #use websocket.send while using groups else use websocket.accept

    async def websocket_recieve(self,event):
        # when message is recieved from the frontend
        ev = {'type': 'notify','message':'notification'}
        await self.channel_layer.group_send(self.suid,ev)

    async def notify(self, event):
        context = {"type":"websocket.send",'text':json.dumps(event['text'])}
        await self.send(context)

    async def websocket_disconnect(self,event):
        # when the scoket disconnects
        pass

    @database_sync_to_async
    def getuser(self,token):
        return Token.objects.get(key=token).user
