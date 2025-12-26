"""
LangGraph agent that researches people using multiple data sources.
Includes Wikipedia, Wikidata, and social media links.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from person_tools import (
    get_person_info_tool,
    search_person_news_tool,
    get_person_social_media_tool,
    get_person_career_info_tool
)


class PersonAgentState(TypedDict):
    """State for the person research agent."""
    person_name: str
    person_info: dict
    career_info: dict
    news_info: dict
    social_media: dict
    error: str


def get_person_input(state: PersonAgentState) -> PersonAgentState:
    """Get person name from user."""
    print("\n" + "="*60)
    print("👤 PERSON RESEARCH AGENT")
    print("="*60)
    person_name = input("\nEnter a person's name: ").strip()
    
    if not person_name:
        return {**state, "error": "No person name provided"}
    
    print(f"\n🔎 Researching {person_name}...")
    return {**state, "person_name": person_name, "error": ""}


def fetch_person_info(state: PersonAgentState) -> PersonAgentState:
    """Fetch person information using Wikipedia."""
    person_name = state.get("person_name", "")
    
    print("  📖 Fetching biographical information...")
    result = get_person_info_tool.invoke({"person_name": person_name})
    
    return {**state, "person_info": result}


def fetch_career_info(state: PersonAgentState) -> PersonAgentState:
    """Fetch career and professional information."""
    person_name = state.get("person_name", "")
    
    print("  💼 Fetching career information...")
    result = get_person_career_info_tool.invoke({"person_name": person_name})
    
    return {**state, "career_info": result}


def fetch_news_info(state: PersonAgentState) -> PersonAgentState:
    """Fetch recent news about the person."""
    person_name = state.get("person_name", "")
    
    print("  📰 Searching for news...")
    result = search_person_news_tool.invoke({"person_name": person_name})
    
    return {**state, "news_info": result}


def fetch_social_media(state: PersonAgentState) -> PersonAgentState:
    """Fetch social media information."""
    person_name = state.get("person_name", "")
    
    print("  🌐 Gathering social media links...")
    result = get_person_social_media_tool.invoke({"person_name": person_name})
    
    return {**state, "social_media": result}


def display_results(state: PersonAgentState) -> PersonAgentState:
    """Display all collected information."""
    print("\n" + "="*60)
    print("📋 RESEARCH RESULTS")
    print("="*60)
    
    if state.get("error"):
        print(f"\n❌ Error: {state['error']}")
        return state
    
    # Display biographical info
    person_info = state.get("person_info", {})
    if person_info.get("success"):
        data = person_info["data"]
        print("\n📖 BIOGRAPHICAL INFORMATION:")
        print(f"  Name: {data['title']}")
        if data.get('description'):
            print(f"  Description: {data['description']}")
        print(f"\n  Summary:")
        print(f"  {data['extract']}")
        if data.get('url'):
            print(f"\n  Wikipedia: {data['url']}")
        if data.get('thumbnail'):
            print(f"  Photo: {data['thumbnail']}")
    else:
        print(f"\n📖 BIOGRAPHICAL INFORMATION:")
        print(f"  ⚠️  {person_info.get('error', 'No information available')}")
    
    # Display career info
    career_info = state.get("career_info", {})
    if career_info.get("success"):
        data = career_info["data"]
        print("\n💼 CAREER INFORMATION:")
        print(f"  Name: {data.get('name', 'N/A')}")
        print(f"  Description: {data.get('description', 'N/A')}")
        
        if data.get('occupations'):
            print(f"\n  Occupations:")
            for occupation in data['occupations']:
                print(f"    • {occupation}")
        
        if data.get('awards'):
            print(f"\n  Awards & Recognition:")
            for award in data['awards']:
                print(f"    🏆 {award}")
        
        if data.get('note'):
            print(f"\n  Note: {data['note']}")
    else:
        print(f"\n💼 CAREER INFORMATION:")
        print(f"  ⚠️  {career_info.get('error', 'No career information available')}")
    
    # Display news info
    news_info = state.get("news_info", {})
    if news_info.get("success"):
        data = news_info["data"]
        print("\n📰 NEWS & MEDIA:")
        if data.get('note'):
            print(f"  ℹ️  {data['note']}")
        if data.get('articles'):
            for article in data['articles']:
                print(f"    • {article}")
    else:
        print(f"\n📰 NEWS & MEDIA:")
        print(f"  ⚠️  {news_info.get('error', 'No news information available')}")
    
    # Display social media
    social_media = state.get("social_media", {})
    if social_media.get("success"):
        data = social_media["data"]
        print("\n🌐 SOCIAL MEDIA & ONLINE PRESENCE:")
        if data.get('note'):
            print(f"  ℹ️  {data['note']}")
        if data.get('platforms'):
            print(f"\n  Search Links:")
            for platform, link in data['platforms'].items():
                print(f"    {platform.title()}: {link}")
    else:
        print(f"\n🌐 SOCIAL MEDIA & ONLINE PRESENCE:")
        print(f"  ⚠️  {social_media.get('error', 'No social media information available')}")
    
    print("\n" + "="*60)
    
    return state


def create_agent():
    """Create and return the person research agent."""
    # Create the graph
    graph = StateGraph(PersonAgentState)
    
    # Add nodes for each step
    graph.add_node("get_input", get_person_input)
    graph.add_node("fetch_person_info", fetch_person_info)
    graph.add_node("fetch_career_info", fetch_career_info)
    graph.add_node("fetch_news_info", fetch_news_info)
    graph.add_node("fetch_social_media", fetch_social_media)
    graph.add_node("display_results", display_results)
    
    # Add edges to define the flow
    graph.add_edge(START, "get_input")
    graph.add_edge("get_input", "fetch_person_info")
    graph.add_edge("fetch_person_info", "fetch_career_info")
    graph.add_edge("fetch_career_info", "fetch_news_info")
    graph.add_edge("fetch_news_info", "fetch_social_media")
    graph.add_edge("fetch_social_media", "display_results")
    graph.add_edge("display_results", END)
    
    # Compile the graph
    return graph.compile()


def main():
    """Run the person research agent."""
    agent = create_agent()
    
    # Run the agent
    result = agent.invoke({
        "person_name": "",
        "person_info": {},
        "career_info": {},
        "news_info": {},
        "social_media": {},
        "error": ""
    })
    
    print("\n✅ Research completed!")


if __name__ == "__main__":
    main()
