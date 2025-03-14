from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from videoflix import settings
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    activation_key = models.UUIDField(default=uuid.uuid4, editable=False)
    
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        return timezone.now() <= self.expires_at
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)