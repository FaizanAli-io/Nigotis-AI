from django.db import models


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class ChatSession(BaseModel):
    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("SALES", "Sales"),
        ("FINANCE", "Finance"),
        ("HR", "HR"),
    ]

    name = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    login_email = models.EmailField()
    login_password = models.CharField(max_length=255)
    auth_token = models.CharField(max_length=255)
    authenticated_at = models.DateTimeField(auto_now_add=True)


class ChatMessage(BaseModel):
    SENDER_CHOICES = [
        ("USER", "User"),
        ("BOT", "Bot"),
    ]

    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    session = models.ForeignKey(
        ChatSession,
        related_name="messages",
        on_delete=models.CASCADE,
    )
