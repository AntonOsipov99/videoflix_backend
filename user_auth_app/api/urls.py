from django.urls import path
from .views import RegistrationView, LoginView, ActivationView, ResetPasswordView, ForgotPasswordView

urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('login/', LoginView.as_view(), name='login'),
    path('activate/<str:activation_key>/', ActivationView.as_view(), name='activate'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]