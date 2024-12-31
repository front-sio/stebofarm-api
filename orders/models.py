from django.db import models
from users.models import User
from products.models import Offer

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)  # Changed from Product to Offer
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
