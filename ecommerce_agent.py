import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from agent_state import EcommerceAnalysisState
from agent_nodes import EcommerceAgentNodes
from bq_client import BigQueryRunner

logger = logging.getLogger(__name__)


class EcommerceAnalysisAgent:
    def __init__(self, google_api_key: str, project_id: str = None):
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            google_api_key=google_api_key,
            temperature=0.1
        )
        
        # Initialize BigQuery client
        self.bq_client = BigQueryRunner(project_id=project_id)
        
        # Initialize agent nodes
        self.nodes = EcommerceAgentNodes(self.bq_client, self.llm)
        
        # Build the graph
        self.app = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(EcommerceAnalysisState)
        
        # Add nodes
        workflow.add_node("understand_query", self.nodes.understand_query_node)
        workflow.add_node("retrieve_schema", self.nodes.retrieve_schema_node)
        workflow.add_node("generate_sql", self.nodes.generate_sql_node)
        workflow.add_node("execute_query", self.nodes.execute_query_node)
        workflow.add_node("generate_insights", self.nodes.generate_insights_node)
        workflow.add_node("error_handler", self.nodes.error_handler_node)
        
        # Define the workflow edges
        workflow.set_entry_point("understand_query")
        
        # Linear flow with error handling
        workflow.add_edge("understand_query", "retrieve_schema")
        workflow.add_edge("retrieve_schema", "generate_sql")
        
        # Conditional edge from generate_sql
        workflow.add_conditional_edges(
            "generate_sql",
            self._should_execute_query,
            {
                "execute": "execute_query",
                "error": "error_handler"
            }
        )
        
        # Conditional edge from execute_query
        workflow.add_conditional_edges(
            "execute_query", 
            self._should_generate_insights,
            {
                "insights": "generate_insights",
                "error": "error_handler"
            }
        )
        
        # Conditional edge from error_handler
        workflow.add_conditional_edges(
            "error_handler",
            self._should_retry_or_end,
            {
                "retry": "generate_sql",
                "end": END
            }
        )
        
        # End the workflow after generating insights
        workflow.add_edge("generate_insights", END)
        
        return workflow.compile()
    
    def _should_execute_query(self, state: EcommerceAnalysisState) -> str:
        if state.get("last_error") or not state.get("generated_sql"):
            return "error"
        return "execute"
    
    def _should_generate_insights(self, state: EcommerceAnalysisState) -> str:
        if state.get("last_error") or not state.get("query_results"):
            return "error" 
        return "insights"
    
    def _should_retry_or_end(self, state: EcommerceAnalysisState) -> str:
        if state["error_count"] >= 3 or state.get("completed", False):
            return "end"
        return "retry"
    
    def analyze(self, user_query: str) -> Dict[str, Any]:
        initial_state = EcommerceAnalysisState(
            messages=[HumanMessage(content=user_query)],
            user_query=user_query,
            analysis_type=None,
            table_schemas={},
            generated_sql="",
            query_results=None,
            insights=[],
            error_count=0,
            last_error=None,
            completed=False
        )
        
        try:
            final_state = self.app.invoke(initial_state)
            
            return {
                "success": final_state.get("completed", False),
                "user_query": final_state.get("user_query", ""),
                "analysis_type": final_state.get("analysis_type", ""),
                "generated_sql": final_state.get("generated_sql", ""),
                "query_results": final_state.get("query_results", {}),
                "insights": final_state.get("insights", []),
                "error_count": final_state.get("error_count", 0),
                "last_error": final_state.get("last_error")
            }
            
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_query": user_query,
                "insights": [f"Analysis failed due to error: {str(e)}"]
            }
    
    def get_schema_info(self, table_name: str = None) -> Dict[str, Any]:
        if table_name:
            try:
                schema = self.bq_client.get_table_schema(table_name)
                return {table_name: schema}
            except Exception as e:
                logger.error(f"Error getting schema for {table_name}: {e}")
                return {"error": str(e)}
        else:
            # Return all table schemas
            from agent_state import ECOMMERCE_TABLES
            schemas = {}
            for table in ECOMMERCE_TABLES.keys():
                try:
                    schemas[table] = self.bq_client.get_table_schema(table)
                except Exception as e:
                    logger.warning(f"Could not get schema for {table}: {e}")
            return schemas