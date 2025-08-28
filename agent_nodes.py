import logging
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from agent_state import EcommerceAnalysisState, ANALYSIS_TYPES, ECOMMERCE_TABLES
from bq_client import BigQueryRunner

logger = logging.getLogger(__name__)


class EcommerceAgentNodes:
    def __init__(self, bq_client: BigQueryRunner, llm: ChatGoogleGenerativeAI):
        self.bq_client = bq_client
        self.llm = llm
        
    def understand_query_node(self, state: EcommerceAnalysisState) -> EcommerceAnalysisState:
        user_message = state["messages"][-1].content if state["messages"] else ""
        state["user_query"] = user_message
        
        analysis_prompt = f"""
        Analyze this user query and determine the type of e-commerce analysis requested:
        
        Query: {user_message}
        
        Available analysis types:
        {', '.join(ANALYSIS_TYPES.keys())}
        
        Return only the analysis type that best matches, or 'general' if unclear.
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
            analysis_type = response.content.strip().lower()
            
            if analysis_type not in ANALYSIS_TYPES:
                analysis_type = "general"
                
            state["analysis_type"] = analysis_type
            logger.info(f"Identified analysis type: {analysis_type}")
            
        except Exception as e:
            logger.error(f"Error in understand_query_node: {e}")
            state["analysis_type"] = "general"
            state["last_error"] = str(e)
            state["error_count"] += 1
            
        return state
    
    def retrieve_schema_node(self, state: EcommerceAnalysisState) -> EcommerceAnalysisState:
        try:
            schemas = {}
            for table_name in ECOMMERCE_TABLES.keys():
                try:
                    schema_info = self.bq_client.get_table_schema(table_name)
                    schemas[table_name] = schema_info
                    logger.info(f"Retrieved schema for {table_name}")
                except Exception as e:
                    logger.warning(f"Could not retrieve schema for {table_name}: {e}")
                    
            state["table_schemas"] = schemas
            
        except Exception as e:
            logger.error(f"Error in retrieve_schema_node: {e}")
            state["last_error"] = str(e)
            state["error_count"] += 1
            
        return state
    
    def generate_sql_node(self, state: EcommerceAnalysisState) -> EcommerceAnalysisState:
        try:
            schema_context = self._format_schema_context(state["table_schemas"])
            
            sql_prompt = f"""
            Generate a BigQuery SQL query for the following e-commerce analysis request:
            
            User Query: {state["user_query"]}
            Analysis Type: {state["analysis_type"]}
            
            Available Tables and Schemas:
            {schema_context}
            
            Requirements:
            - Use only SELECT statements
            - Include meaningful column aliases
            - Add appropriate WHERE clauses to filter data
            - Limit results to reasonable numbers (e.g., LIMIT 100 for detailed data)
            - Use proper JOIN syntax when needed
            - Focus on actionable business insights
            - Only use tables: orders, order_items, products, users from bigquery-public-data.thelook_ecommerce
            
            Return only the SQL query without explanations.
            """
            
            response = self.llm.invoke([HumanMessage(content=sql_prompt)])
            sql_query = response.content.strip()
            
            # Clean up the SQL query
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
                
            state["generated_sql"] = sql_query.strip()
            logger.info("Generated SQL query successfully")
            
        except Exception as e:
            logger.error(f"Error in generate_sql_node: {e}")
            state["last_error"] = str(e)
            state["error_count"] += 1
            
        return state
    
    def execute_query_node(self, state: EcommerceAnalysisState) -> EcommerceAnalysisState:
        try:
            if not state["generated_sql"]:
                raise ValueError("No SQL query to execute")
                
            df = self.bq_client.execute_query(state["generated_sql"])
            
            # Convert results to a serializable format
            query_results = {
                "row_count": len(df),
                "columns": df.columns.tolist(),
                "data": df.to_dict('records')[:50],  # Limit to first 50 rows
                "summary_stats": {}
            }
            
            # Add basic summary statistics for numeric columns
            numeric_columns = df.select_dtypes(include=['number']).columns
            for col in numeric_columns:
                if not df[col].empty:
                    query_results["summary_stats"][col] = {
                        "mean": float(df[col].mean()) if not df[col].isna().all() else None,
                        "min": float(df[col].min()) if not df[col].isna().all() else None,
                        "max": float(df[col].max()) if not df[col].isna().all() else None
                    }
            
            state["query_results"] = query_results
            logger.info(f"Query executed successfully, returned {len(df)} rows")
            
        except Exception as e:
            logger.error(f"Error in execute_query_node: {e}")
            state["last_error"] = str(e)
            state["error_count"] += 1
            
        return state
    
    def generate_insights_node(self, state: EcommerceAnalysisState) -> EcommerceAnalysisState:
        try:
            if not state["query_results"]:
                raise ValueError("No query results to analyze")
                
            results_summary = self._format_results_summary(state["query_results"])
            
            insights_prompt = f"""
            Analyze the following BigQuery results and generate actionable business insights:
            
            Original Query: {state["user_query"]}
            Analysis Type: {state["analysis_type"]}
            SQL Query: {state["generated_sql"]}
            
            Query Results Summary:
            {results_summary}
            
            Generate 3-5 key business insights focusing on:
            - Trends and patterns identified
            - Business implications
            - Actionable recommendations
            - Data-driven conclusions
            
            Format as bullet points, each insight should be concise and actionable.
            """
            
            response = self.llm.invoke([HumanMessage(content=insights_prompt)])
            insights_text = response.content.strip()
            
            # Parse insights into list
            insights = [line.strip() for line in insights_text.split('\n') 
                       if line.strip() and (line.strip().startswith('•') or line.strip().startswith('-'))]
            
            if not insights:
                insights = [insights_text]
                
            state["insights"] = insights
            state["completed"] = True
            
            # Add AI response to messages
            state["messages"].append(AIMessage(content=f"Analysis completed. Generated insights: {'; '.join(insights)}"))
            
            logger.info(f"Generated {len(insights)} insights")
            
        except Exception as e:
            logger.error(f"Error in generate_insights_node: {e}")
            state["last_error"] = str(e)
            state["error_count"] += 1
            
        return state
    
    def error_handler_node(self, state: EcommerceAnalysisState) -> EcommerceAnalysisState:
        error_msg = f"Error occurred: {state.get('last_error', 'Unknown error')}"
        
        if state["error_count"] >= 3:
            final_error = "Maximum retry attempts reached. Unable to complete analysis."
            state["messages"].append(AIMessage(content=final_error))
            state["completed"] = True
            logger.error(final_error)
        else:
            retry_msg = f"Attempting to retry analysis. Error count: {state['error_count']}"
            logger.info("Attempt: " + str(state["error_count"]) + " " + error_msg)
            state["messages"].append(AIMessage(content=retry_msg))
            logger.info(retry_msg)
            
        return state
    
    def _format_schema_context(self, schemas: Dict[str, Any]) -> str:
        context = []
        for table_name, schema_info in schemas.items():
            if schema_info:
                context.append(f"\n{table_name.upper()} table:")
                context.append(f"Description: {ECOMMERCE_TABLES.get(table_name, '')}")
                for field in schema_info[:10]:  # Limit to first 10 fields
                    context.append(f"  - {field['name']} ({field['type']}): {field.get('description', '')}")
        return '\n'.join(context)
    
    def _format_results_summary(self, results: Dict[str, Any]) -> str:
        summary = [
            f"Rows returned: {results['row_count']}",
            f"Columns: {', '.join(results['columns'])}",
        ]
        
        if results["summary_stats"]:
            summary.append("Summary statistics:")
            for col, stats in results["summary_stats"].items():
                summary.append(f"  {col}: min={stats.get('min')}, max={stats.get('max')}, avg={stats.get('mean')}")
        
        if results["data"]:
            summary.append(f"Sample data (first 3 rows): {results['data'][:3]}")
            
        return '\n'.join(summary)