from django.db import models
from users.models import User


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    


class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Crop', 'Crop'),
        ('Livestock', 'Livestock'),
        ('Tool', 'Tool'),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    tags = models.CharField(max_length=255, blank=True, null=True)  # Comma-separated tags
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name



class Offer(models.Model):
    OFFER_TYPE_CHOICES = [
        ('Buy', 'Buy'),
        ('Sell', 'Sell'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="offers")
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    min_order = models.PositiveIntegerField()
    max_order = models.PositiveIntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="offers")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)



class CounterOffer(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="counter_offers")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2)
    proposed_quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')])
    created_at = models.DateTimeField(auto_now_add=True)