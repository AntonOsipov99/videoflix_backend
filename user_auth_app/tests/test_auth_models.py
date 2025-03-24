import pytest
from django.utils import timezone
from datetime import timedelta
from user_auth_app.models import Profile, PasswordResetToken

@pytest.mark.django_db
def test_profile_creation(test_user):
    profile = Profile.objects.get(user=test_user)
    assert profile is not None
    assert profile.activation_key is not None
    assert profile.is_active is False

@pytest.mark.django_db
def test_password_reset_token_validity(reset_token):
    assert reset_token.is_valid() is True
    reset_token.expires_at = timezone.now() - timedelta(hours=1)
    reset_token.save()
    
    assert reset_token.is_valid() is False