from rest_framework import serializers
from .models import Event

# Serializer for the Event model
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'event_code', 'created_at']
        reaad_only_fields = ['id', 'created_at']