from videoflix_app.models import Movie
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import os
from .tasks import process_video

@receiver(post_save, sender=Movie)
def movie_post_save(sender, instance, created, **kwargs):
    if created and instance.video_file:
        process_video.delay(instance.id)
        
@receiver(post_delete, sender=Movie)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if os.path.isfile(instance.video_file.path):
        os.remove(instance.video_file.path)