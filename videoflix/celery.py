import os
from celery import Celery

# Django Settings Modul setzen
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'videoflix.settings')

app = Celery('videoflix')

# Celery mit Django Settings konfigurieren
app.config_from_object('django.conf:settings', namespace='CELERY')

# Tasks aus allen registrierten Django Apps laden
app.autodiscover_tasks()