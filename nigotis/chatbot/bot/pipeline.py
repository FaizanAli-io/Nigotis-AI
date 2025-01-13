from .fetcher import Handler
from .mapper import InvoiceMapper


class Pipeline:
    def __init__(self, auth_token):
        self.auth_token = auth_token

    def run_customer_segmentation(self):
        handler = Handler(self.auth_token)
        invoices = handler.get_client_invoices()

        customers = InvoiceMapper.map_invoices_to_customers(invoices)

        for customer in customers:
            print(str(customer))
