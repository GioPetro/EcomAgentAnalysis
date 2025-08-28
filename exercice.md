AI Technical Assignment, Option B - Data Analysis LangGraph Agent

The Challenge: Build a Data Analysis LangGraph Agent

Your task is to build a custom agent using the LangGraph framework that processes e-commerce data and derives meaningful business insights. This is a hands-on challenge to assess your technical skills and your ability to work with modern AI tools and real-world data.

Requirements:

1. Go to the LangGraph documentation and familiarize yourself with the Python library.
2. Build an agent that analyzes e-commerce data from Google BigQuery's public dataset and generates actionable business insights.

Dataset Specification:

* Dataset: bigquery-public-data.thelook_ecommerce
* Required Tables:
    * orders - Customer order information
    * order_items - Individual items within orders
    * products - Product catalog and details
    * users - Customer demographics and information

Expected Agent Capabilities:

Your agent should be able to perform complex data analysis and generate insights such as:

* Customer segmentation and behavior analysis
* Product performance and recommendation insights
* Sales trends and seasonality patterns
* Geographic sales patterns

1. Use BigQuery integration to query and analyze the specified tables. Your agent should be able to construct and execute SQL queries dynamically based on the analysis requirements.
2. You should preferably use one of the newer Google Gemini models. You can get a free API key from Google AI Studio. Please be mindful of the rate limits. Alternatively, you can use AWS Bedrock if you prefer.
3. Do not use pre-built agents. The goal is to build the agent logic yourself using LangGraph's state management and graph-based approach.

Setup Instructions

Environment Setup

1. Install Python dependencies:

pip install -r requirements.txt

GCP/BigQuery Setup

1. Set up BigQuery access by following the BigQuery Client Libraries documentation if you don't already have BigQuery access configured.
2. Free Tier: Google Cloud provides 1TB of free BigQuery compute per month, which is more than sufficient for this challenge.
3. Authentication: Ensure your environment is authenticated with Google Cloud to access the public datasets.


Deliverables

1. Working Application

* CLI-based interface for chat interactions.
* Google Gemini / AWS Bedrock integration as the LLM backend.

2. Architecture Documentation

* High-level architecture diagram showing Agent’s components and their interactions.
* Brief technical explanation covering:
    * Reasoning for chosen Cloud services and LLM models.
    * Data flow between components (if there are few of them).
    * Error handling and fallback strategies.

Time Expectation

We expect this assignment to take between 4 to 8 hours of work.

Submission

Share (make it public or invite us with our emails) with us a your Git repository (GitHub, GitLab, etc) with:

* Source code
* Documentation
* Architecture diagram

