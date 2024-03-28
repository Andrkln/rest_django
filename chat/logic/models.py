from django.db import models
import uuid


class Conversation(models.Model):
    chat_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user_input = models.TextField()
    response = models.TextField()