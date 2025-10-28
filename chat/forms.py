from django import forms
from . import models

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = models.ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.TextInput(attrs={
                'placeholder': 'Type your message...',
                'class': 'w-full bg-gray-700 text-white rounded-lg px-3 py-2 outline-none placeholder-gray-400',
                "maxlength": 150,
                "autofocus": True
            })
        }   