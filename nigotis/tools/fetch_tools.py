import requests
from enum import Enum
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from .pipeline.mapper import Mapper


class EntityEnum(str, Enum):
    customers = "customers"
    products = "products"
    invoices = "invoices"
    expenses = "expenses"
    incomes = "incomes"
    assets = "assets"
    payrolls = "payrolls"


class FetchToolInput(BaseModel):
    token: str = Field(description="Authentication token")
    entity: EntityEnum = Field(description="Entity to fetch")


@tool("fetch_tool", args_schema=FetchToolInput)
def fetch_tool(token: str, entity: EntityEnum) -> dict:
    """Fetch data for a given entity like customers, products, invoices, etc."""
    mapper = Mapper(token)

    method_name = f"get_{entity.value}"
    if hasattr(mapper, method_name):
        try:
            return getattr(mapper, method_name)()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    else:
        return {"error": f"Method for {entity} not implemented in Mapper class."}
