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
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
    
@method_decorator(cache_page(CACHE_TTL), name='dispatch')
class MovieListViewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response