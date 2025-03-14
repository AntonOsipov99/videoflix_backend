from rest_framework.authtoken.models import Token
from .serializers import RegistrationSerializer, LoginSerializer, ResetPasswordSerializer, ForgotPasswordSerializer
from user_auth_app.models import PasswordResetToken
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from user_auth_app.models import Profile
from videoflix import settings
from django.core.mail import send_mail
from .tasks import send_password_reset_email, send_activation_email_task
from django.contrib.auth import get_user_model

User = get_user_model()
    
class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.validated_data)
    
class RegistrationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            profile = Profile.objects.get(user=user)
            self.send_activation_email(user, profile.activation_key)
            
            return Response({
                "message": "Registration successful. Please check your emails for confirmation."
            })
    
        return Response({
            "message": "Please check your entries and try again."
        }, status=400)

    def send_activation_email(self, user, activation_key):
        try:
            activation_url = f"{settings.FRONTEND_URL}/activate/{activation_key}"
            send_activation_email_task(user.email, activation_url)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to queue activation email for {user.email}: {str(e)}")

class ActivationView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, activation_key):
        try:
            profile = Profile.objects.get(activation_key=activation_key)
            if not profile.is_active:
                user = profile.user
                user.is_active = True
                user.save()
                profile.is_active = True
                profile.save()
                return Response({"message": "Account activated. You can log in now."})
            else:
                return Response({"message": "The account has already been activated."})
        except Profile.DoesNotExist:
            return Response({"message": "Invalid activation link."}, status=400)

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                reset_token = PasswordResetToken.objects.create(user=user)
                reset_url = f"{settings.FRONTEND_URL}/reset-password/{reset_token.token}"
                send_password_reset_email(email, reset_url)
                
                return Response(
                    {"message": "Password reset email sent"}, 
                    status=status.HTTP_200_OK
                )
                
            except User.DoesNotExist:
                return Response(
                    {"message": "Please check your entries and try again."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            token = serializer.validated_data['token']
            password = serializer.validated_data['password']
            
            try:
                reset_token = PasswordResetToken.objects.get(token=token)

                if not reset_token.is_valid():
                    return Response(
                        {"error": "Token expired"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                user = reset_token.user
                user.set_password(password)
                user.save()
        
                reset_token.delete()
                
                return Response(
                    {"message": "Password updated successfully"}, 
                    status=status.HTTP_200_OK
                )
                
            except PasswordResetToken.DoesNotExist:
                return Response(
                    {"error": "Invalid token"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)