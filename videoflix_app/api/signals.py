from videoflix_app.models import Movie
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import os
import shutil
from .tasks import process_video

@receiver(post_save, sender=Movie)
def movie_post_save(sender, instance, created, **kwargs):
    if created and instance.video_file:
        process_video.delay(instance.id)
        
@receiver(post_delete, sender=Movie)
def delete_related_files(sender, instance, **kwargs):
    if instance.video_file and os.path.isfile(instance.video_file.path):
        os.remove(instance.video_file.path)

    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)

    base_dir = os.path.dirname(os.path.dirname(instance.video_file.path))
    movie_dir = os.path.join(base_dir, str(instance.id))
    if os.path.exists(movie_dir) and os.path.isdir(movie_dir):
        shutil.rmtree(movie_dir)
        
    delete_related_video_files(instance)

def delete_related_video_files(instance):
    if not instance.video_file:
        return
    
    filename = os.path.basename(instance.video_file.name)
    name_without_ext = os.path.splitext(filename)[0]
    base_name = name_without_ext.split('_')[0] 
    directory = os.path.dirname(instance.video_file.path)

    for file in os.listdir(directory):
        if file.startswith(base_name) or file.startswith(f"optimized-{base_name}"):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                os.remove(file_path)