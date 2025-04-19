class Responder:
    # @staticmethod
    # def analyze_segmentation(segmentation_data):
    #     prompt = (
    #         "You are a business analyst. I have data on customer purchase frequencies segmented into high, "
    #         "medium, and low frequency groups. Present the data in a clear and structured way, then analyze it. "
    #         "Here is the data:\n\n"
    #     )
    #     for group, clients in segmentation_data.items():
    #         prompt += f"{group.capitalize()} Frequency:\n"
    #         for client in clients:
    #             prompt += f"- {client['name']}: Total Purchases = {client['total_purchases']}\n"
    #         prompt += "\n"

    #     prompt += (
    #         "After presenting the data, please provide insights on customer behavior and possible marketing strategies "
    #         "for each group (high, medium, low frequency). Make the analysis user-friendly and actionable."
    #     )

    #     return prompt

    # @staticmethod
    # def analyze_product_preferences(preferences_data):
    #     prompt = (
    #         "You are a product analyst. I have data on customer product preferences showing each customer's top product "
    #         "based on quantity purchased. Present the data in a structured format, then analyze it. Here is the data:\n\n"
    #     )
    #     for _, customer_data in preferences_data.items():
    #         prompt += f"Customer: {customer_data['name']}\nTop Product: {customer_data['top_product']['name']}\n"
    #         prompt += f"Description: {customer_data['top_product']['description']}\nQuantity: {customer_data['top_product']['quantity']}\n\n"

    #     prompt += (
    #         "After presenting the data, provide insights on customer preferences, potential product recommendations, "
    #         "and strategies for product-related marketing or upselling. Make the analysis user-friendly and actionable."
    #     )

    #     return prompt

    # @staticmethod
    # def analyze_revenue_insights(revenue_data):
    #     prompt = (
    #         "You are a business analyst. I have data on customer revenue showing top clients based on the total value of their purchases. "
    #         "Present the data in a structured format, then analyze it. Here is the data:\n\n"
    #     )
    #     for client in revenue_data["top_clients"]:
    #         prompt += f"Client: {client['name']}\nTotal Revenue: {client['total_revenue']}\n\n"

    #     prompt += "After presenting the data, provide insights on the high-value clients, how to nurture relationships with them, and any patterns in customer revenue behavior."

    #     return prompt
    @staticmethod
    def analyze_segmentation(segmentation_data):
        prompt = (
            "Your name is Nigotis-AI, your role is data-analyst. "
            "Provide a clean and concise output, ensuring it is well-formatted for WhatsApp messages. "
            "Use *single asterisk* for bold text, as WhatsApp does not support double asterisks. "
            "Avoid structured formats like tables, bullet points, or JSON. "
            "Instead, present the information naturally, like: Ms. Sarah has a total revenue of $51,500. "
            "Maintain a professional and engaging tone while making the message easy to read and visually appealing. "
            "Avoid redundant data retrieval and apply filtering only when necessary. "
            "Respond strictly in English.\n\n"
            "You are a business analyst. I have data on customer purchase frequencies segmented into high, "
            "medium, and low frequency groups. Present the data in a clear way, then analyze it. "
            "Here is the data:\n\n"
        )
        for group, clients in segmentation_data.items():
            prompt += f"{group.capitalize()} Frequency:\n"
            for client in clients:
                prompt += f"- {client['name']}: Total Purchases = {client['total_purchases']}\n"
            prompt += "\n"

        prompt += (
            "After presenting the data, please provide insights on customer behavior and possible marketing strategies "
            "for each group (high, medium, low frequency). Make the analysis user-friendly and actionable."
        )

        return prompt

    @staticmethod
    def analyze_product_preferences(preferences_data):
        prompt = (
            "Your name is Nigotis-AI, your role is data-analyst. "
            "Provide a clean and concise output, ensuring it is well-formatted for WhatsApp messages. "
            "Use *single asterisk* for bold text, as WhatsApp does not support double asterisks. "
            "Avoid structured formats like tables, bullet points, or JSON. "
            "Instead, present the information naturally, like: Ms. Sarah has a total revenue of $51,500. "
            "Maintain a professional and engaging tone while making the message easy to read and visually appealing. "
            "Avoid redundant data retrieval and apply filtering only when necessary. "
            "Respond strictly in English.\n\n"
            "You are a product analyst. I have data on customer product preferences showing each customer's top product "
            "based on quantity purchased. Present the data in a structured format, then analyze it. Here is the data:\n\n"
        )
        for _, customer_data in preferences_data.items():
            prompt += f"Customer: {customer_data['name']}\nTop Product: {customer_data['top_product']['name']}\n"
            prompt += f"Description: {customer_data['top_product']['description']}\nQuantity: {customer_data['top_product']['quantity']}\n\n"

        prompt += (
            "After presenting the data, provide insights on customer preferences, potential product recommendations, "
            "and strategies for product-related marketing or upselling. Make the analysis user-friendly and actionable."
        )

        return prompt

    @staticmethod
    def analyze_revenue_insights(revenue_data):
        prompt = (
            "Your name is Nigotis-AI, your role is data-analyst. "
            "Provide a clean and concise output, ensuring it is well-formatted for WhatsApp messages. "
            "Use *single asterisk* for bold text, as WhatsApp does not support double asterisks. "
            "Avoid structured formats like tables, bullet points, or JSON. "
            "Instead, present the information naturally, like: Ms. Sarah has a total revenue of $51,500. "
            "Maintain a professional and engaging tone while making the message easy to read and visually appealing. "
            "Avoid redundant data retrieval and apply filtering only when necessary. "
            "Respond strictly in English.\n\n"
            "You are a business analyst. I have data on customer revenue showing top clients based on the total value of their purchases. "
            "Present the data in a structured format, then analyze it. Here is the data:\n\n"
        )
        for client in revenue_data["top_clients"]:
            prompt += f"Client: {client['name']}\nTotal Revenue: {client['total_revenue']}\n\n"

        prompt += "After presenting the data, provide insights on the high-value clients, how to nurture relationships with them, and any patterns in customer revenue behavior."

        return prompt

    @staticmethod
    def analyze_purchase_value(purchase_value_data):
        prompt = (
            "You are a business strategist. I have data on customer purchase sizes and value, including high-value and low-value clients. "
            "Present the data in a structured format, then analyze it. Here is the data:\n\n"
        )
        prompt += "High Value:\n"
        for client in purchase_value_data["high_value_clients"]:
            prompt += f"Client: {client['name']}\nAverage Transaction: {client['avg_transaction_value']}\nTotal Value: {client['total_transaction_value']}\n\n"

        prompt += "Low Value:\n"
        for client in purchase_value_data["low_value_clients"]:
            prompt += f"Client: {client['name']}\nAverage Transaction: {client['avg_transaction_value']}\nTotal Value: {client['total_transaction_value']}\n\n"

        prompt += (
            "After presenting the data, please provide actionable insights on upselling strategies for high-value clients, "
            "and how to promote budget-friendly options to low-value clients. Also, provide strategies for increasing transaction values."
        )

        return prompt

    @staticmethod
    def analyze_seasonal_trends(seasonal_trends_data):
        prompt = (
            "You are a business strategist. I have data on seasonal trends for client purchases over time. "
            "Present the data in a structured format, then analyze it. Here is the data for monthly sales:\n\n"
        )
        for month, total_sales in seasonal_trends_data.items():
            prompt += f"Month: {month}\nTotal Sales: {total_sales}\n\n"

        prompt += (
            "After presenting the data, provide actionable insights on how to adjust marketing strategies for peak seasons, "
            "and how to sustain or grow sales during off-peak seasons."
        )

        return prompt

    @staticmethod
    def analyze_client_lifetime_value(client_ltv_data):
        prompt = (
            "You are a business strategist. I have data on client lifetime values based on their purchase history. "
            "Present the data in a structured format, then analyze it. Here is the data:\n\n"
        )
        for client_name, total_value in client_ltv_data.items():
            prompt += f"Client: {client_name}\nLifetime Value: {total_value}\n\n"

        prompt += (
            "After presenting the data, provide actionable insights on how to retain high-value clients, "
            "and how to increase lifetime value for clients with lower values."
        )

        return prompt

    @staticmethod
    def analyze_churn_prediction(inactive_clients_data):
        prompt = (
            "You are a business strategist. I have data on clients who have become inactive based on their purchase activity. "
            "Present the data in a structured format, then analyze it. Here is the data for inactive clients:\n\n"
        )
        for client in inactive_clients_data:
            prompt += (
                f"Client: {client['client_name']}\n"
                f"Duration of Inactivity: {client['days_inactive']} days\n"
                f"Last Purchased Products: {', '.join(client['last_products'])}\n\n"
            )

        prompt += (
            "After presenting the data, provide actionable insights on how to re-engage inactive clients, "
            "including personalized outreach strategies, promotions, and product suggestions."
        )

        return prompt

    @staticmethod
    def analyze_most_purchased_products(most_purchased_data):
        prompt = (
            "You are a business strategist. I have data on the most purchased products by clients. "
            "Present the data in a structured format, then analyze it. Here is the data for the most popular products:\n\n"
        )
        for product, total_sales in most_purchased_data:
            prompt += f"Product: {product}\nTotal Sales: {total_sales}\n\n"

        prompt += (
            "After presenting the data, provide actionable insights on how to promote these popular products, "
            "including cross-selling and upselling strategies, and how to use customer data to personalize offers."
        )

        return prompt

    @staticmethod
    def analyze_tailored_promotions(client_recommendations_data):
        prompt = (
            "You are a business strategist. I have data on personalized product recommendations for clients. "
            "Present the data in a structured format, then analyze it. Here is the data for recommended products:\n\n"
        )
        for client_name, recommendations in client_recommendations_data.items():
            prompt += f"Client: {client_name}\nRecommended Products: {', '.join(recommendations)}\n\n"

        prompt += (
            "After presenting the data, provide actionable insights on how to create personalized promotions, "
            "including product bundles, discounts, and targeted campaigns to increase client engagement and purchases."
        )

        return prompt
