from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=255)
    event_code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.event_code})"
