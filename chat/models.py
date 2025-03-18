from django.db import models
from django.contrib.auth.models import User
import datetime


# Create your models here.
class ChatRoomModel(models.Model):
    name = models.CharField(max_length=255)
    participants = models.ManyToManyField(User, related_name='chat_rooms')

class MessageModel(models.Model):
    room = models.ForeignKey(ChatRoomModel, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_sent')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} in {self.room.name}: {self.content}"

class ConversationHistory(models.Model):
    user_id = models.CharField(max_length=100)
    messages = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Historial de conversación"
        verbose_name_plural = "Historiales de conversación"
    
    def __str__(self):
        return f"Historial de conversación para usuario {self.user_id}"
    
    def add_message(self, role, content):
        """Añade un mensaje al historial."""
        self.messages.append({
            'role': role,
            'content': content,
            'timestamp': datetime.datetime.now().isoformat()
        })
        self.save()
    
    def clear_history(self):
        """Limpia el historial de mensajes."""
        self.messages = []
        self.save()