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
