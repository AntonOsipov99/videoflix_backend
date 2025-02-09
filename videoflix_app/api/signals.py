from videoflix_app.models import Movie
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import os
from .tasks import convert_480p
import django_rq

@receiver(post_save, sender=Movie)
def movie_post_save(sender, instance, created, **kwargs):
    print('Video wurde gespeichert')
    if created:
        print('New video created')
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(convert_480p, instance.video_file.path)
        
@receiver(post_delete, sender=Movie)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if os.path.isfile(instance.video_file.path):
        os.remove(instance.video_file.path)