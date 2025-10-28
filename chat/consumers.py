from channels.generic.websocket import WebsocketConsumer
from .models import ChatChannels, ChatMessage
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
import json


class ChatChannelConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        self.chat_channel_name = self.scope["url_route"]["kwargs"]["channel_name"]
        self.channel = get_object_or_404(ChatChannels, channel_name=self.chat_channel_name)
        async_to_sync(self.channel_layer.group_add)(
            self.chat_channel_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chat_channel_name, self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message", "")
        saved_message = ChatMessage.objects.create(
            message=message,
            author=self.user,
            channel=self.channel
        )

        event = {
            "type": "message_handler",
            "message_id": saved_message.id
        }
        
        async_to_sync(self.channel_layer.group_send)(self.chat_channel_name, event)
        
    def message_handler(self, event):
        message_id = event.get("message_id")
        message = get_object_or_404(ChatMessage, id=message_id)
        html = render_to_string("chat/partial/message_partial.html", {
            "message": message, 
            "user": message.author
            })
        self.send(text_data=html)