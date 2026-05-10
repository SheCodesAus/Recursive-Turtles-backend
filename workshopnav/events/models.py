import uuid

from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

# auto-generate a unique 6-character code for each event
def generate_code():
    return uuid.uuid4().hex[:6].upper()

# Event model with title, unique event code, and creation timestamp
class Event(models.Model):
    title = models.CharField(max_length=255)
    event_code = models.CharField(max_length=10, unique=True, default=generate_code)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owned_events', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} ({self.event_code})"

# Poll model linked to an event, with a question, creation timestamp, and active status
class Poll(models.Model):
    event = models.ForeignKey(Event, related_name='polls', on_delete=models.CASCADE)
    question = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Poll: {self.question} for Event: {self.event.title}"
    
# response model linked to a poll, with a response text and creation timestamp
class PollResponse(models.Model):
    poll = models.ForeignKey(Poll, related_name='responses', on_delete=models.CASCADE)
    option = models.ForeignKey('PollOption', related_name='responses', on_delete=models.CASCADE)
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

# Question model linked to an event, with question text, visibility, upvotes, and creation timestamp
class Question(models.Model):
    event = models.ForeignKey(Event, related_name='questions', on_delete=models.CASCADE)
    question_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    anonymous = models.BooleanField(default=False)
    visible = models.BooleanField(default=True)
    upvotes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Question: {self.question_text} for Event: {self.event.title}"


# Feedback model
class Feedback(models.Model):
    #Links feedback to specific event
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="feedback")
    #rating score
    rating = models.IntegerField()
    #optional comment field
    comment = models.TextField(blank=True)
    #auto stores when the feedback is created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.event.title}"


#Email capture model
class EmailCapture(models.Model):
    #Links email to an event
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="emails")
    #Stores user's email
    email = models.EmailField()
    #When email was submitted
    created_at = models.DateTimeField(auto_now_add=True)

    # Prevent the same email being submitted twice for the same event
    class Meta:
        unique_together = ("event", "email")

    def __str__(self):
        return self.email