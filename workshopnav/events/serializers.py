from rest_framework import serializers
from .models import Event, Poll, PollResponse, PollOption

# Serializer for the Event model
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'event_code', 'created_at']
        reaad_only_fields = ['id', 'created_at']

# Serializer for the PollOption model
class PollOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollOption
        fields = ['id', 'option_text', 'created_at']
        read_only_fields = ['id', 'created_at']

# Serializer for the Poll model
class PollSerializer(serializers.ModelSerializer):
    # options = PollOptionSerializer(many=True, read_only=True)
    options = serializers.ListField(
        child=serializers.CharField(max_length=255),
        write_only=True
    )

    poll_options = PollOptionSerializer(many=True, read_only=True, source='options')
    class Meta:
        model = Poll
        fields = ['id', 'question', 'created_at', 'is_active', 'options' , 'poll_options' ] #'poll_code',
        read_only_fields = ['id', 'created_at'] 
    
    def create(self, validated_data):
        options_data = validated_data.pop('options', [])
        poll = Poll.objects.create(**validated_data)
        for option_text in options_data:
            PollOption.objects.create(poll=poll, option_text=option_text)
        return poll

#serializer for the PollResponse model
class PollResponseSerializer(serializers.ModelSerializer):
    option= serializers.PrimaryKeyRelatedField(queryset=PollOption.objects.all())
    class Meta:
        model = PollResponse
        fields = ['id', 'poll', 'option',  'created_at'] # 'response_text',
        read_only_fields = ['id', 'created_at']