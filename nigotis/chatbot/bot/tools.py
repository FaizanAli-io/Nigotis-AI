from datetime import datetime

ENTITIES = [
    "customers",
    "products",
    "invoices",
    "expenses",
    "incomes",
    "assets",
    "payrolls",
]


def fetch_data(mapper, entity):
    if entity not in ENTITIES:
        raise ValueError(f"Invalid entity: {entity}")
    return getattr(mapper, f"get_{entity}")()


def filter_by_date(
    data_array,
    date,
    filter_type="after",
    start_date=None,
    end_date=None,
):

    try:
        target_date = datetime.strptime(date, "%d-%m-%Y")
        if start_date:
            start_date = datetime.strptime(start_date, "%d-%m-%Y")
        if end_date:
            end_date = datetime.strptime(end_date, "%d-%m-%Y")
    except ValueError:
        return data_array  # Return the full array if date parsing fails

    def is_valid_item(item):
        item_date = item.get("date") or item.get("issueDate")
        if not item_date:
            return True  # No date properties, include item
        try:
            item_date_parsed = datetime.strptime(item_date, "%d-%m-%Y")

            # Check for filtering types: "after", "before", or within a range
            if filter_type == "after":
                return item_date_parsed >= target_date
            elif filter_type == "before":
                return item_date_parsed < target_date
            elif filter_type == "range" and start_date and end_date:
                return start_date <= item_date_parsed <= end_date
            else:
                return True  # If filter_type is invalid, include the item
        except ValueError:
            return True  # Include item if date parsing fails

    return [item for item in data_array if is_valid_item(item)]
