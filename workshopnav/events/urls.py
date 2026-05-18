from django.urls import path
from . import views

urlpatterns = [
    path("events/", views.EventListCreateView.as_view()),
    path("events/<int:pk>/", views.EventDetailView.as_view()),

    # attendee join flow
    path("events/join/<str:code>/", views.AttendeeEventByCodeView.as_view()),

    # facilitator / event code routes
    path("events/<str:code>/", views.EventByCodeView.as_view()),

    # polls
    path("events/<int:event_id>/polls/", views.PollListCreateView.as_view()),
    path("polls/<int:poll_id>/", views.PollDetailView.as_view()),
    path("polls/<int:poll_id>/responses/", views.PollResponseCreateView.as_view()),
    path("polls/<int:poll_id>/results/", views.PollResultsView.as_view()),

    # questions
    path("events/<int:event_id>/questions/", views.QuestionListCreateView.as_view()),
    path("questions/<int:question_id>/upvote/", views.QuestionUpvoteView.as_view()),

    # feedback
    path("events/<int:event_id>/feedback/", views.FeedbackCreateView.as_view()),
    path("events/<int:event_id>/open-feedback/", views.OpenFeedbackView.as_view()),

    # emails
    path("events/<int:event_id>/emails/", views.EmailCaptureCreateView.as_view()),
]
    