import requests
from datetime import datetime

import json


class Mapper:
    def __init__(self, auth_token):
        self.auth_token = auth_token

    @staticmethod
    def format_date(date_string):
        date_obj = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")
        return date_obj.strftime("%d-%m-%Y")

    @staticmethod
    def extract_client_name(client):
        info = client["personalInfo"]
        return f"{info['title']} {info['firstName']} {info['lastName']}"

    def _make_request(self, url):
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json().get("data", None)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def map_customers(self):
        url = "https://nigotis-be.vercel.app/api/v1/client/invoice"
        invoices = self._make_request(url)

        customers = {}
        for invoice in invoices:
            client = invoice["clientId"]
            customer_id = client["_id"]
            if customer_id not in customers:
                customers[customer_id] = {
                    "id": customer_id,
                    "name": Mapper.extract_client_name(client),
                    "products": [],
                }

            for item in invoice["items"]:
                product = item["productId"]
                customers[customer_id]["products"].append(
                    {
                        "name": product["name"],
                        "price": product["price"],
                        "description": product["desc"],
                        "quantity": item["quantity"],
                    }
                )

        return list(customers.values())

    def map_products(self):
        url = "https://nigotis-be.vercel.app/api/v1/client/invoice"
        invoices = self._make_request(url)

        products = {}
        for invoice in invoices:
            client = invoice["clientId"]
            client_name = Mapper.extract_client_name(client)

            for item in invoice["items"]:
                product = item["productId"]
                product_id = product["_id"]

                if product_id not in products:
                    products[product_id] = {
                        "name": product["name"],
                        "price": product["price"],
                        "clients": [],
                    }

                products[product_id]["clients"].append(
                    {
                        "client_name": client_name,
                        "quantity": item["quantity"],
                    }
                )

        return list(products.values())

    def map_invoices(self):
        url = "https://nigotis-be.vercel.app/api/v1/client/invoice"
        invoices = self._make_request(url)

        cleaned_invoices = []
        for invoice in invoices:
            cleaned_invoices.append(
                {
                    "client_name": Mapper.extract_client_name(invoice["clientId"]),
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

    def map_income(self):
        url = "https://nigotis-be.vercel.app/api/v1/income"
        incomes = self._make_request(url)

        cleaned_incomes = []
        for income in incomes:
            cleaned_incomes.append(
                {
                    "type": income["type"],
                    "notes": income["notes"],
                    "status": income["status"],
                    "totalAmount": income["totalAmount"],
                    "date": Mapper.format_date(income["date"]),
                }
            )

        return cleaned_incomes

    def map_expenses(self):
        url = "https://nigotis-be.vercel.app/api/v1/company/expense"
        expenses = self._make_request(url)

        cleaned_expenses = []
        for expense in expenses:
            cleaned_expenses.append(
                {
                    "type": expense["type"],
                    "title": expense["title"],
                    "description": expense["desc"],
                    "totalAmount": expense["totalAmount"],
                    "to": Mapper.format_date(expense["to"]),
                    "from": Mapper.format_date(expense["from"]),
                    "date": Mapper.format_date(expense["date"]),
                }
            )

        return cleaned_expenses

    def map_assets(self):
        url = "https://nigotis-be.vercel.app/api/v1/company/asset"
        assets = self._make_request(url)

        cleaned_assets = []
        for asset in assets:
            cleaned_assets.append(
                {
                    "title": asset["title"],
                    "description": asset["desc"],
                    "quantity": asset["quantity"],
                    "totalAmount": asset["totalAmount"],
                    "date": Mapper.format_date(asset["date"]),
                }
            )

        return cleaned_assets
