from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    SKIN_TYPES = [
        ('dry', 'Сухая'),
        ('oily', 'Жирная'),
        ('combination', 'Комбинированная'),
        ('normal', 'Нормальная'),
        ('sensitive', 'Чувствительная'),
    ]
    
    AGE_RANGES = [
        ('under20', 'До 20'),
        ('20-30', '20-30'),
        ('30-45', '30-45'),
        ('45plus', '45+'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    skin_type = models.CharField(max_length=20, choices=SKIN_TYPES, blank=True, null=True)
    problems = models.CharField(max_length=500, blank=True, default='')
    age_range = models.CharField(max_length=20, choices=AGE_RANGES, blank=True, null=True)
    allergies = models.CharField(max_length=500, blank=True, default='')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)