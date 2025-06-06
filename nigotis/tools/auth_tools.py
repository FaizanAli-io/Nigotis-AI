import requests

from langchain_core.tools import tool
from django.utils.timezone import now
from chatbot.models import Session, Client

from utils import functions as F


@tool
def authenticate_session(session_id: int, email: str, password: str) -> str:
    """Authenticate a user session via provided session ID, email, and password."""
    session = Session.objects.get(id=session_id)

    response_data = F.call_login_api(email, password, "admin")

    if not response_data.get("success"):
        return "Authentication failed"

    data = response_data.get("data", {})
    client = Client.objects.filter(login_email=email).first()

    if not client:
        client = Client.objects.create(
            login_email=email,
            login_password=password,
            name=F.extract_name(data),
            role=data["role"].upper(),
            auth_token=data["token"],
            authenticated_at=now(),
        )

    session.client = client
    session.save()

    return "Authentication successful"


@tool
def logout_session(session_id: int) -> str:
    """Logout a user by clearing client from the session."""
    session = Session.objects.get(id=session_id)
    session.client = None
    session.save()
    return "Logout successful"


@tool
def refresh_token(session_id: int) -> str:
    """Refresh the authentication token using saved client credentials."""
    session = Session.objects.get(id=session_id)
    client = session.client

    if not client:
        return "No client associated with session"

    response_data = F.call_login_api(client.login_email, client.login_password, "admin")

    if not response_data.get("success"):
        return "Authentication failed"

    data = response_data.get("data", {})
    client.auth_token = data["token"]
    client.authenticated_at = now()
    client.save()

    return "Token refreshed successfully"
