import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.core.cache import cache

@pytest.fixture
def authenticated_client(api_client, test_user):
    from rest_framework.authtoken.models import Token
    token, _ = Token.objects.get_or_create(user=test_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    return api_client

@pytest.mark.django_db
def test_movie_list_view(authenticated_client, sample_movie):
    url = reverse('movie-list')
    response = authenticated_client.get(url)
    
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['title'] == sample_movie.title

@pytest.mark.django_db
def test_movie_detail_view(authenticated_client, sample_movie):
    url = reverse('movie-detail', args=[sample_movie.id])
    response = authenticated_client.get(url)
    
    assert response.status_code == 200
    assert response.data['title'] == sample_movie.title
    assert response.data['description'] == sample_movie.description

@pytest.mark.django_db
def test_movie_create(authenticated_client, sample_video):
    url = reverse('movie-list')
    data = {
        'title': 'New Movie',
        'description': 'New Description',
        'genre': 'Drama',
        'video_file': sample_video
    }
    response = authenticated_client.post(url, data, format='multipart')
    
    assert response.status_code == 201
    assert response.data['title'] == 'New Movie'