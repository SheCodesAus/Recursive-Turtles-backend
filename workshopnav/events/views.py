#from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import get_object_or_404
from django.db.models import Count

from .models import Event, Poll, PollOption
from .serializers import EventSerializer, PollSerializer, PollResponseSerializer, PollOptionSerializer

class EventListCreateView(APIView):

# Get all events 
    def get(self, request):
        # events = Event.objects.filter(user=request.user)
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

# Create a new event
    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get event by code
class EventByCodeView(APIView):
    def get(self, request, code):
        try:
            event = Event.objects.get(event_code__iexact=code)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found with the provided code."},
                status=status.HTTP_404_NOT_FOUND)
        
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)

#polls for an event
#POST /events/{event_id}/polls/ - create a new poll for the event
#GET /events/{event_id}/polls/ - get all polls for the event
class PollListCreateView(APIView):

    def get(self, request, event_id):
        try:
                event = get_object_or_404(Event, id=event_id)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found."},
                status=status.HTTP_404_NOT_FOUND)
        
        polls = event.polls.all()
        serializer = PollSerializer(polls, many=True)
        return Response(serializer.data)

    def post(self, request, event_id):
        try:
            event = get_object_or_404(Event, id=event_id)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found."},
                status=status.HTTP_404_NOT_FOUND)
        
        serializer = PollSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(event=event)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#POST /polls/{poll_id}/responses/ - submit a response to a poll
class PollResponseCreateView(APIView):

    def get(self, request, poll_id):
        try:
            poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            return Response(
                {"error": "Poll not found."},
                status=status.HTTP_404_NOT_FOUND)
        
        self.responses = poll.responses.all()
        serializer = PollResponseSerializer(self.responses, many=True)
        return Response(serializer.data)


    def post(self, request, poll_id):
        try:
            poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            return Response(
                {"error": "Poll not found."},
                status=status.HTTP_404_NOT_FOUND)
        
        if not poll.is_active:
            return Response(
                {"error": "Poll is not active."},
                status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PollResponseSerializer(data=request.data, context={'poll': poll})

        if serializer.is_valid():
            serializer.save(poll_id=poll_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#GET /polls/{poll_id}/results/ - get the results of a poll (number of responses for each option)
class PollResultsView(APIView):

    def get(self, request, poll_id):
        try:
            poll = Poll.objects.get(id=poll_id)
        except Poll.DoesNotExist:
            return Response(
                {"error": "Poll not found."},
                status=status.HTTP_404_NOT_FOUND)
        
        # options = poll.options.all()
        # results = {}
        # for option in options:
        #     results[option.option_text] = option.responses.count()
        # return Response(results)

        options = PollOption.objects.filter(poll_id=poll_id).annotate(count=Count('responses'))

        total = sum(option.count for option in options)

        options_data = [
            {
                'id': option.id,
                'option_text': option.option_text,
                'count': option.count,
                'percentage': (option.count / total * 100) if total > 0 else 0
            }
            for option in options
        ]

        return Response(options_data)
