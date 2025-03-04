from django.db import models
from datetime import date
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

class Movie(models.Model):
    created_at = models.DateField(default=date.today, editable=False)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    video_file = models.FileField(upload_to='videos', blank=True, null=True)
    genre = models.CharField(max_length=200, blank=True, null=True)
    image = models.FileField(upload_to='images', blank=True, null=True)
    
    def __str__(self):
        return self.title
    
@receiver(post_save, sender=Movie)
@receiver(post_delete, sender=Movie)
def invalidate_movie_cache(sender, instance, **kwargs):
    cache.clear()