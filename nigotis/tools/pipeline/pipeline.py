from .mapper import Mapper
from .reducer import Reducer
from .prompter import Prompter

from openai import OpenAI


class Pipeline:
    def __init__(self, token):
        self.client = OpenAI()
        self.mapper = Mapper(token)
        self.reducer = Reducer()
        self.prompter = Prompter()

    def _openai_response(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.75,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
        )

        return response.choices[0].message.content

    def _process_data(self, map_func, reduce_func, analyze_func):
        mapped = map_func()
        reduced = reduce_func(mapped)
        prompt = analyze_func(reduced)
        response = self._openai_response(prompt)

        return response

    def run_customer_segmentation(self):
        return self._process_data(
            self.mapper.get_customers,
            self.reducer.client_segmentation,
            self.prompter.analyze_segmentation,
        )

    def run_product_preference(self):
        return self._process_data(
            self.mapper.get_customers,
            self.reducer.product_preferences,
            self.prompter.analyze_product_preferences,
        )

    def run_revenue_insights(self):
        return self._process_data(
            self.mapper.get_customers,
            self.reducer.revenue_insights,
            self.prompter.analyze_revenue_insights,
        )

    def run_purchase_value(self):
        return self._process_data(
            self.mapper.get_invoices,
            self.reducer.purchase_value,
            self.prompter.analyze_purchase_value,
        )

    def run_seasonal_trends(self):
        return self._process_data(
            self.mapper.get_invoices,
            self.reducer.seasonal_trends,
            self.prompter.analyze_seasonal_trends,
        )

    def run_client_lifetime_value(self):
        return self._process_data(
            self.mapper.get_customers,
            self.reducer.client_lifetime_value,
            self.prompter.analyze_client_lifetime_value,
        )

    def run_churn_prediction(self):
        return self._process_data(
            self.mapper.get_invoices,
            self.reducer.inactive_clients,
            self.prompter.analyze_churn_prediction,
        )

    def run_most_purchased_products(self):
        return self._process_data(
            self.mapper.get_products,
            self.reducer.most_purchased_products,
            self.prompter.analyze_most_purchased_products,
        )

    def run_tailored_promotions(self):
        return self._process_data(
            self.mapper.get_customers,
            self.reducer.product_recommendations,
            self.prompter.analyze_tailored_promotions,
        )
