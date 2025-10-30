from django.urls import path
from . import views

urlpatterns = [
    path("", views.chat_view, name="chat_view"),
    path("chat/<username>", views.get_or_create_channel, name="start-chat"),
    path("chat/channel/<channel_name>", views.chat_view, name="private_chat_channel"),
]