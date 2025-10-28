from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/chat/<str:channel_name>/", consumers.ChatChannelConsumer.as_asgi()),
]
