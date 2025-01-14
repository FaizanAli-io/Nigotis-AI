from .fetcher import Fetcher
from .mapper import Mapper
from .reducer import Reducer
from .responder import Responder


class Pipeline:
    def __init__(self, auth_token):
        self.auth_token = auth_token

    def run_customer_segmentation(self):
        fetcher = Fetcher(self.auth_token)
        invoices = fetcher.get_client_invoices()

        customers = Mapper.map_invoices_to_customers(invoices)
        segmentation = Reducer.client_segmentation(customers)

        response = Responder.analyze_segmentation(segmentation)

        return response

    def run_product_preference(self):
        fetcher = Fetcher(self.auth_token)
        invoices = fetcher.get_client_invoices()

        customers = Mapper.map_invoices_to_customers(invoices)
        preferences = Reducer.product_preferences(customers)

        response = Responder.analyze_product_preferences(preferences)

        return response
