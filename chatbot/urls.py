from django.urls import path
from .views import ChatbotQueryView

app_name = 'chatbot'

urlpatterns = [
    path('query/', ChatbotQueryView.as_view(), name='chatbot-query'),
]
