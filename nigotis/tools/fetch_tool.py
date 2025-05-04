import requests
from typing import Optional
from dateutil.parser import isoparse
from pydantic import BaseModel, Field
from langchain_core.tools import tool

from .pipeline.mapper import Mapper
from .helpers import EntityEnum


ENTITY_DATE_FIELD_MAP = {
    "customers": "joinDate",
    "products": "issueDate",
    "invoices": "issueDate",
    "expenses": "from",
    "incomes": "date",
    "assets": "date",
    "payrolls": None,
}


class FetchToolInput(BaseModel):
    token: str = Field(description="Authentication token")
    entity: EntityEnum = Field(description="Entity to fetch")
    start_date: Optional[str] = Field(
        default=None, description="Filter results from this ISO date (YYYY-MM-DD)"
    )
    end_date: Optional[str] = Field(
        default=None, description="Filter results up to this ISO date (YYYY-MM-DD)"
    )


@tool("fetch_tool", args_schema=FetchToolInput)
def fetch_tool(
    token: str,
    entity: EntityEnum,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict:
    """Fetch data for a given entity like customers, products, invoices, etc., optionally filtering by date range."""
    mapper = Mapper(token)
    method_name = f"get_{entity.value}"

    if not hasattr(mapper, method_name):
        return {"error": f"Method for {entity} not implemented in Mapper class."}

    try:
        data = getattr(mapper, method_name)()
        date_field = ENTITY_DATE_FIELD_MAP.get(entity.value)

        if date_field and (start_date or end_date):
            try:
                start = isoparse(start_date) if start_date else None
                end = isoparse(end_date) if end_date else None

                def in_range(item):
                    date_str = item.get(date_field)
                    if not date_str:
                        return False
                    try:
                        item_date = isoparse(date_str)
                        return (not start or item_date >= start) and (
                            not end or item_date <= end
                        )
                    except ValueError:
                        return False

                data = [item for item in data if in_range(item)]

            except ValueError as ve:
                return {"error": f"Invalid date format: {ve}"}

        return {"data": data}

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
