from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
import chat
from .models import ChatChannels, ChatMessage
from django.contrib.auth.decorators import login_required
from .forms import ChatMessageForm
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

User = get_user_model()

@login_required
def chat_view(request, channel_name="dota_chat"):
    channel = ChatChannels.objects.filter(channel_name=channel_name).prefetch_related('channel_messages').first()
    
    other_user = None
    if channel.is_private:
        if request.user not in channel.members.all():
            raise Http404("You are not allowed to access this channel.")
        for member in channel.members.all():
            if member != request.user:
                other_user = member
                break
            
    
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
    return render(request, "chat/chat.html", {"channel_name": channel_name, "channel_messages": channel_messages, "form": form, "other_user": other_user})

@login_required
def get_or_create_channel(request, username):
    if request.user.username == username:
        return redirect("home")
    
    other_user = User.objects.get(username=username)
    my_chat_channels = request.user.chat_channels.filter(is_private=True)
    if my_chat_channels:
        for chat_channel in my_chat_channels:
            if other_user in chat_channel.members.all():
                chat_channel = chat_channel
                break
            else:
                chat_channel = ChatChannels.objects.create(is_private=True)
                chat_channel.members.add(request.user, other_user)
    else:
        chat_channel = ChatChannels.objects.create(is_private=True)
        chat_channel.members.add(request.user, other_user)
    
    return redirect("private_chat_channel", channel_name=chat_channel.channel_name)



def chat_file_upload(request, channel_name):
    chat_channel = get_object_or_404(ChatChannels, channel_name=channel_name)

    if request.htmx and request.FILES:
        uploaded_file = request.FILES['file']
        
        message = ChatMessage.objects.create(
            file=uploaded_file,
            author=request.user,
            channel=chat_channel
        )
        
        channel_layer = get_channel_layer()
        event = {
            "type": "message_handler",
            "message_id": message.id,
        }
        async_to_sync(channel_layer.group_send)(chat_channel.channel_name, event)
    return HttpResponse(status=200)