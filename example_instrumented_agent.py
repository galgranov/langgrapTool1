"""
Example: Instrumented Agent with Datadog Monitoring
This file demonstrates how to add comprehensive monitoring to your agents.
"""
import time
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# Import Datadog utilities
from datadog_tracing import trace_agent, TraceSpan
from datadog_metrics import track_agent_execution, track_company_analyzed
from datadog_logger import get_logger, log_agent_start, log_agent_end

# Import tools (already instrumented)
from company_tools import get_company_info_tool, get_stock_price_tool


class AgentState(TypedDict):
    """State for the example agent."""
    ticker: str
    company_info: dict
    stock_price: dict
    result: str


# Initialize logger with agent name
logger = get_logger(__name__, agent_name="example_agent")


# Example 1: Instrument individual functions with decorators
@trace_agent("example_agent")
def get_input(state: AgentState) -> AgentState:
    """Get ticker input from user."""
    log_agent_start(logger, "example_agent", step="get_input")
    
    ticker = input("\nEnter a stock ticker (e.g., AAPL): ").strip().upper()
    logger.info(f"User input received", extra={"ticker": ticker})
    
    return {**state, "ticker": ticker}


def fetch_data(state: AgentState) -> AgentState:
    """Fetch company data with manual instrumentation."""
    ticker = state.get("ticker", "")
    
    # Manual tracing using context manager
    with TraceSpan("fetch_company_data", span_type="agent") as span:
        span.set_tag("ticker", ticker)
        
        logger.info(f"Fetching data for {ticker}")
        
        # These tools are already instrumented!
        company_info = get_company_info_tool.invoke({"ticker": ticker})
        stock_price = get_stock_price_tool.invoke({"ticker": ticker})
        
        # Track business metric
        if company_info.get("success"):
            track_company_analyzed(ticker)
        
        return {
            **state,
            "company_info": company_info,
            "stock_price": stock_price
        }


def display_results(state: AgentState) -> AgentState:
    """Display results with logging."""
    logger.info("Displaying results")
    
    print("\n" + "="*60)
    print("📊 COMPANY ANALYSIS RESULTS")
    print("="*60)
    
    company_info = state.get("company_info", {})
    if company_info.get("success"):
        data = company_info["data"]
        print(f"\n🏢 {data.get('name', 'N/A')}")
        print(f"   Ticker: {data.get('ticker', 'N/A')}")
        print(f"   Sector: {data.get('sector', 'N/A')}")
        print(f"   Market Cap: {data.get('market_cap', 'N/A')}")
    
    stock_price = state.get("stock_price", {})
    if stock_price.get("success"):
        data = stock_price["data"]
        print(f"\n💰 Current Price: {data.get('currency', '')} {data.get('current_price', 'N/A')}")
    
    print("="*60 + "\n")
    
    log_agent_end(logger, "example_agent", success=True)
    
    return {**state, "result": "success"}


def create_agent():
    """Create the instrumented agent."""
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("get_input", get_input)
    graph.add_node("fetch_data", fetch_data)
    graph.add_node("display_results", display_results)
    
    # Add edges
    graph.add_edge(START, "get_input")
    graph.add_edge("get_input", "fetch_data")
    graph.add_edge("fetch_data", "display_results")
    graph.add_edge("display_results", END)
    
    return graph.compile()


def main():
    """Run the instrumented agent."""
    print("\n" + "="*60)
    print("🔬 EXAMPLE: Instrumented Agent with Datadog")
    print("="*60)
    print("\nThis agent demonstrates comprehensive monitoring:")
    print("  ✅ Distributed tracing")
    print("  ✅ Custom metrics")
    print("  ✅ Structured logging")
    print("  ✅ Business metrics")
    print("="*60)
    
    # Track overall execution
    start_time = time.time()
    success = False
    
    try:
        agent = create_agent()
        
        # Run agent
        result = agent.invoke({
            "ticker": "",
            "company_info": {},
            "stock_price": {},
            "result": ""
        })
        
        success = True
        print("\n✅ Agent execution completed successfully!")
        
    except Exception as e:
        logger.error(f"Agent execution failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        raise
        
    finally:
        duration = time.time() - start_time
        track_agent_execution("example_agent", success=success, duration=duration)
        
        print(f"\n📊 Execution time: {duration:.2f}s")
        print("\n💡 Check your Datadog dashboard for:")
        print("   • APM traces in the 'APM' section")
        print("   • Custom metrics in 'Metrics Explorer'")
        print("   • Logs in the 'Logs' section")
        print("="*60 + "\n")


if __name__ == "__main__":
    main()
