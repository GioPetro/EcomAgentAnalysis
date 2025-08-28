# E-commerce Data Analysis Agent Architecture

## High-Level Architecture Overview

The BigQuery E-commerce Analysis Agent is built using LangGraph's state-based workflow architecture, integrating with Google Cloud services and providing a rich CLI interface for user interactions.

## System Components

### 1. User Interface Layer
- **CLI Interface** (`cli.py`)
  - Rich terminal interface with colored output
  - Interactive chat mode and single-query execution
  - Schema inspection capabilities
  - Result formatting and visualization

### 2. Agent Orchestration Layer
- **EcommerceAnalysisAgent** (`ecommerce_agent.py`)
  - Main system orchestrator
  - LangGraph workflow compilation and execution
  - State management coordination
  - Result aggregation and formatting

### 3. Workflow Processing Layer
- **Agent Nodes** (`agent_nodes.py`)
  - `understand_query_node`: Analyzes user intent and determines analysis type
  - `retrieve_schema_node`: Fetches relevant table schemas from BigQuery
  - `generate_sql_node`: Creates SQL queries using LLM with schema context
  - `execute_query_node`: Executes queries against BigQuery dataset
  - `generate_insights_node`: Generates business insights from query results
  - `error_handler_node`: Manages errors and retry logic

### 4. State Management
- **EcommerceAnalysisState** (`agent_state.py`)
  - Tracks conversation history and context
  - Maintains query generation and execution state
  - Manages error counts and retry mechanisms
  - Stores analysis results and insights

### 5. Data Access Layer
- **BigQueryRunner** (`bq_client.py`)
  - Abstracts BigQuery operations
  - Handles authentication and connection management
  - Provides schema introspection capabilities
  - Executes SQL queries with error handling

### 6. External Services
- **Google Gemini LLM**
  - Powers natural language understanding
  - Generates SQL queries from user intent
  - Creates business insights from data results
  
- **BigQuery Public Dataset**
  - `bigquery-public-data.thelook_ecommerce`
  - Contains orders, order_items, products, users tables
  - Provides rich e-commerce data for analysis

## Data Flow Architecture

```
[User Input] 
    ↓
[CLI Interface]
    ↓
[EcommerceAnalysisAgent]
    ↓
[LangGraph Workflow]
    ↓ ↓ ↓ ↓ ↓ ↓
[understand_query] → [retrieve_schema] → [generate_sql] → [execute_query] → [generate_insights] → [Results]
    ↓                      ↓                 ↓              ↓                 ↓
[Gemini LLM]        [BigQuery Client]   [Gemini LLM]   [BigQuery Client]   [Gemini LLM]
                         ↓                               ↓
                   [Schema Retrieval]              [Query Execution]
                         ↓                               ↓
                   [BigQuery Dataset]             [BigQuery Dataset]
```

## Workflow State Transitions

The agent follows a structured workflow with conditional routing:

1. **Entry Point**: `understand_query`
2. **Linear Flow**: `understand_query` → `retrieve_schema` → `generate_sql`
3. **Conditional Routing**: 
   - Success: `generate_sql` → `execute_query` → `generate_insights` → END
   - Error: Any node → `error_handler` → (retry or end based on error count)

## Error Handling Strategy

### Multi-Level Error Handling
- **Node-Level**: Each node handles its specific errors
- **Workflow-Level**: Conditional edges route to error handler
- **Retry Logic**: Up to 3 attempts before termination
- **Graceful Degradation**: Meaningful error messages to user

### Error Recovery Mechanisms
- **Query Refinement**: Retry SQL generation with error context
- **Schema Context Expansion**: Retrieve additional table information
- **Fallback Responses**: Provide partial results when possible
- **User Guidance**: Clear error messages with suggested actions

## Integration Patterns

### Google Gemini Integration
- **Context Management**: Provides schema information for SQL generation
- **Temperature Control**: Set to 0.1 for consistent, deterministic outputs
- **Prompt Engineering**: Structured prompts for reliable SQL generation
- **Response Parsing**: Clean and validate LLM responses

### BigQuery Integration
- **Authentication**: Supports multiple auth methods (service account, ADC)
- **Query Optimization**: Generates efficient queries with proper limits
- **Result Processing**: Converts results to structured formats
- **Schema Caching**: Retrieves and caches table schemas for context

## Security Considerations

### Data Security
- **Read-Only Access**: Only SELECT queries are permitted
- **Query Validation**: SQL injection prevention through structured prompts
- **Result Limiting**: Prevents excessive data retrieval
- **Authentication**: Secure credential management through environment variables

### API Security
- **Rate Limiting**: Respects Google Gemini API rate limits
- **Error Handling**: Prevents credential exposure in error messages
- **Input Validation**: Sanitizes user inputs before processing

## Performance Characteristics

### Optimization Features
- **Parallel Processing**: Independent operations run concurrently where possible
- **Streaming Responses**: Real-time feedback during processing
- **Result Caching**: Schema information cached across sessions
- **Query Optimization**: Generated queries include appropriate limits and filters

### Scalability Considerations
- **Stateless Design**: Each query execution is independent
- **Resource Management**: Memory-efficient result processing
- **Connection Pooling**: Efficient BigQuery connection management
- **Async Capabilities**: Supports background processing for long queries

## Monitoring and Observability

### Logging Strategy
- **Structured Logging**: Comprehensive logging at each workflow step
- **Error Tracking**: Detailed error capture and context preservation
- **Performance Metrics**: Query execution time and success rate tracking
- **Debug Support**: Configurable log levels for troubleshooting

### Health Monitoring
- **Service Health**: Connection status to external services
- **Query Success Rate**: Track successful vs failed queries
- **Error Patterns**: Identify common failure modes
- **Resource Usage**: Monitor memory and processing time

## Technology Stack

### Core Framework
- **LangGraph**: State-based workflow orchestration
- **LangChain**: LLM integration and prompt management
- **Python 3.8+**: Runtime environment

### External Services
- **Google Gemini 1.5 Pro**: Language model for SQL generation and insights
- **Google BigQuery**: Data warehouse and query engine
- **BigQuery Public Datasets**: E-commerce data source

### User Interface
- **Click**: Command-line interface framework
- **Rich**: Terminal formatting and visualization
- **Pandas**: Data processing and analysis

### Supporting Libraries
- **google-cloud-bigquery**: BigQuery client library
- **python-dotenv**: Environment configuration management
- **structlog**: Structured logging capabilities

## Deployment Considerations

### Environment Requirements
- Google Cloud credentials (service account or ADC)
- Google Gemini API key
- Network access to Google Cloud services
- Python environment with required dependencies

### Configuration Management
- Environment-based configuration (.env files)
- Flexible authentication methods
- Configurable logging levels
- Optional project-specific settings

This architecture provides a robust, scalable foundation for e-commerce data analysis while maintaining security, performance, and user experience as primary concerns.