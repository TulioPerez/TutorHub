from datetime import date
from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from timezone_field import TimeZoneField
import os
import json
from django.conf import settings


# DOUBLE CHECK REQUIRED FIELDS FOR REGISTRATION
#   DIVIDE BY REGISTRATION REQUIRED AND UPDATED PROFILE 

class UserRoles(models.TextChoices):
    STUDENT = 'STUDENT', 'Student'
    TUTOR = 'TUTOR', 'Tutor'
    PARENT = 'PARENT', 'Parent'


class Address(models.Model):
    street_address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state_region = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = CountryField(blank=True, null=True)

    def __str__(self):
        return f"{self.city}, {self.state_region}, {self.country}"


# django default fields: username, password, first_name, last_name, email, is_staff, is_active, is_superuser, date_joined, last_login
class User(AbstractUser):
    nickname = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=10, choices=UserRoles.choices, default=UserRoles.STUDENT)
    phone_number = PhoneNumberField(blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to="profile_images/", blank=True, null=True)
    show_address = models.BooleanField(default=False)
    show_phone_number = models.BooleanField(default=False)

    # localization
    preferred_language = models.CharField(max_length=10, blank=True, null=True, default='en')
    time_zone = TimeZoneField(default='UTC', blank=True)

    # Address
    address = models.OneToOneField(Address, on_delete=models.SET_NULL, blank=True, null=True)

    # Relationships
    follows = models.ManyToManyField(
        "self",
        through="FollowRelation",
        through_fields=('follower', 'followee'),
        symmetrical=False,
        related_name="followed_by"
    )

    # Tutors-specific registration fields
    is_tutor = models.BooleanField(default=False)
    availability = models.JSONField(default=dict, blank=True, null=True)
    subject_levels = models.ManyToManyField('SubjectLevel', blank=True, related_name="users")

    # USERNAME_FIELD = "email"
    # REQUIRED_FIELDS = ["username"]

    # For index page name display
    def get_display_name(self):
        return self.nickname or self.first_name

    @property # calculated on the fly but accessible as if it's an attribute
    def age(self):
        if self.birthdate:
            today = date.today()
            return today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
        return None

    def __str__(self):
        return self.email


# Relationships
class FollowRelation(models.Model):
    follower = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
    followee = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE)
    is_blocked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('follower', 'followee')

    def __str__(self):
        return f"{self.follower} follows {self.followee}"


# Rating System
class Review(models.Model):
    tutor = models.ForeignKey(User, related_name="reviews", on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()  # Scale of 1–5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


# Levels
class Level(models.Model):
    name = models.CharField(max_length=50, unique=True)
    order = models.IntegerField(unique=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    @classmethod
    def load_levels(cls):
        file_path = os.path.join(settings.BASE_DIR, 'tutorhub', 'static', 'tutorhub', 'levels.json')
        with open(file_path, 'r') as file:
            levels_data = json.load(file)
        
        for level in levels_data:
            cls.objects.get_or_create(
                name=level['name'],
                defaults={'order': level['order']}
            )


class SubjectLevel(models.Model):
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tutor_subject_levels")
    subject = models.CharField(max_length=100)
    levels = models.ManyToManyField(Level)

    class Meta:
        unique_together = ('tutor', 'subject')

    def __str__(self):
        levels_str = ", ".join(level.name for level in self.levels.all())
        return f"{self.subject} ({levels_str})"


class Credential(models.Model):
    CREDENTIAL_CHOICES = [
        ("Certificate", "Certificate"),
        ("Diploma", "Diploma"),
        ("Resume", "Resume"),
        ("Coursework", "Coursework (No Certificate)"),
        ("Other", "Other"),
    ]
        
    credential_type = models.CharField(max_length=50, choices=CREDENTIAL_CHOICES, default="Certificate",)
    file = models.FileField(upload_to="credentials/", blank=True, null=True)
    description = models.TextField(blank=True, null=True, help_text="Provide details about this credential, especially for coursework with no file.")

    user = models.ForeignKey(User, related_name="credentials", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.credential_type} for {self.user}"
    

# for group messages
class Thread(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)  # Optional name for group chats
    is_group = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    participants = models.ManyToManyField(User, related_name="threads")

    def __str__(self):
        return f"Thread: {self.name or 'Unnamed'}"


class ThreadParticipant(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('MEMBER', 'Member'),
    ]

    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='MEMBER')
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} in {self.thread.name or 'Thread'} ({self.role})"


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)
    edited_timestamp = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)  # Track if the message is deleted

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"
