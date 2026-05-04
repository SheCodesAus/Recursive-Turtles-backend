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

# Poll model linked to an event, with a question, creation timestamp, and active status
class Poll(models.Model):
    event = models.ForeignKey(Event, related_name='polls', on_delete=models.CASCADE)
    # poll_code = models.CharField(max_length=10, unique=True, default=generate_code)
    question = models.CharField(max_length=255)
    # options= models.ArrayField(models.CharField(max_length=255), blank=True, default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Poll: {self.question} for Event: {self.event.title}"
    
# response model linked to a poll, with a response text and creation timestamp
class PollResponse(models.Model):
    poll = models.ForeignKey(Poll, related_name='responses', on_delete=models.CASCADE)
    option = models.ForeignKey('PollOption', related_name='responses', on_delete=models.CASCADE, null=True, blank=True)
    #response_text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response: {self.option.option_text} for Poll: {self.poll.question}"

# options model linked to a poll, with an option text and creation timestamp
class PollOption(models.Model):
    poll = models.ForeignKey(Poll, related_name='options', on_delete=models.CASCADE)
    option_text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Option: {self.option_text} for Poll: {self.poll.question}"
