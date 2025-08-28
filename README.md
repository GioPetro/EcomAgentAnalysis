# E-commerce Data Analysis LangGraph Agent

A sophisticated LangGraph-based agent that analyzes e-commerce data from Google BigQuery's public dataset and generates actionable business insights.

## Features

- **Natural Language Queries**: Ask questions in plain English about e-commerce data
- **Dynamic SQL Generation**: Automatically generates optimized BigQuery SQL queries
- **Multi-type Analysis**: Supports customer segmentation, product performance, sales trends, and geographic patterns
- **Interactive CLI**: Rich terminal interface with colored output and formatted results
- **Error Handling**: Robust error handling with automatic retry mechanisms
- **Schema Intelligence**: Automatic table schema retrieval and context-aware query generation

## Architecture

The agent is built using LangGraph's state-based workflow with the following components:

1. **Query Understanding**: Analyzes user input to determine analysis type
2. **Schema Retrieval**: Fetches relevant table schemas from BigQuery
3. **SQL Generation**: Creates optimized SQL queries using Google Gemini LLM
4. **Query Execution**: Executes queries against BigQuery public dataset
5. **Insight Generation**: Generates actionable business insights from results

## Dataset

Uses BigQuery's public e-commerce dataset: `bigquery-public-data.thelook_ecommerce`

### Available Tables:
- **orders** - Customer order information and transaction data
- **order_items** - Individual items within orders with quantities and prices
- **products** - Product catalog with details and categories
- **users** - Customer demographics and profile information

## Setup Instructions

### Prerequisites

- Python 3.8+
- Google Cloud Project (for BigQuery access)
- Google API key (from Google AI Studio)

### 1. Environment Setup

```bash
# Clone/navigate to the project directory
cd bigqueryagentanalysis

# Install dependencies
pip install -r requirements.txt
```

### 2. Google Cloud Setup

#### BigQuery Access
1. Create a Google Cloud Project (if you don't have one)
2. Enable the BigQuery API
3. Set up authentication using one of these methods:

**Option A: Service Account (Recommended)**
```bash
# Create service account and download JSON key
gcloud auth application-default login
```

**Option B: Application Default Credentials**
```bash
gcloud auth application-default login
```

#### Google Gemini API
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create a new API key
3. Copy the API key for configuration

### 3. Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CLOUD_PROJECT=your_project_id_here
```

## Usage

### Interactive CLI Mode (Recommended)

```bash
python cli.py
```

This launches an interactive session where you can:
- Ask natural language questions about the e-commerce data
- View table schemas
- Get formatted results with insights

### Single Query Mode

```bash
python cli.py --query "What are the top selling products by revenue?"
```

### Schema Inspection

```bash
# View all table schemas
python cli.py --schema

# View specific table schema
python cli.py --schema orders
```

## Example Queries

### Customer Segmentation
- "Show me customer segments based on purchase behavior"
- "Who are the high-value customers and what do they buy?"
- "Analyze customer lifetime value by demographics"

### Product Performance
- "What are the top performing products by category?"
- "Which products have the highest profit margins?"
- "Show product recommendations based on purchase patterns"

### Sales Trends
- "Analyze monthly sales trends over the past year"
- "What are the seasonal patterns in our sales?"
- "Compare sales performance across different time periods"

### Geographic Analysis
- "Show sales distribution by geography"
- "Which regions have the highest customer acquisition?"
- "Analyze regional preferences for product categories"

## Project Structure

```
bigqueryagentanalysis/
├── agent_state.py          # State definitions for LangGraph
├── agent_nodes.py          # Node implementations for the workflow
├── ecommerce_agent.py      # Main agent class and graph assembly
├── bq_client.py           # BigQuery client wrapper
├── cli.py                 # Command-line interface
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration template
└── README.md             # This file
```

## Technical Details

### LangGraph Implementation

The agent uses LangGraph's state-based architecture with:

- **State Management**: Tracks conversation history, query results, and error states
- **Node-based Processing**: Each step (query understanding, SQL generation, etc.) is a separate node
- **Conditional Edges**: Smart routing based on success/failure conditions
- **Error Handling**: Automatic retry logic with fallback strategies

### Key Components

1. **EcommerceAnalysisState**: TypedDict defining the agent's state structure
2. **EcommerceAgentNodes**: Individual processing nodes for each workflow step
3. **EcommerceAnalysisAgent**: Main orchestrator that assembles and runs the graph
4. **BigQueryRunner**: Wrapper for BigQuery operations with error handling

### Error Handling Strategy

- **Retry Logic**: Up to 3 attempts for failed operations
- **Fallback Queries**: Simplified queries when complex ones fail
- **Graceful Degradation**: Partial results when full analysis isn't possible
- **User Feedback**: Clear error messages and suggestions

## Limitations

- **Rate Limits**: Subject to Google Gemini API rate limits
- **Query Complexity**: Very complex queries may timeout or fail
- **Data Size**: Results are limited to reasonable sizes for display
- **Read-Only**: Only SELECT queries are supported for security

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify GOOGLE_API_KEY is set correctly
   - Ensure BigQuery permissions are configured
   - Try `gcloud auth application-default login`

2. **SQL Generation Issues**
   - Check that table schemas are accessible
   - Verify dataset permissions
   - Simplify your query and try again

3. **Performance Issues**
   - Large result sets may take time to process
   - Consider more specific queries to reduce data volume

### Debug Mode

Set environment variable for detailed logging:
```bash
export LOG_LEVEL=DEBUG
python cli.py
```

## Contributing

This is a technical assignment implementation. For production use, consider:

- Adding more sophisticated error handling
- Implementing query result caching
- Adding data visualization capabilities
- Enhanced security measures
- Performance optimizations

## License

This project is for educational and assessment purposes.