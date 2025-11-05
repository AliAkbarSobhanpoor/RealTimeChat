from django.db import models
from django.contrib.auth import get_user_model
import shortuuid
import os
import mimetypes
User = get_user_model()


class ChatChannels(models.Model):
    channel_name = models.CharField(max_length=100, unique=True, default=shortuuid.uuid)
    users_online = models.ManyToManyField(User, related_name="online_channels", blank=True)
    members = models.ManyToManyField(User, related_name="chat_channels", blank=True)
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.channel_name


class ChatMessage(models.Model):
    channel = models.ForeignKey(ChatChannels, related_name='channel_messages', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name="author_messages" , on_delete=models.CASCADE)
    message = models.TextField(max_length=300, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    
    def __str__(self):
        if self.message:
            return f"Message from {self.author} in {self.channel}: {self.message[:20]}..."
        else:
            file_name = os.path.basename(self.file.name)
            return f"file from {self.author}: file name is: {file_name}"
    
    @property
    def is_image(self):
        mimetype , _ = mimetypes.guess_type(self.file.name)
        if mimetype and mimetype.startswith("image/"):
            return True
        else:
            return False 
    
    class Meta:
        ordering = ['-timestamp']