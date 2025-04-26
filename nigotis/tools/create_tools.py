import requests

from langchain_core.tools import tool

BASE_URL = "https://nigotis-be.vercel.app/api/v1"


@tool
def create_asset(
    token: str,
    title: str,
    desc: str,
    quantity: int,
    date: str,
    totalAmount: float,
) -> str:
    """Create a company asset using provided details."""
    response = requests.post(
        f"{BASE_URL}/company/asset",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": title,
            "desc": desc,
            "quantity": quantity,
            "date": date,
            "totalAmount": totalAmount,
        },
    )
    return "Asset created" if response.status_code == 201 else "Asset creation failed"


@tool
def create_expense(
    token: str,
    title: str,
    desc: str,
    type: str,
    totalAmount: float,
    date: str,
    from_date: str,
    to_date: str,
) -> str:
    """Create a company expense using provided details."""
    response = requests.post(
        f"{BASE_URL}/company/expense",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": title,
            "desc": desc,
            "type": type,
            "totalAmount": totalAmount,
            "date": date,
            "from": from_date,
            "to": to_date,
        },
    )
    return (
        "Expense created" if response.status_code == 201 else "Expense creation failed"
    )


@tool
def create_income(
    token: str,
    type: str,
    totalAmount: float,
    date: str,
    notes: str,
) -> str:
    """Create an income record using provided details."""
    response = requests.post(
        f"{BASE_URL}/income",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "type": type,
            "totalAmount": totalAmount,
            "date": date,
            "notes": notes,
        },
    )
    return "Income created" if response.status_code == 201 else "Income creation failed"
