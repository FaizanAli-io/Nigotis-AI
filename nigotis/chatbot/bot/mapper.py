from datetime import datetime


def format_date(date_string):
    date_obj = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    return date_obj.strftime("%d-%m-%Y")


class Mapper:
    @staticmethod
    def extract_client_name(client):
        info = client["personalInfo"]
        return f"{info['title']} {info['firstName']} {info['lastName']}"

    @staticmethod
    def map_invoices_to_customers(invoices):
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

    @staticmethod
    def map_invoices_to_products(invoices):
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

    @staticmethod
    def map_to_simplified_invoices(invoices):
        simplified_invoices = []

        for invoice in invoices:
            simplified_invoices.append(
                {
                    "client_name": Mapper.extract_client_name(invoice["clientId"]),
                    "issueDate": format_date(invoice["issueDate"]),
                    "dueDate": format_date(invoice["dueDate"]),
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

        return simplified_invoices
