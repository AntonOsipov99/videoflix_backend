import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from unittest.mock import patch
from user_auth_app.models import PasswordResetToken

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_registration_view(api_client):
    """Test der Registrierungs-API"""
    with patch('user_auth_app.api.views.send_activation_email_task') as mock_email:
        url = reverse('registration')
        data = {
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'repeated_password': 'securepass123'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == 200
        assert 'message' in response.data
        mock_email.assert_called_once()

@pytest.mark.django_db
def test_login_view_success(api_client, test_user):
    """Test des erfolgreichen Logins"""
    url = reverse('login')
    data = {
        'email': test_user.email,
        'password': 'password123'
    }
    response = api_client.post(url, data, format='json')
    
    assert response.status_code == 200
    assert 'token' in response.data

@pytest.mark.django_db
def test_password_reset_flow(api_client, test_user):
    with patch('user_auth_app.api.views.send_password_reset_email') as mock_email:
        forgot_url = reverse('forgot-password')
        response = api_client.post(
            forgot_url, 
            {'email': test_user.email}, 
            format='json'
        )
        
        assert response.status_code == 200
        mock_email.assert_called_once()
        
    token = PasswordResetToken.objects.get(user=test_user)
    reset_url = reverse('reset-password')
    response = api_client.post(
        reset_url,
        {
            'token': token.token,
            'password': 'newpassword123',
            'confirm_password': 'newpassword123'
        },
        format='json'
    )
    
    assert response.status_code == 200