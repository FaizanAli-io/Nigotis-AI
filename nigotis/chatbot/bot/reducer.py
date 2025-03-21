import numpy as np
from datetime import datetime
from collections import defaultdict


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
                    "quantity": top_product["quantity"],
                    "description": top_product["description"],
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

    # @staticmethod
    # def purchase_value(invoices):
    #     customers = {}

    #     for invoice in invoices:
    #         client_name = invoice["client_name"]
    #         transaction_value = sum(
    #             product["price"] * product["quantity"]
    #             for product in invoice["products"]
    #         )

    #         if client_name not in customers:
    #             customers[client_name] = {
    #                 "name": client_name,
    #                 "total_transaction_value": 0,
    #                 "total_invoices": 0,
    #             }

    #         customers[client_name]["total_transaction_value"] += transaction_value
    #         customers[client_name]["total_invoices"] += 1

    #     for customer in customers.values():
    #         customer["avg_transaction_value"] = (
    #             customer["total_transaction_value"] / customer["total_invoices"]
    #         )

    #     customer_list = list(customers.values())
    #     avg_transaction_values = [c["avg_transaction_value"] for c in customer_list]

    #     median = np.median(avg_transaction_values)

    #     high_value_clients = sorted(
    #         [c for c in customer_list if c["avg_transaction_value"] > median],
    #         key=lambda x: x["avg_transaction_value"],
    #         reverse=True,
    #     )
    #     low_value_clients = sorted(
    #         [c for c in customer_list if c["avg_transaction_value"] < median],
    #         key=lambda x: x["avg_transaction_value"],
    #         reverse=True,
    #     )

    #     return {
    #         "high_value_clients": high_value_clients,
    #         "low_value_clients": low_value_clients,
    #     }
    @staticmethod
    def purchase_value(invoices):
        customers = {}

        for invoice in invoices:
            client_name = invoice.get("client_name")
            if not client_name:
                print(f"Skipping invoice with missing client_name: {invoice}")
                continue

            transaction_value = sum(
                product["price"] * product["quantity"]
                for product in invoice.get("products", [])
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

    @staticmethod
    def seasonal_trends(invoices):
        monthly_sales = defaultdict(int)

        for invoice in invoices:
            issue_date = datetime.strptime(invoice["issueDate"], "%d-%m-%Y")
            month = issue_date.strftime("%Y-%m")
            for product in invoice["products"]:
                monthly_sales[month] += product["quantity"] * product["price"]

        return dict(monthly_sales)

    @staticmethod
    def client_lifetime_value(customers):
        client_ltv = {}

        for customer in customers:
            client_name = customer["name"]
            total_value = 0
            for product in customer["products"]:
                total_value += product["quantity"] * product["price"]
            client_ltv[client_name] = total_value

        return client_ltv

    # @staticmethod
    # def inactive_clients(invoices):
    #     inactive_clients = []
    #     client_last_purchase = {}
    #     current_date = datetime.now()
    #     inactivity_threshold_days = 90

    #     for invoice in invoices:
    #         issue_date = datetime.strptime(invoice["issueDate"], "%d-%m-%Y")
    #         client_name = invoice["client_name"]

    #         if (
    #             client_name not in client_last_purchase
    #             or issue_date > client_last_purchase[client_name]["issue_date"]
    #         ):
    #             last_products = [product["name"] for product in invoice["products"]]
    #             client_last_purchase[client_name] = {
    #                 "issue_date": issue_date,
    #                 "last_products": last_products,
    #             }

    #     for client_name, data in client_last_purchase.items():
    #         days_inactive = (current_date - data["issue_date"]).days
    #         if days_inactive > inactivity_threshold_days:
    #             inactive_clients.append(
    #                 {
    #                     "client_name": client_name,
    #                     "days_inactive": days_inactive,
    #                     "last_products": data["last_products"],
    #                 }
    #             )

    #     return inactive_clients
    @staticmethod
    def inactive_clients(invoices):
        inactive_clients = []
        client_last_purchase = {}
        current_date = datetime.now()
        inactivity_threshold_days = 90

        for invoice in invoices:
            try:
                client_name = invoice.get("client_name", None)
                issue_date_str = invoice.get("issueDate", None)

                if not client_name or not issue_date_str:
                    print(f"Skipping invoice due to missing data: {invoice}")
                    continue  # Skip invoices with missing client_name or issueDate

                issue_date = datetime.strptime(issue_date_str, "%d-%m-%Y")

                if (
                    client_name not in client_last_purchase
                    or issue_date > client_last_purchase[client_name]["issue_date"]
                ):
                    last_products = [
                        product["name"] for product in invoice.get("products", [])
                    ]
                    client_last_purchase[client_name] = {
                        "issue_date": issue_date,
                        "last_products": last_products,
                    }

            except Exception as e:
                print(f"Error processing invoice: {invoice}, Error: {str(e)}")
                continue

        for client_name, data in client_last_purchase.items():
            days_inactive = (current_date - data["issue_date"]).days
            if days_inactive > inactivity_threshold_days:
                inactive_clients.append(
                    {
                        "client_name": client_name,
                        "days_inactive": days_inactive,
                        "last_products": data["last_products"],
                    }
                )

        return inactive_clients

    @staticmethod
    def most_purchased_products(products):
        product_sales = defaultdict(int)

        for product in products:
            for client in product["clients"]:
                product_sales[product["name"]] += client["quantity"]

        sorted_products = sorted(
            product_sales.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        return sorted_products

    @staticmethod
    def product_recommendations(customers):
        client_recommendations = {}

        for customer in customers:
            client_name = customer["name"]
            product_frequency = defaultdict(int)

            for product in customer["products"]:
                product_frequency[product["name"]] += 1

            sorted_products = sorted(
                product_frequency.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            client_recommendations[client_name] = [
                product for product, _ in sorted_products[:3]
            ]

        return client_recommendations
