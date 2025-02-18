from django.db import models
from datetime import date

class Movie(models.Model):
    created_at = models.DateField(default=date.today, editable=False)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    video_file = models.FileField(upload_to='videos', blank=True, null=True)
    
    def __str__(self):
        return self.title
    
