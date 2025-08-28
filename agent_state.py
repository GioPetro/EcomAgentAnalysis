from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage


class EcommerceAnalysisState(TypedDict):
    messages: List[BaseMessage]
    user_query: str
    analysis_type: Optional[str]
    table_schemas: Dict[str, List[Dict[str, Any]]]
    generated_sql: str
    query_results: Optional[Dict[str, Any]]
    insights: List[str]
    error_count: int
    last_error: Optional[str]
    completed: bool


ECOMMERCE_TABLES = {
    "orders": "Customer order information and transaction data",
    "order_items": "Individual items within orders with quantities and prices", 
    "products": "Product catalog with details and categories",
    "users": "Customer demographics and profile information"
}

ANALYSIS_TYPES = {
    "customer_segmentation": "Customer segmentation and behavior analysis",
    "product_performance": "Product performance and recommendation insights", 
    "sales_trends": "Sales trends and seasonality patterns",
    "geographic_patterns": "Geographic sales patterns and regional analysis",
    "general": "General data analysis and insights"
}