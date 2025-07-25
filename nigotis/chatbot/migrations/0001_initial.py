# Generated by Django 5.1.4 on 2025-06-06 11:46

import django.db.models.deletion
import pgvector.django.vector
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Client",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("name", models.CharField(max_length=255)),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("ADMIN", "Admin"),
                            ("SALES", "Sales"),
                            ("FINANCE", "Finance"),
                            ("HR", "HR"),
                        ],
                        max_length=10,
                    ),
                ),
                (
                    "login_email",
                    models.EmailField(blank=True, max_length=254, null=True),
                ),
                (
                    "login_password",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("auth_token", models.CharField(blank=True, max_length=255, null=True)),
                ("authenticated_at", models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Session",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("title", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "phone_number",
                    models.CharField(blank=True, max_length=20, null=True),
                ),
                ("website", models.BooleanField(default=False)),
                (
                    "client",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="sessions",
                        to="chatbot.client",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Message",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("unique_message_id", models.TextField()),
                (
                    "sender",
                    models.CharField(
                        choices=[("USER", "User"), ("BOT", "Bot")], max_length=10
                    ),
                ),
                ("content", models.TextField()),
                ("embedding", pgvector.django.vector.VectorField(dimensions=1536)),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="chatbot.session",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
            },
        ),
    ]
