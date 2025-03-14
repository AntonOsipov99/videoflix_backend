
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

        
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data['email']
        password = data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        if user.check_password(password):
            token, created = Token.objects.get_or_create(user=user)
            return {'token': token.key, 'is_active': user.is_active}
        else:
            raise serializers.ValidationError("Incorrect password")

class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError(
                {'error': 'Please check your entries and try again.'}
            )
        return data
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Please check your entries and try again."
            )
        return value
    
    def save(self):
        account = User(
            username=self.validated_data['email'], 
            email=self.validated_data['email'],
            is_active=False
        )
        account.set_password(self.validated_data['password'])
        account.save()
        
        return account
    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('Please check your entries and try again.')
        return value

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(min_length=1, write_only=True)
    confirm_password = serializers.CharField(min_length=1, write_only=True)
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data