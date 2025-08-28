#!/usr/bin/env python3

import os
import logging
import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown
from dotenv import load_dotenv

from ecommerce_agent import EcommerceAnalysisAgent

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

console = Console()


class EcommerceCLI:
    def __init__(self):
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            console.print("[red]Error: GOOGLE_API_KEY environment variable not found[/red]")
            console.print("Please set your Google API key in a .env file or environment variable")
            return
        
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        
        try:
            self.agent = EcommerceAnalysisAgent(
                google_api_key=google_api_key,
                project_id=project_id
            )
            console.print("[green]✓ Agent initialized successfully[/green]")
        except Exception as e:
            console.print(f"[red]Error initializing agent: {e}[/red]")
    
    def display_welcome(self):
        welcome_text = """
        # E-commerce Data Analysis Agent
        
        Welcome to the BigQuery E-commerce Analysis Agent! 
        
        **Available Analysis Types:**
        - Customer segmentation and behavior analysis
        - Product performance and recommendation insights  
        - Sales trends and seasonality patterns
        - Geographic sales patterns
        - General data analysis and insights
        
        **Commands:**
        - Type your analysis question to get started
        - 'schema' - View table schemas
        - 'help' - Show this help message
        - 'quit' or 'exit' - Exit the application
        """
        
        console.print(Panel(Markdown(welcome_text), title="Welcome", border_style="blue"))
    
    def display_result(self, result):
        if not result.get("success"):
            console.print(f"[red]Analysis failed: {result.get('error', 'Unknown error')}[/red]")
            return
        
        # Display query information
        query_panel = Panel(
            f"Query: {result['user_query']}\nType: {result['analysis_type']}", 
            title="Analysis Request",
            border_style="yellow"
        )
        console.print(query_panel)
        
        # Display generated SQL
        if result.get("generated_sql"):
            sql_syntax = Syntax(result["generated_sql"], "sql", theme="monokai", line_numbers=True)
            console.print(Panel(sql_syntax, title="Generated SQL", border_style="cyan"))
        
        # Display query results summary
        if result.get("query_results"):
            self._display_query_results(result["query_results"])
        
        # Display insights
        if result.get("insights"):
            self._display_insights(result["insights"])
    
    def _display_query_results(self, results):
        # Results summary
        summary_text = f"""
        **Query Results Summary:**
        - Rows returned: {results.get('row_count', 0)}
        - Columns: {len(results.get('columns', []))}
        """
        
        if results.get("summary_stats"):
            summary_text += "\n**Summary Statistics:**\n"
            for col, stats in results["summary_stats"].items():
                summary_text += f"- {col}: min={stats.get('min')}, max={stats.get('max')}, avg={round(stats.get('mean', 0), 2)}\n"
        
        console.print(Panel(Markdown(summary_text), title="Query Results", border_style="green"))
        
        # Sample data table
        if results.get("data") and len(results["data"]) > 0:
            table = Table(title="Sample Data (First 5 Rows)")
            
            # Add columns
            for col in results["columns"][:8]:  # Limit to first 8 columns
                table.add_column(col, style="cyan")
            
            # Add rows
            for row in results["data"][:5]:
                table.add_row(*[str(row.get(col, ""))[:50] for col in results["columns"][:8]])
            
            console.print(table)
    
    def _display_insights(self, insights):
        insights_text = "\n".join([f"• {insight}" for insight in insights])
        console.print(Panel(insights_text, title="Business Insights", border_style="magenta"))
    
    def display_schema(self, table_name=None):
        if not self.agent:
            console.print("[red]Agent not initialized[/red]")
            return
        
        try:
            schemas = self.agent.get_schema_info(table_name)
            
            for table, schema_info in schemas.items():
                if isinstance(schema_info, list):
                    table_panel = Table(title=f"{table.upper()} Table Schema")
                    table_panel.add_column("Column", style="cyan")
                    table_panel.add_column("Type", style="green")
                    table_panel.add_column("Mode", style="yellow")
                    table_panel.add_column("Description", style="white")
                    
                    for field in schema_info:
                        table_panel.add_row(
                            field.get("name", ""),
                            field.get("type", ""),
                            field.get("mode", ""),
                            field.get("description", "")[:100]
                        )
                    
                    console.print(table_panel)
                    console.print()
                else:
                    console.print(f"[red]Error getting schema for {table}: {schema_info}[/red]")
                    
        except Exception as e:
            console.print(f"[red]Error displaying schema: {e}[/red]")
    
    def run_interactive_session(self):
        self.display_welcome()
        
        if not self.agent:
            console.print("[red]Cannot start session - agent not initialized[/red]")
            return
        
        while True:
            try:
                user_input = console.input("\n[bold blue]Ask your analysis question: [/bold blue]")
                
                if user_input.lower() in ['quit', 'exit']:
                    console.print("[green]Thank you for using the E-commerce Analysis Agent![/green]")
                    break
                
                elif user_input.lower() == 'help':
                    self.display_welcome()
                    continue
                
                elif user_input.lower().startswith('schema'):
                    table_name = user_input.split()[1] if len(user_input.split()) > 1 else None
                    self.display_schema(table_name)
                    continue
                
                elif not user_input.strip():
                    continue
                
                # Process the analysis request
                with console.status("[bold green]Analyzing your request..."):
                    result = self.agent.analyze(user_input)
                
                self.display_result(result)
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Session interrupted by user[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Unexpected error: {e}[/red]")
                logging.error(f"Unexpected error in CLI: {e}", exc_info=True)


@click.command()
@click.option('--query', '-q', help='Single query to analyze')
@click.option('--schema', '-s', help='Show schema for specific table')
@click.option('--interactive/--no-interactive', default=True, help='Run in interactive mode')
def main(query, schema, interactive):
    cli = EcommerceCLI()
    
    if schema:
        cli.display_schema(schema)
        return
    
    if query:
        if not cli.agent:
            return
        
        with console.status("[bold green]Analyzing your query..."):
            result = cli.agent.analyze(query)
        
        cli.display_result(result)
        return
    
    if interactive:
        cli.run_interactive_session()
    else:
        click.echo("Please provide a query with --query or use --interactive mode")


if __name__ == "__main__":
    main()