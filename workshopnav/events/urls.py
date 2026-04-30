from django.urls import path
from . import views

urlpatterns = [
    path('events/', views.EventListCreateView.as_view()),
    path('events/<str:code>/', views.EventByCodeView.as_view()),
]