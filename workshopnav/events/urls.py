from django.urls import path
from . import views   # 👈 THIS LINE IS MISSING

urlpatterns = [
    path("questions/", views.questions_list),
]