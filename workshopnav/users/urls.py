from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import CustomUserView,  LoginView, LogoutView, ChangePasswordView, PasswordResetConfirmView, PasswordResetRequestView

urlpatterns = [
    path('signup/', CustomUserView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('users/', CustomUserView.as_view(), name='user-list-create'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]