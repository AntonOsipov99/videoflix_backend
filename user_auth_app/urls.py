from django.urls import include, path

urlpatterns = [
    path('api/auth/', include('user_auth_app.api.urls'))
]