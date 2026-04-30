#from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import get_object_or_404

from .models import Event
from .serializers import EventSerializer

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


