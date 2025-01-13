import requests


class Handler:
    def __init__(self, auth_token):
        self.auth_token = auth_token

    def _make_request(self, url):
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json().get("data", None)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def get_products(self):
        url = "https://nigotis-be.vercel.app/api/v1/product"
        return self._make_request(url)

    def get_clients(self):
        url = "https://nigotis-be.vercel.app/api/v1/client"
        return self._make_request(url)

    def get_client_invoices(self):
        url = "https://nigotis-be.vercel.app/api/v1/client/invoice"
        return self._make_request(url)
