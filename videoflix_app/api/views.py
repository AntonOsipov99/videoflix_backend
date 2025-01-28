from rest_framework import generics
from videoflix_app.models import Movie
from .serializers import MovieSerializer

class MovieListView(generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer