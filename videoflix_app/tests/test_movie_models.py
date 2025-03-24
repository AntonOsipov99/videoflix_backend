import pytest
from videoflix_app.models import Movie
from django.core.cache import cache

@pytest.mark.django_db
def test_movie_creation(sample_movie):
    assert sample_movie.title == 'Test Movie'
    assert sample_movie.description == 'Test Description'
    assert sample_movie.is_processed is False
    assert sample_movie.genre == 'Drama'

@pytest.mark.django_db
def test_movie_str_method(sample_movie):
    assert str(sample_movie) == 'Test Movie'

@pytest.mark.django_db
def test_cache_invalidation(sample_movie):
    cache.set('test_key', 'test_value')

    sample_movie.title = 'Updated Title'
    sample_movie.save()

    assert cache.get('test_key') is None