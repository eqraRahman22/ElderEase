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

# ~ The bellow portion is added by SMH
class CaregivingLog(models.Model):
    """
    Logs caregiving activities performed for an elderly person.
    Supports Feature 1: Monitoring caregiving services & history.
    """
    caregiver = models.ForeignKey(
        CaregiverProfile,                     # Link to caregiver profile
        on_delete=models.CASCADE              # If caregiver is deleted, logs are also deleted
    )
    elderly = models.ForeignKey(
        ElderlyProfile,                       # Link to elderly person
        on_delete=models.CASCADE              # If elderly is deleted, related logs are deleted
    )
    task = models.CharField(
        max_length=255                        # Short description of the task performed
    )
    notes = models.TextField(
        blank=True,                           # Optional extra details about the task
        null=True
    )
    date = models.DateTimeField(
        auto_now_add=True                     # Automatically store timestamp when log is created
    )

    def __str__(self):
        # Shows task name, elderly name, and date in a human-readable format
        return f"{self.task} for {self.elderly.name} on {self.date.strftime('%Y-%m-%d')}"


class CaregiverRequest(models.Model):
    """
    Stores a request from a family member to a caregiver for a specific elderly person.
    Supports Feature 2: Search & request caregiver.
    """
    STATUS_CHOICES = [
        ("pending", "Pending"),               # Request sent but no response yet
        ("accepted", "Accepted"),             # Caregiver accepted the request
        ("declined", "Declined"),             # Caregiver declined the request
    ]

    family_member = models.ForeignKey(
        settings.AUTH_USER_MODEL,             # Link to the CustomUser who is the family member
        on_delete=models.CASCADE,             # If family member account is deleted, requests are deleted
        related_name="caregiver_requests"     # Allows reverse query: family_member.caregiver_requests.all()
    )
    caregiver = models.ForeignKey(
        CaregiverProfile,                     # Caregiver being requested
        on_delete=models.CASCADE
    )
    elderly = models.ForeignKey(
        ElderlyProfile,                       # Elderly person for whom the caregiver is requested
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,                        # Current status of the request
        choices=STATUS_CHOICES,               # Restrict to predefined statuses
        default="pending"                     # Default status when created
    )
    request_date = models.DateTimeField(
        auto_now_add=True                     # Automatically stores when the request was made
    )

    def __str__(self):
        # Shows which family member requested which caregiver & current status
        return f"Request by {self.family_member.username} for {self.caregiver.name} ({self.status})"

