#from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import get_object_or_404
from django.db.models import Count

from .models import Event, Poll, PollOption, Question, Feedback, EmailCapture
from .serializers import EventSerializer, PollSerializer, PollResponseSerializer, PollOptionSerializer, QuestionSerializer, FeedbackSerializer, EmailCaptureSerializer

class EventListCreateView(APIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(owner=self.request.user)
    
    def is_event_owner(self, event, user):
        return event.owner == user

    # Get all events owned by the authenticated user
    def get(self, request):
        events = self.get_queryset()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    # Create a new event
    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Get event by code (public view, but edit/delete restricted to owner)
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
    
    def put(self, request, code):
        permission_classes = [permissions.IsAuthenticated]
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            event = Event.objects.get(event_code__iexact=code)
        except Event.DoesNotExist:
            return Response({"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if event.owner != request.user:
            return Response({"error": "You do not have permission to edit this event."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = EventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, code):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            event = Event.objects.get(event_code__iexact=code)
        except Event.DoesNotExist:
            return Response({"error": "Event not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if event.owner != request.user:
            return Response({"error": "You do not have permission to delete this event."}, status=status.HTTP_403_FORBIDDEN)
        
        event.delete()
        return Response({"message": "Event deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

#polls for an event
#GET /events/{event_id}/polls/ - get all polls for the event (public)
#POST /events/{event_id}/polls/ - create a new poll (event owner only)
class PollListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

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
        
        # Only event owner can create polls
        if event.owner != request.user:
            return Response(
                {"error": "Only the event owner can create polls."},
                status=status.HTTP_403_FORBIDDEN)
        
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

#Ask questions in an event
#POST /questions/{question_id}/
class QuestionListCreateView(APIView):

    def get(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found."},
                status=status.HTTP_404_NOT_FOUND)
        
        questions = event.questions.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

    def post(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found."},
                status=status.HTTP_404_NOT_FOUND)

        serializer = QuestionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(event=event)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    
#POST /questions/{question_id}/upvote/ - upvote a question
class QuestionUpvoteView(APIView):

    def get(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response(
                {"error": "Question not found."},
                status=status.HTTP_404_NOT_FOUND)
        
        serializer = QuestionSerializer(question)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response(
                {"error": "Question not found."},
                status=status.HTTP_404_NOT_FOUND)
        
        question.upvotes += 1
        question.save()
        serializer = QuestionSerializer(question)
        return Response(serializer.data | {"message": "Upvoted successfully"}, status=status.HTTP_200_OK)
    
class QuestionVisibilityView(APIView):

    def post(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response(
                {"error": "Question not found."},
                status=status.HTTP_404_NOT_FOUND)
        
        question.visible = not question.visible
        question.save()
        serializer = QuestionSerializer(question)
        return Response(serializer.data | {"message": f"Question is now {'visible' if question.visible else 'hidden'}"}, status=status.HTTP_200_OK)
#POST /events/:id/feedback/ -> User submits feedback

class FeedbackCreateView(APIView):

#GET feedback summary
    def get(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        feedback = event.feedback.all()
        serializer = FeedbackSerializer(feedback, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#POST /events/:id/feedback/ -> User submits feedback
    def post(self, request, event_id):
        try:
            event = get_object_or_404(Event, id=event_id)
        except Event.DoesNotExist:
            return Response(
                {"error": "Event not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = FeedbackSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(event=event)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailCaptureCreateView(APIView):
#Get collected emails endpoint
    def get(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        emails = event.emails.all()
        serializer = EmailCaptureSerializer(emails, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

#POST /events/:id/emails/ -> User submits email
    def post(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        email = request.data.get("email")

        if EmailCapture.objects.filter(event=event, email=email).exists():
            return Response(
                {"error": "This email has already been submitted for this event."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = EmailCaptureSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(event=event)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)