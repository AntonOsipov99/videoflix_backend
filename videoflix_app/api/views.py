from rest_framework import generics
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from videoflix_app.models import Movie
from .serializers import MovieSerializer
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

@method_decorator(cache_page(CACHE_TTL), name='dispatch')
class MovieListView(generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer