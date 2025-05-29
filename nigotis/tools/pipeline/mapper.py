import requests
from datetime import datetime

from utils import functions as F

BASE_URL = "https://nigotis-be.vercel.app/api/v1"


class Mapper:
    def __init__(self, auth_token):
        self.auth_token = auth_token

    @staticmethod
    def format_date(date_string):
        date_obj = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")
        return date_obj.strftime("%Y-%m-%d")

    def _make_request(self, url):
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = requests.get(url, headers=headers)

        if response.json().get("success") is False:
            raise requests.exceptions.RequestException(
                f"Error: {response.json().get('message')}"
            )

        response.raise_for_status()
        return response.json().get("data", None)

    def get_customers(self):
        clients_url = f"{BASE_URL}/client"
        clients = self._make_request(clients_url)

        customers = {
            client["_id"]: {
                "id": client["_id"],
                "name": F.extract_name(client),
                "products": [],
            }
            for client in clients
        }

        invoices_url = f"{BASE_URL}/client/invoice"
        invoices = self._make_request(invoices_url)

        for invoice in invoices:
            client = invoice.get("clientId")
            if not client:
                continue

            customer_id = client.get("_id")
            if customer_id not in customers:
                continue

            for item in invoice.get("items", []):
                product = item.get("productId", {})
                customers[customer_id]["products"].append(
                    {
                        "name": product.get("name", ""),
                        "price": product.get("price", 0),
                        "description": product.get("desc", ""),
                        "quantity": item.get("quantity", 0),
                        "issueDate": Mapper.format_date(invoice.get("issueDate", "")),
                    }
                )

        return list(customers.values())

    def get_products(self):
        products_url = f"{BASE_URL}/product"
        product_list = self._make_request(products_url)

        products = {
            product["_id"]: {
                "id": product["_id"],
                "name": product["name"],
                "price": product["price"],
                "clients": [],
            }
            for product in product_list
        }

        invoices_url = f"{BASE_URL}/client/invoice"
        invoices = self._make_request(invoices_url)

        for invoice in invoices:
            client = invoice.get("clientId")
            if not client:
                continue

            client_name = F.extract_name(client)

            for item in invoice.get("items", []):
                product = item.get("productId", {})
                product_id = product.get("_id")
                if product_id in products:
                    products[product_id]["clients"].append(
                        {"name": client_name, "quantity": item.get("quantity", 0)}
                    )

        return list(products.values())

    def get_invoices(self):
        url = f"{BASE_URL}/client/invoice"
        invoices = self._make_request(url)

        cleaned_invoices = []
        for invoice in invoices:
            cleaned_invoices.append(
                {
                    "id": invoice["_id"],
                    "name": F.extract_name(invoice["clientId"]),
                    "issueDate": Mapper.format_date(invoice["issueDate"]),
                    "dueDate": Mapper.format_date(invoice["dueDate"]),
                    "status": invoice["status"],
                    "products": [
                        {
                            "name": item["productId"]["name"],
                            "price": item["productId"]["price"],
                            "quantity": item["quantity"],
                        }
                        for item in invoice["items"]
                    ],
                }
            )

        return cleaned_invoices

    def get_incomes(self):
        url = f"{BASE_URL}/income"
        incomes = self._make_request(url)

        cleaned_incomes = []
        for income in incomes:
            cleaned_incomes.append(
                {
                    "id": income["_id"],
                    "type": income["type"],
                    "notes": income["notes"],
                    "status": income["status"],
                    "totalAmount": income["totalAmount"],
                    "date": Mapper.format_date(income["date"]),
                }
            )

        return cleaned_incomes

    def get_expenses(self):
        url = f"{BASE_URL}/company/expense"
        expenses = self._make_request(url)

        cleaned_expenses = []
        for expense in expenses:
            cleaned_expenses.append(
                {
                    "id": expense["_id"],
                    "type": expense["type"],
                    "title": expense["title"],
                    "description": expense["desc"],
                    "totalAmount": expense["totalAmount"],
                    "to": Mapper.format_date(expense["to"]),
                    "from": Mapper.format_date(expense["from"]),
                }
            )

        return cleaned_expenses

    def get_assets(self):
        url = f"{BASE_URL}/company/asset"
        assets = self._make_request(url)

        cleaned_assets = []
        for asset in assets:
            cleaned_assets.append(
                {
                    "id": asset["_id"],
                    "title": asset["title"],
                    "description": asset["desc"],
                    "quantity": asset["quantity"],
                    "totalAmount": asset["totalAmount"],
                    "date": Mapper.format_date(asset["date"]),
                }
            )

        return cleaned_assets

    def get_payrolls(self):
        url = f"{BASE_URL}/user"
        employees = self._make_request(url)

        cleaned_payrolls = []
        for employee in employees:
            jobInfo = employee.get("jobInfo", {})
            payInfo = jobInfo.get("payrollId")

            cleaned_payrolls.append(
                {
                    "id": employee["_id"],
                    "name": F.extract_name(employee),
                    "department": jobInfo.get("department", "N/A"),
                    "jobRole": jobInfo.get("jobRole", "N/A"),
                    "role": employee.get("role", "N/A"),
                }
                | (
                    {
                        "salary": payInfo.get("salary", 0),
                        "hourlyRate": payInfo.get("hourlyRate", 0),
                        "overtimeHourlyRate": payInfo.get("overtimeHourlyRate", 0),
                        "salaryType": payInfo.get("salaryType", 0),
                        "bonus": str(payInfo.get("bonus", 0)) + "%",
                        "tax": str(payInfo.get("tax", 0)) + "%",
                    }
                    if payInfo
                    else {"SalaryData": "No salary data"}
                )
            )

        return cleaned_payrolls
