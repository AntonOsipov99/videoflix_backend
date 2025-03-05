
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
            return {'token': token.key}
        else:
            raise serializers.ValidationError("Incorrect password")

class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only= True)

    class Meta:
        model = User
        fields = ['email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
        
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email address is already registered.")
        return value
        
    def save(self):
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        
        if pw != repeated_pw:
            raise serializers.ValidationError({'error': 'passwords dont match'})
        
        account = User(username=self.validated_data['email'], email=self.validated_data['email'])
        account.set_password(pw)
        account.save()
        return account