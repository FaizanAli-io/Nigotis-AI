from .fetcher import Fetcher
from .mapper import Mapper
from .reducer import Reducer
from .responder import Responder


class Pipeline:
    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.fetcher = Fetcher(self.auth_token)

    def _process_data(self, fetch_func, map_func, reduce_func, analyze_func):
        data = fetch_func()
        mapped = map_func(data)
        reduced = reduce_func(mapped)
        response = analyze_func(reduced)

        return response

    def run_customer_segmentation(self):
        return self._process_data(
            self.fetcher.get_client_invoices,
            Mapper.map_invoices_to_customers,
            Reducer.client_segmentation,
            Responder.analyze_segmentation,
        )

    def run_product_preference(self):
        return self._process_data(
            self.fetcher.get_client_invoices,
            Mapper.map_invoices_to_customers,
            Reducer.product_preferences,
            Responder.analyze_product_preferences,
        )

    def run_revenue_insights(self):
        return self._process_data(
            self.fetcher.get_client_invoices,
            Mapper.map_invoices_to_customers,
            Reducer.revenue_insights,
            Responder.analyze_revenue_insights,
        )

    def run_purchase_value(self):
        return self._process_data(
            self.fetcher.get_client_invoices,
            Mapper.map_to_simplified_invoices,
            Reducer.purchase_value,
            Responder.analyze_purchase_value,
        )
