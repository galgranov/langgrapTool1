"""
LangGraph agent that researches companies using stock tickers.
Includes company profile, stock prices, financial metrics, and news.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from company_tools import (
    get_company_info_tool,
    get_stock_price_tool,
    get_financial_metrics_tool,
    get_company_news_tool
)


class CompanyAgentState(TypedDict):
    """State for the company research agent."""
    ticker: str
    company_info: dict
    stock_price: dict
    financial_metrics: dict
    company_news: dict
    error: str


def get_ticker_input(state: CompanyAgentState) -> CompanyAgentState:
    """Get stock ticker from user."""
    print("\n" + "="*60)
    print("📈 COMPANY RESEARCH AGENT")
    print("="*60)
    ticker = input("\nEnter a stock ticker (e.g., AAPL, GOOGL, TSLA): ").strip()
    
    if not ticker:
        return {**state, "error": "No ticker provided"}
    
    print(f"\n🔎 Researching {ticker.upper()}...")
    return {**state, "ticker": ticker.upper(), "error": ""}


def fetch_company_info(state: CompanyAgentState) -> CompanyAgentState:
    """Fetch company profile information."""
    ticker = state.get("ticker", "")
    
    print("  🏢 Fetching company profile...")
    result = get_company_info_tool.invoke({"ticker": ticker})
    
    return {**state, "company_info": result}


def fetch_stock_price(state: CompanyAgentState) -> CompanyAgentState:
    """Fetch current stock price and trading data."""
    ticker = state.get("ticker", "")
    
    print("  💰 Fetching stock price data...")
    result = get_stock_price_tool.invoke({"ticker": ticker})
    
    return {**state, "stock_price": result}


def fetch_financial_metrics(state: CompanyAgentState) -> CompanyAgentState:
    """Fetch financial metrics and ratios."""
    ticker = state.get("ticker", "")
    
    print("  📊 Fetching financial metrics...")
    result = get_financial_metrics_tool.invoke({"ticker": ticker})
    
    return {**state, "financial_metrics": result}


def fetch_company_news(state: CompanyAgentState) -> CompanyAgentState:
    """Fetch company news."""
    ticker = state.get("ticker", "")
    
    print("  📰 Searching for news...")
    result = get_company_news_tool.invoke({"ticker": ticker})
    
    return {**state, "company_news": result}


def display_results(state: CompanyAgentState) -> CompanyAgentState:
    """Display all collected information."""
    print("\n" + "="*60)
    print("📋 RESEARCH RESULTS")
    print("="*60)
    
    if state.get("error"):
        print(f"\n❌ Error: {state['error']}")
        return state
    
    # Display company info
    company_info = state.get("company_info", {})
    if company_info.get("success"):
        data = company_info["data"]
        print("\n🏢 COMPANY PROFILE:")
        print(f"  Ticker: {data.get('ticker', 'N/A')}")
        print(f"  Name: {data.get('name', 'N/A')}")
        print(f"  Sector: {data.get('sector', 'N/A')}")
        print(f"  Industry: {data.get('industry', 'N/A')}")
        print(f"  Market Cap: {data.get('market_cap', 'N/A')}")
        print(f"  Employees: {data.get('employees', 'N/A'):,}" if isinstance(data.get('employees'), int) else f"  Employees: {data.get('employees', 'N/A')}")
        print(f"  Headquarters: {data.get('city', 'N/A')}, {data.get('state', 'N/A')}, {data.get('country', 'N/A')}")
        if data.get('website') and data['website'] != 'N/A':
            print(f"  Website: {data['website']}")
        
        if data.get('description') and data['description'] != 'N/A':
            desc = data['description']
            print(f"\n  Description:")
            print(f"  {desc[:300]}..." if len(desc) > 300 else f"  {desc}")
    else:
        print(f"\n🏢 COMPANY PROFILE:")
        print(f"  ⚠️  {company_info.get('error', 'No company information available')}")
    
    # Display stock price
    stock_price = state.get("stock_price", {})
    if stock_price.get("success"):
        data = stock_price["data"]
        print("\n💰 STOCK PRICE:")
        print(f"  Current Price: {data.get('currency', '')} {data.get('current_price', 'N/A')}")
        print(f"  Market State: {data.get('market_state', 'N/A')}")
        
        if data.get('change') != 'N/A' and data.get('change_percent') != 'N/A':
            change_symbol = "🔺" if data['change'] > 0 else "🔻" if data['change'] < 0 else "▬"
            print(f"  Change: {change_symbol} {data['change']:.2f} ({data['change_percent']:.2f}%)")
        
        print(f"  Previous Close: {data.get('previous_close', 'N/A')}")
        print(f"  Day Range: {data.get('day_low', 'N/A')} - {data.get('day_high', 'N/A')}")
        
        volume = data.get('volume', 'N/A')
        if volume != 'N/A':
            print(f"  Volume: {volume:,}")
    else:
        print(f"\n💰 STOCK PRICE:")
        print(f"  ⚠️  {stock_price.get('error', 'No price data available')}")
    
    # Display financial metrics
    financial_metrics = state.get("financial_metrics", {})
    if financial_metrics.get("success"):
        data = financial_metrics["data"]
        print("\n📊 FINANCIAL METRICS:")
        print(f"  P/E Ratio (TTM): {data.get('pe_ratio', 'N/A')}")
        print(f"  Forward P/E: {data.get('forward_pe', 'N/A')}")
        print(f"  PEG Ratio: {data.get('peg_ratio', 'N/A')}")
        print(f"  Price/Book: {data.get('price_to_book', 'N/A')}")
        print(f"  Dividend Yield: {data.get('dividend_yield', 'N/A')}")
        
        print(f"\n  Performance Metrics:")
        print(f"    Profit Margin: {data.get('profit_margin', 'N/A')}")
        print(f"    Revenue Growth: {data.get('revenue_growth', 'N/A')}")
        print(f"    Return on Equity: {data.get('roe', 'N/A')}")
        print(f"    Debt/Equity: {data.get('debt_to_equity', 'N/A')}")
        
        print(f"\n  52-Week Range:")
        print(f"    High: {data.get('52week_high', 'N/A')}")
        print(f"    Low: {data.get('52week_low', 'N/A')}")
    else:
        print(f"\n📊 FINANCIAL METRICS:")
        print(f"  ⚠️  {financial_metrics.get('error', 'No financial metrics available')}")
    
    # Display news
    company_news = state.get("company_news", {})
    if company_news.get("success"):
        data = company_news["data"]
        print("\n📰 NEWS & MEDIA:")
        if data.get('note'):
            print(f"  ℹ️  {data['note']}")
        if data.get('search_link'):
            print(f"  🔗 Search Link: {data['search_link']}")
    else:
        print(f"\n📰 NEWS & MEDIA:")
        print(f"  ⚠️  {company_news.get('error', 'No news available')}")
    
    print("\n" + "="*60)
    
    return state


def create_agent():
    """Create and return the company research agent."""
    # Create the graph
    graph = StateGraph(CompanyAgentState)
    
    # Add nodes for each step
    graph.add_node("get_input", get_ticker_input)
    graph.add_node("fetch_company_info", fetch_company_info)
    graph.add_node("fetch_stock_price", fetch_stock_price)
    graph.add_node("fetch_financial_metrics", fetch_financial_metrics)
    graph.add_node("fetch_company_news", fetch_company_news)
    graph.add_node("display_results", display_results)
    
    # Add edges to define the flow
    graph.add_edge(START, "get_input")
    graph.add_edge("get_input", "fetch_company_info")
    graph.add_edge("fetch_company_info", "fetch_stock_price")
    graph.add_edge("fetch_stock_price", "fetch_financial_metrics")
    graph.add_edge("fetch_financial_metrics", "fetch_company_news")
    graph.add_edge("fetch_company_news", "display_results")
    graph.add_edge("display_results", END)
    
    # Compile the graph
    return graph.compile()


def main():
    """Run the company research agent."""
    agent = create_agent()
    
    # Run the agent
    result = agent.invoke({
        "ticker": "",
        "company_info": {},
        "stock_price": {},
        "financial_metrics": {},
        "company_news": {},
        "error": ""
    })
    
    print("\n✅ Research completed!")


if __name__ == "__main__":
    main()
