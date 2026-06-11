from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Comparison(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comparisons')
    name = models.CharField(max_length=100, default='Мое сравнение')
    products = models.ManyToManyField(Product, related_name='comparisons')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"