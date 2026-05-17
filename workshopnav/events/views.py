from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import get_object_or_404
from django.db.models import Count

from .models import Event, Poll, PollOption, Question, Feedback, EmailCapture
from .serializers import (
    EventSerializer,
    PollSerializer,
    PollResponseSerializer,
    QuestionSerializer,
    FeedbackSerializer,
    EmailCaptureSerializer,
)


class EventOwnerMixin:
    def is_event_owner(self, event, user):
        return event.owner == user


# EVENTS
class EventListCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Event.objects.all()

    def get(self, request):
        events = self.get_queryset()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EventSerializer(data=request.data)

        if serializer.is_valid():

            if request.user.is_authenticated:
                serializer.save(owner=request.user)
            else:
                serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ATTENDEE EVENT VIEW
class AttendeeEventByCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, code):
        event = get_object_or_404(Event, event_code__iexact=code)

        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)


# FACILITATOR EVENT VIEW
class EventByCodeView(EventOwnerMixin, APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, code):
        event = get_object_or_404(Event, event_code__iexact=code)

        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, code):

        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        event = get_object_or_404(Event, event_code__iexact=code)

        if not self.is_event_owner(event, request.user):
            return Response(
                {"error": "You do not have permission to edit this event."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = EventSerializer(event, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, code):

        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        event = get_object_or_404(Event, event_code__iexact=code)

        if not self.is_event_owner(event, request.user):
            return Response(
                {"error": "You do not have permission to delete this event."},
                status=status.HTTP_403_FORBIDDEN,
            )

        event.delete()

        return Response(
            {"message": "Event deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


# POLLS
class PollListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, event_id):

        event = get_object_or_404(Event, id=event_id)

        polls = event.polls.all()
        serializer = PollSerializer(polls, many=True)

        return Response(serializer.data)

    def post(self, request, event_id):

        event = get_object_or_404(Event, id=event_id)

        if event.owner != request.user:
            return Response(
                {"error": "Only the event owner can create polls."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PollSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(event=event)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PollDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, poll_id):

        poll = get_object_or_404(Poll, id=poll_id)

        serializer = PollSerializer(poll)

        return Response(serializer.data)

    def put(self, request, poll_id):

        poll = get_object_or_404(Poll, id=poll_id)

        if poll.event.owner != request.user:
            return Response(
                {"error": "Only the event owner can update this poll."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PollSerializer(poll, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, poll_id):

        poll = get_object_or_404(Poll, id=poll_id)

        if poll.event.owner != request.user:
            return Response(
                {"error": "Only the event owner can delete this poll."},
                status=status.HTTP_403_FORBIDDEN,
            )

        poll.delete()

        return Response(
            {"message": "Poll deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


# POLL RESPONSES
class PollResponseCreateView(APIView):

    def get(self, request, poll_id):

        poll = get_object_or_404(Poll, id=poll_id)

        responses = poll.responses.all()

        serializer = PollResponseSerializer(responses, many=True)

        return Response(serializer.data)

    def post(self, request, poll_id):

        poll = get_object_or_404(Poll, id=poll_id)

        if not poll.is_active:
            return Response(
                {"error": "Poll is not active."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PollResponseSerializer(
            data=request.data,
            context={"poll": poll},
        )

        if serializer.is_valid():
            serializer.save(poll=poll)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# POLL RESULTS
class PollResultsView(APIView):

    def get(self, request, poll_id):

        options = PollOption.objects.filter(poll_id=poll_id).annotate(
            count=Count("responses")
        )

        total = sum(option.count for option in options)

        options_data = [
            {
                "id": option.id,
                "option_text": option.option_text,
                "count": option.count,
                "percentage": (option.count / total * 100) if total > 0 else 0,
            }
            for option in options
        ]

        return Response(options_data)


# QUESTIONS
class QuestionListCreateView(APIView):

    def get(self, request, event_id):

        event = get_object_or_404(Event, id=event_id)

        questions = event.questions.all()

        serializer = QuestionSerializer(questions, many=True)

        return Response(serializer.data)

    def post(self, request, event_id):

        event = get_object_or_404(Event, id=event_id)

        serializer = QuestionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(event=event)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestionUpvoteView(APIView):

    def get(self, request, question_id):

        question = get_object_or_404(Question, id=question_id)

        serializer = QuestionSerializer(question)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, question_id):

        question = get_object_or_404(Question, id=question_id)

        question.upvotes += 1
        question.save()

        serializer = QuestionSerializer(question)

        return Response(
            serializer.data | {"message": "Upvoted successfully"},
            status=status.HTTP_200_OK,
        )


# FEEDBACK
class FeedbackCreateView(APIView):

    def get(self, request, event_id):

        event = get_object_or_404(Event, id=event_id)

        feedback = event.feedback.all()

        serializer = FeedbackSerializer(feedback, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, event_id):

        event = get_object_or_404(Event, id=event_id)

        serializer = FeedbackSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(event=event)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OpenFeedbackView(APIView):

    def post(self, request, event_id):

        event = get_object_or_404(Event, id=event_id)

        event.feedback_open = True
        event.save()

        return Response(
            {
                "message": "Feedback opened successfully.",
                "feedback_open": event.feedback_open,
            },
            status=status.HTTP_200_OK,
        )


# EMAIL CAPTURE
class EmailCaptureCreateView(APIView):

    def get(self, request, event_id):

        event = get_object_or_404(Event, id=event_id)

        emails = event.emails.all()

        serializer = EmailCaptureSerializer(emails, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, event_id):

        event = get_object_or_404(Event, id=event_id)

        email = request.data.get("email")

        if EmailCapture.objects.filter(event=event, email=email).exists():
            return Response(
                {"error": "This email has already been submitted for this event."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = EmailCaptureSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(event=event)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)