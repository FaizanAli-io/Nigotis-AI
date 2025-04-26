from enum import Enum
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from .pipeline.pipeline import Pipeline


class AnalysisChoice(str, Enum):
    customer_segmentation = "SEG"
    product_preference = "PRF"
    revenue_insights = "REV"
    purchase_value_analysis = "PUR"
    seasonal_trends = "TRE"
    client_lifetime_value = "CLV"
    churn_prediction = "CHP"
    most_purchased_products = "MPP"
    tailored_promotions = "TPR"


class AnalysisToolInput(BaseModel):
    token: str = Field(description="Authentication token")
    choice: AnalysisChoice = Field(description="Type of analysis to perform")


@tool("analysis_tool", args_schema=AnalysisToolInput, return_direct=True)
def analysis_tool(token: str, choice: AnalysisChoice) -> str:
    """Run a specific analysis like customer segmentation, revenue insights, churn prediction, etc."""
    pipe = Pipeline(token)
    return {
        "SEG": pipe.run_customer_segmentation,
        "PRF": pipe.run_product_preference,
        "REV": pipe.run_revenue_insights,
        "PUR": pipe.run_purchase_value,
        "TRE": pipe.run_seasonal_trends,
        "CLV": pipe.run_client_lifetime_value,
        "CHP": pipe.run_churn_prediction,
        "MPP": pipe.run_most_purchased_products,
        "TPR": pipe.run_tailored_promotions,
    }.get(choice.value, lambda: "Feature not implemented yet")()
