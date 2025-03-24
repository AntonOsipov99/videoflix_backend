import uuid
import pytest
from user_auth_app.api.serializers import (
    LoginSerializer, RegistrationSerializer, 
    ForgotPasswordSerializer, ResetPasswordSerializer
)

@pytest.mark.django_db
def test_registration_serializer_valid_data():
    data = {
        'email': 'new@example.com',
        'password': 'securepass',
        'repeated_password': 'securepass'
    }
    serializer = RegistrationSerializer(data=data)
    assert serializer.is_valid() is True

@pytest.mark.django_db
def test_registration_serializer_passwords_mismatch():
    data = {
        'email': 'new@example.com',
        'password': 'securepass',
        'repeated_password': 'differentpass'
    }
    serializer = RegistrationSerializer(data=data)
    assert serializer.is_valid() is False
    assert 'error' in serializer.errors

@pytest.mark.django_db
def test_login_serializer(test_user):
    data = {
        'email': test_user.email,
        'password': 'password123'
    }
    serializer = LoginSerializer(data=data)
    assert serializer.is_valid() is True
    assert 'token' in serializer.validated_data
    
@pytest.mark.django_db
def test_forgot_password_serializer_valid_email(test_user):
    data = {'email': test_user.email}
    serializer = ForgotPasswordSerializer(data=data)
    
    assert serializer.is_valid() is True
    assert serializer.validated_data['email'] == test_user.email

@pytest.mark.django_db
def test_forgot_password_serializer_invalid_email():
    data = {'email': 'nonexistent@example.com'}
    serializer = ForgotPasswordSerializer(data=data)
    
    assert serializer.is_valid() is False
    assert 'email' in serializer.errors

@pytest.mark.django_db
def test_reset_password_serializer_valid_data():
    data = {
        'token': uuid.uuid4(),
        'password': 'newpassword123',
        'confirm_password': 'newpassword123'
    }
    serializer = ResetPasswordSerializer(data=data)
    
    assert serializer.is_valid() is True

@pytest.mark.django_db
def test_reset_password_serializer_mismatched_passwords():
    data = {
        'token': uuid.uuid4(),
        'password': 'newpassword123',
        'confirm_password': 'differentpassword'
    }
    serializer = ResetPasswordSerializer(data=data)
    
    assert serializer.is_valid() is False
    assert 'non_field_errors' in serializer.errors