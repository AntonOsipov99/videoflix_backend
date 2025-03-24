import pytest
from django.contrib.auth.models import User
from user_auth_app.models import Profile, PasswordResetToken
import uuid

@pytest.fixture
def test_user():
    user = User.objects.create_user(
        username='testuser@example.com',
        email='testuser@example.com',
        password='password123'
    )
    return user

@pytest.fixture
def inactive_user():
    user = User.objects.create_user(
        username='inactive@example.com',
        email='inactive@example.com',
        password='password123',
        is_active=False
    )
    return user

@pytest.fixture
def profile(test_user):
    return Profile.objects.get(user=test_user)

@pytest.fixture
def reset_token(test_user):
    return PasswordResetToken.objects.create(user=test_user)