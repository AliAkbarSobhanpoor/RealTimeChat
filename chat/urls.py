from django.urls import path

import chat
from .views import *

urlpatterns = [
    path("", chat_view, name="home"),
]