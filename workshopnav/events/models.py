import uuid

from django.db import models

# auto-generate a unique 6-character code for each event
def generate_code():
    return uuid.uuid4().hex[:6].upper()

# Event model with title, unique event code, and creation timestamp
class Event(models.Model):
    title = models.CharField(max_length=255)
    event_code = models.CharField(max_length=10, unique=True, default=generate_code)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.event_code})"
