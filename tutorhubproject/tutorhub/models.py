from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    profile_image = models.ImageField(upload_to="profile_images/", blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    availability = models.JSONField(default=dict)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class GradeLevel(models.Model):
    level = models.CharField(max_length=50)

    def __str__(self):
        return self.level


class Tutor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="tutor_profile")
    subjects = models.ManyToManyField(Subject)
    grade_levels = models.ManyToManyField(GradeLevel)
    liked_by = models.ManyToManyField(User, related_name="liked_tutors", blank=True)

    def __str__(self):
        return f"{self.user.nickname or self.user.username} - Tutor"


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"
