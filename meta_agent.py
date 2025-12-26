"""
MetaAgent - Orchestrates company and person research agents.
Gets a company ticker, researches the company, fetches top 10 executives,
and then researches each executive using the person agent.
"""
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, START, END
from company_tools import (
    get_company_info_tool,
    get_stock_price_tool,
    get_company_executives_tool
)
from person_tools import (
    get_person_info_tool,
    get_person_career_info_tool
)


class MetaAgentState(TypedDict):
    """State for the meta agent."""
    ticker: str
    company_info: dict
    stock_price: dict
    executives: dict
    executives_research: List[Dict[str, Any]]
    error: str


def get_ticker_input(state: MetaAgentState) -> MetaAgentState:
    """Get stock ticker from user."""
    print("\n" + "="*80)
    print("🎯 META AGENT - Company & Executive Research")
    print("="*80)
    ticker = input("\nEnter a stock ticker (e.g., AAPL, GOOGL, TSLA): ").strip()
    
    if not ticker:
        return {**state, "error": "No ticker provided"}
    
    print(f"\n🚀 Starting comprehensive research for {ticker.upper()}...")
    return {**state, "ticker": ticker.upper(), "error": ""}


def fetch_company_data(state: MetaAgentState) -> MetaAgentState:
    """Fetch company information and stock data."""
    ticker = state.get("ticker", "")
    
    print("\n" + "─"*80)
    print("📊 PHASE 1: COMPANY RESEARCH")
    print("─"*80)
    
    print("  🏢 Fetching company profile...")
    company_info = get_company_info_tool.invoke({"ticker": ticker})
    
    print("  💰 Fetching stock price data...")
    stock_price = get_stock_price_tool.invoke({"ticker": ticker})
    
    # Display company summary
    if company_info.get("success"):
        data = company_info["data"]
        print(f"\n  ✓ Company: {data.get('name', 'N/A')}")
        print(f"  ✓ Sector: {data.get('sector', 'N/A')}")
        print(f"  ✓ Employees: {data.get('employees', 'N/A'):,}" if isinstance(data.get('employees'), int) else f"  ✓ Employees: {data.get('employees', 'N/A')}")
    
    if stock_price.get("success"):
        data = stock_price["data"]
        print(f"  ✓ Current Price: {data.get('currency', '')} {data.get('current_price', 'N/A')}")
    
    return {
        **state,
        "company_info": company_info,
        "stock_price": stock_price
    }


def fetch_executives(state: MetaAgentState) -> MetaAgentState:
    """Fetch company executives."""
    ticker = state.get("ticker", "")
    
    print("\n  👥 Fetching company executives...")
    executives = get_company_executives_tool.invoke({"ticker": ticker})
    
    if executives.get("success"):
        count = executives["data"].get("count", 0)
        print(f"  ✓ Found {count} executives")
    else:
        print(f"  ⚠️  {executives.get('error', 'Could not fetch executives')}")
    
    return {**state, "executives": executives}


def research_executives(state: MetaAgentState) -> MetaAgentState:
    """Research each executive using person agent."""
    executives_data = state.get("executives", {})
    
    print("\n" + "─"*80)
    print("👤 PHASE 2: EXECUTIVE RESEARCH")
    print("─"*80)
    
    if not executives_data.get("success"):
        print("  ⚠️  No executives to research")
        return {**state, "executives_research": []}
    
    executives = executives_data["data"].get("executives", [])
    research_results = []
    
    for idx, exec_info in enumerate(executives, 1):
        name = exec_info.get("name", "N/A")
        title = exec_info.get("title", "N/A")
        
        print(f"\n  [{idx}/{len(executives)}] Researching: {name}")
        print(f"      Title: {title}")
        
        # Fetch person info
        person_info = get_person_info_tool.invoke({"person_name": name})
        career_info = get_person_career_info_tool.invoke({"person_name": name})
        
        research_result = {
            "executive_info": exec_info,
            "biographical_info": person_info,
            "career_info": career_info
        }
        
        research_results.append(research_result)
        
        # Display brief summary
        if person_info.get("success"):
            data = person_info["data"]
            print(f"      ✓ Found biographical data")
            if data.get('description'):
                print(f"      → {data['description'][:80]}...")
        else:
            print(f"      ⚠️  Limited biographical data available")
    
    return {**state, "executives_research": research_results}


