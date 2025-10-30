from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatChannels, ChatMessage
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import Http404
from asgiref.sync import sync_to_async
import json


class ChatChannelConsumer(AsyncWebsocketConsumer):
    
    @staticmethod
    async def aget_object_or_404(klass, *args, **kwargs):    
        if hasattr(klass, 'aget'):
            queryset = klass
            model_name = queryset.model._meta.object_name
        else:
            queryset = klass.objects
            model_name = klass._meta.object_name
        
        try:
            return await queryset.aget(*args, **kwargs)
        except queryset.model.DoesNotExist:
            raise Http404(f"No {model_name} matches the given query.")
        
    
    async def connect(self):
        self.user = self.scope["user"]
        self.chat_channel_name = self.scope["url_route"]["kwargs"]["channel_name"]
        self.channel = await self.aget_object_or_404(ChatChannels, channel_name=self.chat_channel_name)
        await self.channel_layer.group_add(
            self.chat_channel_name, self.channel_name
        )
        
        is_online = await self.channel.users_online.filter(id=self.user.id).aexists()
        if not is_online:
            await sync_to_async(self.channel.users_online.add)(self.user) # in django v6 you can remove this part
            await self.update_online_users_count()
            
        await self.accept()

    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_channel_name, self.channel_name
        )
    
        is_online = await self.channel.users_online.filter(id=self.user.id).aexists()
        if is_online:
            await sync_to_async(self.channel.users_online.remove)(self.user)
            await self.update_online_users_count()
            

    async def receive(self, text_data=None, bytes_data=None):
        # this is a place for receiving content form the websocket connection
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message", "")
        saved_message = await ChatMessage.objects.acreate(
            message=message,
            author=self.user,
            channel=self.channel
        )

        event = {
            "type": "message_handler",
            "message_id": saved_message.id
        }

        await self.channel_layer.group_send(self.chat_channel_name, event)
    
    
    @staticmethod
    @sync_to_async
    def render_message_html(partial, context):
        # base for render the html message for group send . work with asyncWebsocketConsumer
        return render_to_string(partial, context)
    
    
    async def message_handler(self, event):
        # handler for broadcasting new messages
        message_id = event.get("message_id")
        message = await self.aget_object_or_404(ChatMessage, id=message_id)
        html = await self.render_message_html("chat/partial/message_partial.html", {
            "message": message, 
            "user": self.user
        }) 
        await self.send(text_data=html)
    
        
    async def update_online_users_count(self):
        online_count = await sync_to_async(self.channel.users_online.count)() - 1
        event = {
            "type": "online_count_handler",
            "online_count": online_count
        }
        await self.channel_layer.group_send(self.chat_channel_name, event)
    
    # handler for broadcasting online user count.
    async def online_count_handler(self, event):
        online_count = event["online_count"]
        html = await self.render_message_html("chat/partial/online_count.html", {"online_count": online_count})
        await self.send(text_data=html) 