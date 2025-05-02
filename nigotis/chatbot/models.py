from django.db import models

from pgvector.django import VectorField


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Client(BaseModel):
    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("SALES", "Sales"),
        ("FINANCE", "Finance"),
        ("HR", "HR"),
    ]
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    login_email = models.EmailField(null=True, blank=True)
    login_password = models.CharField(max_length=255, null=True, blank=True)
    auth_token = models.CharField(max_length=255, null=True, blank=True)
    authenticated_at = models.DateTimeField(null=True, blank=True)


class Session(BaseModel):
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    website = models.BooleanField(default=False)
    client = models.ForeignKey(
        Client,
        null=True,
        blank=True,
        related_name="sessions",
        on_delete=models.SET_NULL,
    )


class Message(BaseModel):
    SENDER_CHOICES = [
        ("USER", "User"),
        ("BOT", "Bot"),
    ]

    unique_message_id = models.TextField()
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    embedding = VectorField(dimensions=1536)
    session = models.ForeignKey(
        Session,
        related_name="messages",
        on_delete=models.CASCADE,
    )
