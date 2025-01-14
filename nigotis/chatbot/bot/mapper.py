class Mapper:
    @staticmethod
    def map_invoices_to_customers(invoices):
        customers = {}

        for invoice in invoices:
            client = invoice["clientId"]
            info = client["personalInfo"]

            customer_id = client["_id"]
            if customer_id not in customers:
                customers[customer_id] = {
                    "id": customer_id,
                    "name": f"{info['title']} {info['firstName']} {info['lastName']}",
                    "email": client["email"],
                    "address": info["address"],
                    "phone": info["phone"],
                    "products": [],
                }

            for item in invoice["items"]:
                product = item["productId"]
                customers[customer_id]["products"].append(
                    {
                        "id": product["_id"],
                        "name": product["name"],
                        "description": product["desc"],
                        "price": product["price"],
                        "quantity": item["quantity"],
                    }
                )

        return list(customers.values())
