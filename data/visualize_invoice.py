import requests
from datetime import datetime
from collections import defaultdict
from matplotlib import pyplot as plt


def visualize_invoice_distribution():
    url = "https://nigotis-be.vercel.app/api/v1/client/invoice"
    auth_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY3MjhmNTE3N2I5YjdkZjJiMDA4YTA0MyIsImlhdCI6MTczNzAyMDI0NCwiZXhwIjoxNzM5NjEyMjQ0fQ.e0TS6-ZmUw2UqDM6bPCJElVkLMv7xLeXURlkvAiS62o"

    try:
        response = requests.get(url, headers={"Authorization": f"Bearer {auth_token}"})
        response.raise_for_status()

        invoices = response.json()["data"]

        month_counts = defaultdict(int)
        for invoice in invoices:
            issue_date = invoice.get("issueDate")
            if issue_date:
                month = datetime.strptime(
                    issue_date.split("T")[0], "%Y-%m-%d"
                ).strftime("%Y-%m")
                month_counts[month] += 1

        for month, count in month_counts.items():
            print(f"{month}: {count} invoices")

        sorted_months = sorted(month_counts.items())
        months, counts = zip(*sorted_months)

        plt.figure(figsize=(12, 6))
        plt.bar(months, counts, color="skyblue")
        plt.xticks(rotation=45, ha="right")
        plt.title("Invoice Issue Month Distribution")
        plt.xlabel("Issue Months")
        plt.ylabel("Number of Invoices")
        plt.tight_layout()
        plt.show()

    except requests.exceptions.RequestException as e:
        print(f"Error visualizing invoice distribution: {e}")


visualize_invoice_distribution()
