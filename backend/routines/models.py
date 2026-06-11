from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Routine(models.Model):
    GOAL_CHOICES = [
        ('custom', 'Пользовательская'),
    ]
    
    TIME_CHOICES = [
        ('morning', 'Утренняя'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routines')
    name = models.CharField(max_length=200)
    goal = models.CharField(max_length=50, choices=GOAL_CHOICES, default='custom')
    time_of_day = models.CharField(max_length=20, choices=TIME_CHOICES, default='morning')
    cleansing = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    toner = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    serum = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    cream = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    spf = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    class Meta:
        verbose_name = 'Рутина'
        verbose_name_plural = 'Рутины'