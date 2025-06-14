from openai import OpenAI
from django.db.models import F
from django.db import transaction
from pgvector.django import CosineDistance

from chatbot.models import Message

openai_client = OpenAI()


def embed_message(content: str) -> list[float]:
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=[content],
    )
    return response.data[0].embedding


class MemoryManager:
    @staticmethod
    @transaction.atomic
    def add_message(
        sender: str,
        content: str,
        session_id: int,
        unique_message_id: str = None,
    ):
        embedding = embed_message(content)

        Message.objects.create(
            sender=sender,
            content=content,
            embedding=embedding,
            session_id=session_id,
            **({"unique_message_id": unique_message_id} if unique_message_id else {})
        )

    @staticmethod
    def get_similar_messages(session_id: int, content: str, limit=None, threshold=None):
        embedding = embed_message(content)

        queryset = Message.objects.filter(session_id=session_id)
        similarity = 1 - CosineDistance(F("embedding"), embedding)
        queryset = queryset.annotate(similarity=similarity)

        if threshold is not None:
            queryset = queryset.filter(similarity__gte=threshold)

        queryset = queryset.order_by(CosineDistance(F("embedding"), embedding))

        if limit is not None:
            queryset = queryset[:limit]

        messages = list(queryset)

        return messages