def display_results(state: MetaAgentState) -> MetaAgentState:
    """Display all collected information in a comprehensive report."""
    print("\n" + "="*80)
    print("📋 COMPREHENSIVE RESEARCH REPORT")
    print("="*80)
    
    if state.get("error"):
        print(f"\n❌ Error: {state['error']}")
        return state
    
    # ============ COMPANY SECTION ============
    print("\n" + "┌" + "─"*78 + "┐")
    print("│" + " "*25 + "COMPANY OVERVIEW" + " "*37 + "│")
    print("└" + "─"*78 + "┘")
    
    company_info = state.get("company_info", {})
    if company_info.get("success"):
        data = company_info["data"]
        print(f"\n🏢 {data.get('name', 'N/A')}")
        print(f"   Ticker: {data.get('ticker', 'N/A')}")
        print(f"   Sector: {data.get('sector', 'N/A')} | Industry: {data.get('industry', 'N/A')}")
        print(f"   Market Cap: {data.get('market_cap', 'N/A')}")
        print(f"   Employees: {data.get('employees', 'N/A'):,}" if isinstance(data.get('employees'), int) else f"   Employees: {data.get('employees', 'N/A')}")
        print(f"   HQ: {data.get('city', 'N/A')}, {data.get('state', 'N/A')}, {data.get('country', 'N/A')}")
        if data.get('website') and data['website'] != 'N/A':
            print(f"   Website: {data['website']}")
    
    stock_price = state.get("stock_price", {})
    if stock_price.get("success"):
        data = stock_price["data"]
        print(f"\n💰 Stock Information:")
        print(f"   Current Price: {data.get('currency', '')} {data.get('current_price', 'N/A')}")
        
        if data.get('change') != 'N/A' and data.get('change_percent') != 'N/A':
            change_symbol = "📈" if data['change'] > 0 else "📉" if data['change'] < 0 else "▬"
            print(f"   Change: {change_symbol} {data['change']:.2f} ({data['change_percent']:.2f}%)")
        
        print(f"   Day Range: {data.get('day_low', 'N/A')} - {data.get('day_high', 'N/A')}")
    
    # ============ EXECUTIVES SECTION ============
    print("\n" + "┌" + "─"*78 + "┐")
    print("│" + " "*23 + "EXECUTIVE LEADERSHIP" + " "*35 + "│")
    print("└" + "─"*78 + "┘")
    
    executives_research = state.get("executives_research", [])
    
    if not executives_research:
        print("\n  ⚠️  No executive research data available")
    else:
        for idx, research in enumerate(executives_research, 1):
            exec_info = research.get("executive_info", {})
            bio_info = research.get("biographical_info", {})
            career_info = research.get("career_info", {})
            
            print(f"\n{'─'*80}")
            print(f"👤 EXECUTIVE #{idx}: {exec_info.get('name', 'N/A')}")
            print(f"{'─'*80}")
            
            # Executive role at company
            print(f"\n📌 Role at Company:")
            print(f"   Title: {exec_info.get('title', 'N/A')}")
            if exec_info.get('age') != 'N/A':
                print(f"   Age: {exec_info.get('age', 'N/A')}")
            if exec_info.get('total_pay') != 'N/A':
                print(f"   Compensation: {exec_info.get('total_pay', 'N/A')}")
            
            # Biographical information
            if bio_info.get("success"):
                bio_data = bio_info["data"]
                print(f"\n📖 Biographical Information:")
                if bio_data.get('description'):
                    print(f"   {bio_data['description']}")
                
                print(f"\n   Summary:")
                summary = bio_data.get('extract', 'N/A')
                # Limit summary to 300 characters
                if len(summary) > 300:
                    print(f"   {summary[:300]}...")
                else:
                    print(f"   {summary}")
                
                if bio_data.get('url'):
                    print(f"\n   📚 Wikipedia: {bio_data['url']}")
            else:
                print(f"\n📖 Biographical Information:")
                print(f"   ⚠️  {bio_info.get('error', 'No biographical information available')}")
            
            # Career information
            if career_info.get("success"):
                career_data = career_info["data"]
                
                if career_data.get('occupations'):
                    print(f"\n💼 Career & Occupations:")
                    for occupation in career_data['occupations'][:5]:  # Limit to 5
                        print(f"   • {occupation}")
                
                if career_data.get('awards'):
                    print(f"\n🏆 Awards & Recognition:")
                    for award in career_data['awards'][:3]:  # Limit to 3
                        print(f"   • {award}")
    
    print("\n" + "="*80)
    print("✅ Research Complete!")
    print("="*80)
    
    return state


def create_agent():
    """Create and return the meta agent."""
    # Create the graph
    graph = StateGraph(MetaAgentState)
    
    # Add nodes for each step
    graph.add_node("get_input", get_ticker_input)
    graph.add_node("fetch_company_data", fetch_company_data)
    graph.add_node("fetch_executives", fetch_executives)
    graph.add_node("research_executives", research_executives)
    graph.add_node("display_results", display_results)
    
    # Add edges to define the flow
    graph.add_edge(START, "get_input")
    graph.add_edge("get_input", "fetch_company_data")
    graph.add_edge("fetch_company_data", "fetch_executives")
    graph.add_edge("fetch_executives", "research_executives")
    graph.add_edge("research_executives", "display_results")
    graph.add_edge("display_results", END)
    
    # Compile the graph
    return graph.compile()


def main():
    """Run the meta agent."""
    agent = create_agent()
    
    # Run the agent
    result = agent.invoke({
        "ticker": "",
        "company_info": {},
        "stock_price": {},
        "executives": {},
        "executives_research": [],
        "error": ""
    })
    
    print("\n🎉 Meta agent execution completed!")


if __name__ == "__main__":
    main()
