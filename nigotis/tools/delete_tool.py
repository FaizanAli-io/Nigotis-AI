import requests
from pydantic import BaseModel, Field
from langchain_core.tools import tool

from .helpers import EntityEnum, BASE_URL


class DeleteToolInput(BaseModel):
    token: str = Field(description="Authentication token")
    entity: EntityEnum = Field(description="Entity to delete from")
    id: str = Field(description="The ID of the entity to delete")


ENTITY_DELETE_CONFIG = {
    EntityEnum.customers: ("/client", "clientId"),
    EntityEnum.products: ("/product", "productId"),
    EntityEnum.invoices: ("/client/invoice", "invoiceId"),
    EntityEnum.expenses: ("/company/expense", "expenseId"),
    EntityEnum.assets: ("/company/asset", "assetId"),
    EntityEnum.incomes: ("/income", "incomeId"),
    EntityEnum.payrolls: ("/user", "userId"),
}


@tool("delete_tool", args_schema=DeleteToolInput)
def delete_tool(token: str, entity: EntityEnum, id: str) -> str:
    """Delete a specific entity by its ID (with ID in request body)."""
    config = ENTITY_DELETE_CONFIG.get(entity)
    if not config:
        return f"⚠ Unsupported entity '{entity}'."

    endpoint, id_field = config
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    response = requests.delete(url, headers=headers, json={id_field: id})

    if response.status_code in [200, 204]:
        return f"{entity.value.capitalize()} with ID {id} deleted successfully."
    else:
        return f"❌ Failed to delete {entity.value} with ID {id}: {response.text}"
