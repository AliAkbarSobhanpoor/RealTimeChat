from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatChannels(models.Model):
    channel_name = models.CharField(max_length=100, unique=True)


    def __str__(self):
        return self.channel_name


class ChatMessage(models.Model):
    channel = models.ForeignKey(ChatChannels, related_name='channel_messages', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name="author_messages" , on_delete=models.CASCADE)
    message = models.TextField(max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.author} in {self.channel}: {self.message[:20]}..."

    class Meta:
        ordering = ['timestamp'] # newest to the oldest
        