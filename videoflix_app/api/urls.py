from django.contrib import admin
from django.urls import path, include
from .views import MovieListView, MovieListViewDetail

urlpatterns = [
    path('movies/', MovieListView.as_view(), name='movie-list'),
    path('movies/<int:pk>/', MovieListViewDetail.as_view(), name='movie-detail'),
] 
