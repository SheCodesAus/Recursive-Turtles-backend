from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import CustomUserView

urlpatterns = [
    path('signup/', CustomUserView.as_view(), name='signup'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/', CustomUserView.as_view(), name='user-list-create'),
]