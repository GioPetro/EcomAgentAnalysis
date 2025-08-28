# E-commerce Data Analysis LangGraph Agent

A LangGraph-based agent that analyzes e-commerce data from Google BigQuery's public dataset and generates business insights from natural language queries.

## Setup

1. **Install dependencies:**
   '''bash
   pip install -r requirements.txt
   '''

2. **Get Google API key:**
   - Go to [Google AI Studio](https://aistudio.google.com/)
   - Create a new API key

3. **Set up BigQuery access:**
   '''bash
   gcloud auth application-default login
   '''

4. **Create '.env' file:**
   '''bash
   cp .env.example .env
   '''
   
   Edit '.env' with your API key:
   '''env
   GOOGLE_API_KEY=your_google_api_key_here
   '''

## Usage

**Interactive mode:**
'''bash
python cli.py
'''

**Single query:**
'''bash
python cli.py --query "What are the top selling products?"
'''

**View schemas:**
'''bash
python cli.py --schema
'''

## Example Questions

- "Show me the top 10 products by revenue"
- "What are the customer segments by purchase behavior?"
- "Analyze sales trends by month"
- "Which regions have the highest sales?"

## Files

- 'cli.py' - Main CLI interface
- 'ecommerce_agent.py' - LangGraph agent
- 'agent_state.py' - State definition for graph
- 'agent_nodes.py' - Workflow nodes
- 'bq_client.py' - BigQuery client


## License
This is for assessment purposes only. This cannot be used commercially.