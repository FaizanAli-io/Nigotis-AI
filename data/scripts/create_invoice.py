import requests
import random
from datetime import datetime, timedelta

client_ids = [
    "6782143b2b1598fa2f872050",
    "678214542b1598fa2f87205d",
    "67829adf651f216c6cd0a07b",
    "6785656a08a717f49d63b799",
    "6785657908a717f49d63b7a6",
    "6785658c08a717f49d63b7b3",
    "6785659908a717f49d63b7c0",
    "678565a808a717f49d63b7cd",
    "678565b908a717f49d63b7da",
    "678565ea08a717f49d63b7eb",
    "678565f508a717f49d63b7f8",
    "678565fe08a717f49d63b805",
]

product_ids = [
    "678019b290e149b98a291617",
    "678019ca90e149b98a291622",
    "678019de90e149b98a29162a",
    "678019e490e149b98a291632",
    "678019eb90e149b98a29163a",
    "6785669208a717f49d63b81a",
    "6785669a08a717f49d63b822",
    "678566ad08a717f49d63b82a",
    "678566b508a717f49d63b832",
    "678566bc08a717f49d63b83a",
]


def generate_random_invoice():
    client_id = random.choice(client_ids)
    issue_date = datetime.now().strftime("%Y-%m-%d")
    due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    tax = random.randint(5, 10)
    discount = random.randint(5, 10)

    product_count = random.randint(1, 4)
    items = []
    selected_products = set()

    while len(selected_products) < product_count:
        product_id = random.choice(product_ids)
        if product_id not in selected_products:
            selected_products.add(product_id)
            items.append(
                {
                    "productId": product_id,
                    "quantity": random.randint(2, 4),
                }
            )

    return {
        "clientId": client_id,
        "issueDate": issue_date,
        "dueDate": due_date,
        "status": "pending",
        "tax": tax,
        "discount": discount,
        "paidAmount": 0,
        "items": items,
    }


def send_invoices(count):
    url = "https://nigotis-be.vercel.app/api/v1/client/invoice"
    auth_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY3MjhmNTE3N2I5YjdkZjJiMDA4YTA0MyIsImlhdCI6MTczNzAyMDI0NCwiZXhwIjoxNzM5NjEyMjQ0fQ.e0TS6-ZmUw2UqDM6bPCJElVkLMv7xLeXURlkvAiS62o"

    for i in range(count):
        invoice = generate_random_invoice()

        response = requests.post(
            url,
            json=invoice,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        print(response.json()["message"])


send_invoices(0)
