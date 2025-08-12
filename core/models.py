# core/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('caregiver', 'Caregiver'),
        ('family', 'Family Member'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
class CaregiverProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    dob = models.DateField()
    gender = models.CharField(max_length=20)
    emergency_contact = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class ElderlyProfile(models.Model):
    family_member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    dob = models.DateField()
    gender = models.CharField(max_length=20)
    med_condition = models.TextField()
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Schedule(models.Model):
    elderly = models.ForeignKey(ElderlyProfile, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=255)
    task_list = models.TextField(help_text="Comma-separated tasks")
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.elderly.name} - {self.date}"

# The bellow portion is added by SMH
class CaregivingLog(models.Model):
    """
    Logs caregiving activities performed for an elderly person.
    Linked to a caregiver and an elderly profile.
    """
    caregiver = models.ForeignKey(CaregiverProfile, on_delete=models.CASCADE)
    elderly = models.ForeignKey(ElderlyProfile, on_delete=models.CASCADE)
    task = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task} for {self.elderly.name} on {self.date.strftime('%Y-%m-%d')}"


class CaregiverRequest(models.Model):
    """
    Stores a request from a family member to a caregiver for a specific elderly person.
    Tracks request status and request date.
    """
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
    ]

    family_member = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="caregiver_requests"
    )
    caregiver = models.ForeignKey(CaregiverProfile, on_delete=models.CASCADE)
    elderly = models.ForeignKey(ElderlyProfile, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    request_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.family_member.username} for {self.caregiver.name} ({self.status})"
