from django.db import models

# Create your models here.

class Session(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    TYPE_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
    ]

    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, related_name='messages'
    )
    content = models.TextField()
    message_type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}"


class SystemPrompt(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField(max_length=4000)

    def __str__(self):
        return self.name
