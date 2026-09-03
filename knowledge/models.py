from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Location(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    location_type = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name}, {self.city}"


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Knowledge(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    last_confirmed = models.DateTimeField(null=True, blank=True)

    confirmations = models.PositiveIntegerField(default=0)

    disagreements = models.PositiveIntegerField(default=0)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    def __str__(self):
        return self.title


class Vote(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    knowledge = models.ForeignKey(
        Knowledge,
        on_delete=models.CASCADE
    )

    vote_type = models.CharField(
        max_length=20,
        choices=[
            ('agree', 'Agree'),
            ('disagree', 'Disagree'),
        ]
    )

    class Meta:
        unique_together = ('user', 'knowledge')

    def __str__(self):
        return f"{self.user.username} - {self.knowledge.title}"


class Report(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    knowledge = models.ForeignKey(
        Knowledge,
        on_delete=models.CASCADE
    )

    reason = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report - {self.knowledge.title}"