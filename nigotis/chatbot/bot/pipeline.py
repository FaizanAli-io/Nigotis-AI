from .mapper import Mapper
from .reducer import Reducer
from .responder import Responder
from .agent import BaseAgent, LlamaAgent


class Pipeline:
    def __init__(self, auth_token):
        self.mapper = Mapper(auth_token)
        self.base_agent = BaseAgent()
        self.llama_agent = LlamaAgent(self.mapper)

    def _process_data(self, map_func, reduce_func, analyze_func):
        mapped = map_func()
        reduced = reduce_func(mapped)
        prompt = analyze_func(reduced)

        return self.base_agent.get_response(prompt)

    def run_generic_question(self, message):
        return self.llama_agent.get_response(message)

    def run_customer_segmentation(self):
        return self._process_data(
            self.mapper.get_customers,
            Reducer.client_segmentation,
            Responder.analyze_segmentation,
        )

    def run_product_preference(self):
        return self._process_data(
            self.mapper.get_customers,
            Reducer.product_preferences,
            Responder.analyze_product_preferences,
        )

    def run_revenue_insights(self):
        return self._process_data(
            self.mapper.get_customers,
            Reducer.revenue_insights,
            Responder.analyze_revenue_insights,
        )

    def run_purchase_value(self):
        return self._process_data(
            self.mapper.get_invoices,
            Reducer.purchase_value,
            Responder.analyze_purchase_value,
        )

    def run_seasonal_trends(self):
        return self._process_data(
            self.mapper.get_invoices,
            Reducer.seasonal_trends,
            Responder.analyze_seasonal_trends,
        )

    def run_client_lifetime_value(self):
        return self._process_data(
            self.mapper.get_customers,
            Reducer.client_lifetime_value,
            Responder.analyze_client_lifetime_value,
        )

    def run_churn_prediction(self):
        return self._process_data(
            self.mapper.get_invoices,
            Reducer.inactive_clients,
            Responder.analyze_churn_prediction,
        )

    def run_most_purchased_products(self):
        return self._process_data(
            self.mapper.get_products,
            Reducer.most_purchased_products,
            Responder.analyze_most_purchased_products,
        )

    def run_tailored_promotions(self):
        return self._process_data(
            self.mapper.get_customers,
            Reducer.product_recommendations,
            Responder.analyze_tailored_promotions,
        )

    def run_analysis_func(self, choice):
        return {
            "SEG": self.run_customer_segmentation,
            "PRF": self.run_product_preference,
            "REV": self.run_revenue_insights,
            "PUR": self.run_purchase_value,
            "TRE": self.run_seasonal_trends,
            "CLV": self.run_client_lifetime_value,
            "CHP": self.run_churn_prediction,
            "MPP": self.run_most_purchased_products,
            "TPR": self.run_tailored_promotions,
        }.get(choice, lambda: "Feature not implemented yet")()
