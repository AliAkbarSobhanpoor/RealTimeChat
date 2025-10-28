from django.shortcuts import redirect, render
from .models import ChatChannels
from django.contrib.auth.decorators import login_required
from .forms import ChatMessageForm

@login_required
def chat_view(request):
    channel = ChatChannels.objects.filter(channel_name="dota_chat").prefetch_related('channel_messages').first()
    channel_messages = channel.channel_messages.all()[:30]
    if request.htmx:
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.channel = channel
            message.author = request.user
            message.save()
            return render(request, "chat/partial/message_partial.html", {"message": message, "user": message.author})
    form = ChatMessageForm()
    return render(request, "chat/chat.html", {"channel": channel, "channel_messages": channel_messages, "form": form})
