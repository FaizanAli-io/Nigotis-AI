import requests

from enum import Enum

from utils import functions as F

BASE_URL = "https://nigotis-be.vercel.app/api/v1"


class EntityEnum(str, Enum):
    customers = "customers"
    products = "products"
    invoices = "invoices"
    expenses = "expenses"
    incomes = "incomes"
    assets = "assets"
    payrolls = "payrolls"


def get_client_name_id_map(token: str) -> dict[str, str] | str:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    res = requests.get(f"{BASE_URL}/client", headers=headers)
    clients = res.json().get("data", [])
    if not clients:
        return "⚠ No clients found."
    name_id_map = {}
    for client in clients:
        full_name = F.extract_name(client)
        name_id_map[full_name.lower()] = client["_id"]
    return name_id_map


def get_product_name_id_map(token: str) -> dict[str, str] | str:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    res = requests.get(f"{BASE_URL}/product", headers=headers)
    products = res.json().get("data", [])
    if not products:
        return "⚠ No products found."
    name_id_map = {}
    for product in products:
        name_id_map[product["name"].lower()] = product["_id"]
    return name_id_map


def resolve_client_name(token: str, name: str) -> str:
    mapping = get_client_name_id_map(token)
    if isinstance(mapping, str):
        return mapping
    name_key = name.lower()
    if name_key not in mapping:
        return f"⚠ Client must be one of: {', '.join(mapping.keys())}"
    return mapping[name_key]


def resolve_product_name(token: str, name: str) -> str:
    mapping = get_product_name_id_map(token)
    if isinstance(mapping, str):
        return mapping
    name_key = name.lower()
    if name_key not in mapping:
        return f"⚠ Product must be one of: {', '.join(mapping.keys())}"
    return mapping[name_key]
