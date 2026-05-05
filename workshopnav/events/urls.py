from django.urls import path
from .views import FeedbackListCreateView

urlpatterns = [
    path('feedback/', FeedbackListCreateView.as_view(), name='feedback'),
]