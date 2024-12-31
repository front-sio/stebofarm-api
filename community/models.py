from django.db import models
from users.models import User

class Community(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

class Group(models.Model):
    name = models.CharField(max_length=255)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    members = models.ManyToManyField(User)
