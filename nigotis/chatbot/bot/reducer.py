import numpy as np


class Reducer:
    @staticmethod
    def client_segmentation(customers):
        purchase_frequencies = [
            sum(product["quantity"] for product in customer["products"])
            for customer in customers
        ]

        # Calculate quartiles
        lower_quartile = np.percentile(purchase_frequencies, 25)
        upper_quartile = np.percentile(purchase_frequencies, 75)

        segmentation = {
            "high_frequency": [],
            "medium_frequency": [],
            "low_frequency": [],
        }

        for customer, total_purchases in zip(customers, purchase_frequencies):
            data = {"name": customer["name"], "total_purchases": total_purchases}
            if total_purchases > upper_quartile:
                segmentation["high_frequency"].append(data)
            elif lower_quartile <= total_purchases <= upper_quartile:
                segmentation["medium_frequency"].append(data)
            else:
                segmentation["low_frequency"].append(data)

        return segmentation

    @staticmethod
    def product_preferences(customers):
        preferences = {}

        for customer in customers:
            products = customer["products"]
            # Identify the top product based on quantity
            top_product = max(products, key=lambda p: p["quantity"])
            preferences[customer["id"]] = {
                "name": customer["name"],
                "top_product": {
                    "name": top_product["name"],
                    "description": top_product["description"],
                    "quantity": top_product["quantity"],
                },
            }

        return preferences

    @staticmethod
    def revenue_insights(customers):
        revenue_data = []
        for customer in customers:
            total_revenue = sum(
                p["price"] * p["quantity"] for p in customer["products"]
            )
            revenue_data.append(
                {"name": customer["name"], "total_revenue": total_revenue}
            )

        top_clients = sorted(
            revenue_data, key=lambda x: x["total_revenue"], reverse=True
        )
        return {"top_clients": top_clients[:5]}

    @staticmethod
    def purchase_value(invoices):
        customers = {}

        for invoice in invoices:
            client_name = invoice["client_name"]
            transaction_value = sum(
                product["price"] * product["quantity"]
                for product in invoice["products"]
            )

            if client_name not in customers:
                customers[client_name] = {
                    "name": client_name,
                    "total_transaction_value": 0,
                    "total_invoices": 0,
                }

            customers[client_name]["total_transaction_value"] += transaction_value
            customers[client_name]["total_invoices"] += 1

        for customer in customers.values():
            customer["avg_transaction_value"] = (
                customer["total_transaction_value"] / customer["total_invoices"]
            )

        customer_list = list(customers.values())
        avg_transaction_values = [c["avg_transaction_value"] for c in customer_list]

        median = np.median(avg_transaction_values)

        high_value_clients = sorted(
            [c for c in customer_list if c["avg_transaction_value"] > median],
            key=lambda x: x["avg_transaction_value"],
            reverse=True,
        )
        low_value_clients = sorted(
            [c for c in customer_list if c["avg_transaction_value"] < median],
            key=lambda x: x["avg_transaction_value"],
            reverse=True,
        )

        return {
            "high_value_clients": high_value_clients,
            "low_value_clients": low_value_clients,
        }
