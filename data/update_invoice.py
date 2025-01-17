import requests
from datetime import datetime, timedelta
import random

SEASONAL_TRENDS = {
    "Q1": ("2024-01-01", "2024-03-31"),  # Quarter 1 date range
    "Q2": ("2024-04-01", "2024-06-30"),  # Quarter 2 date range
    "Q3": ("2024-07-01", "2024-09-30"),  # Quarter 3 date range
    "Q4": ("2024-10-01", "2024-12-31"),  # Quarter 4 date range
}

QUARTER_WEIGHTS = {"Q1": 0.4, "Q2": 0.1, "Q3": 0.1, "Q4": 0.4}


def random_date_within_range(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)


def generate_seasonal_issue_date():
    quarter = random.choices(
        population=list(QUARTER_WEIGHTS.keys()),
        weights=list(QUARTER_WEIGHTS.values()),
        k=1,
    )[0]
    start_date, end_date = SEASONAL_TRENDS[quarter]
    return random_date_within_range(start_date, end_date).strftime("%Y-%m-%d")


def update_invoices():
    url = "https://nigotis-be.vercel.app/api/v1/client/invoice"
    auth_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY3MjhmNTE3N2I5YjdkZjJiMDA4YTA0MyIsImlhdCI6MTczNzAyMDI0NCwiZXhwIjoxNzM5NjEyMjQ0fQ.e0TS6-ZmUw2UqDM6bPCJElVkLMv7xLeXURlkvAiS62o"

    try:
        response = requests.get(url, headers={"Authorization": f"Bearer {auth_token}"})
        response.raise_for_status()

        invoices = response.json()["data"]
        for i, invoice in enumerate(invoices):
            issue_date = datetime.strptime(generate_seasonal_issue_date(), "%Y-%m-%d")
            due_date = (issue_date + timedelta(days=30)).strftime("%Y-%m-%d")

            update_payload = {
                "invoiceId": invoice["_id"],
                "issueDate": issue_date.strftime("%Y-%m-%d"),
                "dueDate": due_date,
            }

            update_response = requests.put(
                url,
                json=update_payload,
                headers={"Authorization": f"Bearer {auth_token}"},
            )
            update_response.raise_for_status()
            print(f"Invoice {i+1} updated successfully.")

    except requests.exceptions.RequestException as e:
        print(f"Error updating invoices: {e}")


update_invoices()
