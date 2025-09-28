from django.db import models
from django.conf import settings
from django.utils import timezone

class ChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_user_message = models.BooleanField(default=True)
    response = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Chat Messages'
