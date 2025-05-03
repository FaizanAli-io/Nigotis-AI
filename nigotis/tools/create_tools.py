import requests
from typing import TypedDict

from langchain_core.tools import tool

from .helpers import (
    resolve_client_name,
    resolve_product_name,
)

BASE_URL = "https://nigotis-be.vercel.app/api/v1"


@tool
def create_client(
    token: str,
    email: str,
    title: str,
    firstName: str,
    middleName: str,
    lastName: str,
    joinDate: str,
) -> str:
    """Create a client with the provided details."""
    response = requests.post(
        f"{BASE_URL}/client",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": email,
            "title": title,
            "firstName": firstName,
            "middleName": middleName,
            "lastName": lastName,
            "joinDate": joinDate,
        },
    )

    return response.json()


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

    return response.json()


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

    return response.json()


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

    return response.json()


class Item(TypedDict):
    productName: str
    quantity: int


@tool
def create_invoice(
    token: str,
    client_name: str,
    issueDate: str,
    dueDate: str,
    status: str,
    paidAmount: float,
    items: list[Item],
    tax: float = 0,
    discount: float = 0,
) -> str:
    """
    Create an invoice using client and product names with invoice details.

    Parameters:
    - token: Authorization token.
    - client_name: Name of the client (used to resolve client ID).
    - issueDate: Invoice issue date (YYYY-MM-DD).
    - dueDate: Invoice due date (YYYY-MM-DD).
    - status: Status of the invoice (e.g., "pending", "paid").
    - paidAmount: Amount paid towards the invoice.
    - items: A list of items, where each item is:
        (productName: str, quantity: int).
            - productName: Name of the product (used to resolve product ID).
            - quantity: Quantity of the product.
    - tax: Tax amount (default 0).
    - discount: Discount amount (default 0).
    """

    client_id = resolve_client_name(token, client_name)
    if isinstance(client_id, str) and client_id.startswith("⚠"):
        return client_id

    resolved_items = []
    for item in items:
        product_name, quantity = item["productName"], item["quantity"]
        product_id = resolve_product_name(token, product_name)
        if isinstance(product_id, str) and product_id.startswith("⚠"):
            return product_id
        resolved_items.append(
            {
                "productId": product_id,
                "quantity": quantity,
            }
        )

    response = requests.post(
        f"{BASE_URL}/client/invoice",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "clientId": client_id,
            "issueDate": issueDate,
            "dueDate": dueDate,
            "status": status,
            "tax": tax,
            "discount": discount,
            "paidAmount": paidAmount,
            "items": resolved_items,
        },
    )

    return response.json()
