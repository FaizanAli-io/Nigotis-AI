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
