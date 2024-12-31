from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('farmer', 'Farmer'),
        ('supplier', 'Supplier'),
        ('expert', 'Expert'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    national_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    driving_license = models.CharField(max_length=20, blank=True, null=True, unique=True)
    is_verified = models.BooleanField(default=False)  # Verification status
    profile = models.OneToOneField('UserProfile', on_delete=models.CASCADE, null=True, blank=True, related_name="user_profile")

    # def save(self, *args, **kwargs):
    #     # Ensure either National ID or Driving License is provided
    #     if not self.national_id and not self.driving_license:
    #         raise ValueError("Either National ID or Driving License must be provided")
    #     super().save(*args, **kwargs)

    # Avoid conflicts with the default `auth.User` model
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",  # Add a unique related_name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_set",  # Add a unique related_name
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )





class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile_details')
    location = models.CharField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)



class FrontendApp(models.Model):
    name = models.CharField(max_length=255, unique=True)
    unique_key = models.CharField(max_length=255, unique=True)  # Unique key for the frontend
    created_at = models.DateTimeField(auto_now_add=True)