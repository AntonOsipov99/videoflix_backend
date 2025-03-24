import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from videoflix_app.models import Movie

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def test_user():
    User = get_user_model()
    user = User.objects.create_user(
        username='testuser@example.com',
        email='testuser@example.com',
        password='password123'
    )
    return user

@pytest.fixture
def authenticated_client(api_client, test_user):
    token, _ = Token.objects.get_or_create(user=test_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return api_client

@pytest.fixture
def sample_video():
    file = tempfile.NamedTemporaryFile(suffix='.mp4')
    file.write(b'dummy video content')
    file.seek(0)
    return SimpleUploadedFile(
        name='test_video.mp4',
        content=file.read(),
        content_type='video/mp4'
    )

@pytest.fixture
def sample_movie(sample_video):
    movie = Movie.objects.create(
        title='Test Movie',
        description='Test Description',
        video_file=sample_video,
        genre='Drama'
    )
    return movie