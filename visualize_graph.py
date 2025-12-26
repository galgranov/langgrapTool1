"""
Visualize the City Weather Agent graph structure.
"""
from city_weather_agent import create_agent


def visualize_graph():
    """Create and display the graph visualization."""
    agent = create_agent()
    
    try:
        # Try to generate PNG image
        png_data = agent.get_graph().draw_mermaid_png()
        
        # Save to file
        with open("city_weather_agent_graph.png", "wb") as f:
            f.write(png_data)
        
        print("✅ Graph visualization saved as 'city_weather_agent_graph.png'")
        print("\nYou can also view the graph in ASCII format below:")
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"PNG generation not available: {e}")
    
    # Try ASCII representation
    try:
        print("\n" + "="*60)
        print(agent.get_graph().draw_ascii())
        print("="*60)
    except ImportError:
        print("\nASCII rendering requires 'grandalf' package.")
        print("Skipping ASCII visualization...")
    
    # Also generate Mermaid diagram code
    print("\n📊 Mermaid Diagram Code (paste into https://mermaid.live):")
    print("\n" + "="*60)
    print(agent.get_graph().draw_mermaid())
    print("="*60)


if __name__ == "__main__":
    visualize_graph()
