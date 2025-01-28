from django.contrib import admin
from django.urls import path, include
from .views import MovieListView

urlpatterns = [
    path('movies/', MovieListView.as_view())
]
