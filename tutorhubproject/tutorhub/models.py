from datetime import date
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    nickname = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    is_tutor = models.BooleanField(default=False)
    
    street_address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)

    profile_image = models.ImageField(upload_to="profile_images/", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)

    # Tutors-only registration fields
    availability = models.JSONField(default=dict, blank=True, null=True)
    subject_grades = models.ManyToManyField('SubjectGrade', blank=True, related_name="users")
    followed_by = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="followed_tutors")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    @property
    def age(self):
        if self.birthdate:
            today = date.today()
            return today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
        return None

    def __str__(self):
        return self.email


class SubjectGrade(models.Model):
    tutor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tutor_subject_grades")
    subject = models.CharField(max_length=100)
    grade_levels = models.JSONField(default=list)

    class Meta:
        unique_together = ('tutor', 'subject')

    def __str__(self):
        grades = ", ".join(self.grade_levels)
        return f"{self.subject} ({grades})"


class Credential(models.Model):
    file = models.FileField(upload_to="credentials/")
    user = models.ForeignKey(User, related_name="credentials", on_delete=models.CASCADE)

    def __str__(self):
        return f"Credential for {self.user}"
    

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
