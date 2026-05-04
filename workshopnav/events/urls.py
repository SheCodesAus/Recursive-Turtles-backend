from django.urls import path
from . import views

urlpatterns = [
    path('events/', views.EventListCreateView.as_view()),
    path('events/<str:code>/', views.EventByCodeView.as_view()),
    path('events/<int:event_id>/polls/', views.PollListCreateView.as_view()),
    path('polls/<int:poll_id>/responses/', views.PollResponseCreateView.as_view()),
    path('polls/<int:poll_id>/results/', views.PollResultsView.as_view()),
]