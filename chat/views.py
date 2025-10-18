from django.shortcuts import render
from .models import ChatChannels
from django.contrib.auth.decorators import login_required


@login_required
def chat_view(request):
    channel = ChatChannels.objects.filter(channel_name="dota_chat").prefetch_related('channel_messages').first()
    channel_messages = channel.channel_messages.all()[:30]
    return render(request, "chat/chat.html", {"channel": channel, "channel_messages": channel_messages})
