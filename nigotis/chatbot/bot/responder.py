import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class Responder:
    @staticmethod
    def analyze_segmentation(segmentation_data, max_words=300):
        prompt = (
            "You are a business analyst. I have data on customer purchase frequencies segmented into high, "
            "medium, and low frequency groups. Here is the data:\n\n"
        )
        for group, clients in segmentation_data.items():
            prompt += f"{group.capitalize()} Frequency:\n"
            for client in clients:
                prompt += f"- {client['name']}: Total Purchases = {client['total_purchases']}\n"
            prompt += "\n"

        prompt += (
            "Please analyze the data and provide insights on customer behavior and possible marketing strategies "
            "for each group (high, medium, low frequency). Make the analysis user-friendly and actionable."
        )

        return Responder.get_gpt_response(prompt, max_words)

    @staticmethod
    def analyze_product_preferences(preferences_data, max_words=300):
        prompt = (
            "You are a product analyst. I have data on customer product preferences showing each customer's top product "
            "based on quantity purchased. Here is the data:\n\n"
        )
        for _, customer_data in preferences_data.items():
            prompt += f"Customer: {customer_data['name']}\nTop Product: {customer_data['top_product']['name']}\n"
            prompt += f"Description: {customer_data['top_product']['description']}\nQuantity: {customer_data['top_product']['quantity']}\n\n"

        prompt += (
            "Please analyze the data and provide insights on customer preferences, potential product recommendations, "
            "and strategies for product-related marketing or upselling. Make the analysis user-friendly and actionable."
        )

        return Responder.get_gpt_response(prompt, max_words)

    @staticmethod
    def analyze_revenue_insights(revenue_data, max_words=300):
        prompt = (
            "You are a business analyst. I have data on customer revenue showing top clients based on the total value of their purchases. "
            "Here is the data:\n\n"
        )
        for client in revenue_data["top_clients"]:
            prompt += f"Client: {client['name']}\nTotal Revenue: {client['total_revenue']}\n\n"

        prompt += "Please analyze the data and provide insights on the high-value clients, how to nurture relationships with them, and any other patterns you observe in customer revenue behavior."

        return Responder.get_gpt_response(prompt, max_words)

    @staticmethod
    def analyze_purchase_value(purchase_value_data, max_words=300):
        prompt = (
            "You are a business strategist. I have data on customer purchase sizes and value, including high-value and low-value clients. "
            "Here is the data:\n\n"
        )
        prompt += "High Value:\n"
        for client in purchase_value_data["high_value_clients"]:
            prompt += f"Client: {client['name']}\nAverage Transaction: {client['avg_transaction_value']}\nTotal Value: {client['total_transaction_value']}\n\n"

        prompt += "Low Value:\n"
        for client in purchase_value_data["low_value_clients"]:
            prompt += f"Client: {client['name']}\nAverage Transaction: {client['avg_transaction_value']}\nTotal Value: {client['total_transaction_value']}\n\n"

        prompt += (
            "Please analyze the data and provide actionable insights on upselling strategies for high-value clients, "
            "and how to promote budget-friendly options to low-value clients. Also, provide strategies for increasing transaction values."
        )

        return Responder.get_gpt_response(prompt, max_words)

    @staticmethod
    def get_gpt_response(prompt, max_words):
        key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=key)

        # Approximate tokens per word (using 4 tokens per word as a general estimate)
        max_tokens = max_words * 4

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )

        return response.choices[0].message.content.strip()
