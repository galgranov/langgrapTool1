"""
LangGraph agent that fetches city information, weather forecast, and census data.
Refactored to use modular tools with voice generation.
"""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from tools import get_city_info_tool, get_weather_tool, get_census_tool, generate_voice_tool


class AgentState(TypedDict):
    """State for the city weather agent."""
    city: str
    city_info: dict
    weather: dict
    census: dict
    voice_result: dict
    error: str


def get_city_input(state: AgentState) -> AgentState:
    """Get city name from user."""
    print("\n" + "="*60)
    print("🌍 CITY INFORMATION AGENT")
    print("="*60)
    city = input("\nEnter a city name: ").strip()
    
    if not city:
        return {**state, "error": "No city name provided"}
    
    print(f"\n🔎 Gathering information about {city}...")
    return {**state, "city": city, "error": ""}


def fetch_city_info(state: AgentState) -> AgentState:
    """Fetch city information using the city info tool."""
    city = state.get("city", "")
    
    print("  📍 Fetching city information...")
    result = get_city_info_tool.invoke({"city": city})
    
    return {**state, "city_info": result}


def fetch_weather(state: AgentState) -> AgentState:
    """Fetch weather data using the weather tool."""
    city = state.get("city", "")
    
    print("  🌤️  Fetching weather forecast...")
    result = get_weather_tool.invoke({"city": city})
    
    return {**state, "weather": result}


def fetch_census(state: AgentState) -> AgentState:
    """Fetch census/demographic data using the census tool."""
    city = state.get("city", "")
    
    print("  📊 Fetching census & demographic data...")
    result = get_census_tool.invoke({"city": city})
    
    return {**state, "census": result}


def generate_voice_summary(state: AgentState) -> AgentState:
    """Generate voice summary of the collected information."""
    city = state.get("city", "")
    
    print("  🔊 Generating voice summary...")
    
    # Build summary text for voice
    summary_parts = []
    summary_parts.append(f"City information report for {city}.")
    
    # Add city info
    city_info = state.get("city_info", {})
    if city_info.get("success"):
        data = city_info["data"]
        summary_parts.append(f"{data['title']}. {data['description'][:300]}")
    
    # Add census info
    census = state.get("census", {})
    if census.get("success"):
        data = census["data"]
        summary_parts.append(f"The city is located in {data['country']}.")
        if data.get('city_population') and data['city_population'] != 'N/A':
            summary_parts.append(f"Population is approximately {data['city_population']:,}.")
    
    # Add weather
    weather = state.get("weather", {})
    if weather.get("success"):
        data = weather["data"]
        current = data["current"]
        summary_parts.append(f"Current weather: {current['condition']}, temperature {current['temperature']} degrees Celsius.")
        if data["forecast"]:
            first_forecast = data["forecast"][0]
            summary_parts.append(f"Tomorrow's forecast: {first_forecast['condition']}, with temperatures between {first_forecast['min_temp']} and {first_forecast['max_temp']} degrees.")
    
    summary_text = " ".join(summary_parts)
    
    # Generate voice file
    result = generate_voice_tool.invoke({"text": summary_text, "city": city})
    
    return {**state, "voice_result": result}


def display_results(state: AgentState) -> AgentState:
    """Display all collected information."""
    print("\n" + "="*60)
    print("📋 RESULTS")
    print("="*60)
    
    if state.get("error"):
        print(f"\n❌ Error: {state['error']}")
        return state
    
    # Display city info
    city_info = state.get("city_info", {})
    if city_info.get("success"):
        data = city_info["data"]
        print("\n📍 CITY INFORMATION:")
        print(f"  City: {data['title']}")
        print(f"  Description: {data['description'][:200]}..." if len(data['description']) > 200 else f"  Description: {data['description']}")
        if data.get('url'):
            print(f"  Wikipedia: {data['url']}")
    else:
        print(f"\n📍 CITY INFORMATION:")
        print(f"  ⚠️  {city_info.get('error', 'No information available')}")
    
    # Display census data
    census = state.get("census", {})
    if census.get("success"):
        data = census["data"]
        print("\n📊 CENSUS & DEMOGRAPHIC DATA:")
        print(f"  City: {data['city']}")
        print(f"  Country: {data['country']}")
        if data.get('city_population') and data['city_population'] != 'N/A':
            print(f"  City Population: {data['city_population']:,}")
        print(f"  Region: {data.get('admin1', 'N/A')}")
        print(f"  Elevation: {data.get('elevation', 'N/A')}")
        print(f"  Timezone: {data.get('timezone', 'N/A')}")
        
        if data.get('country_info'):
            country_info = data['country_info']
            print(f"\n  Country Information:")
            print(f"    Capital: {country_info.get('capital', 'N/A')}")
            print(f"    Region: {country_info.get('region', 'N/A')} ({country_info.get('subregion', 'N/A')})")
            if country_info.get('population') != 'N/A':
                print(f"    Population: {country_info['population']:,}")
            if country_info.get('area') != 'N/A':
                print(f"    Area: {country_info['area']:,} km²")
            print(f"    Languages: {country_info.get('languages', 'N/A')}")
            print(f"    Currency: {country_info.get('currency', 'N/A')}")
    else:
        print(f"\n📊 CENSUS & DEMOGRAPHIC DATA:")
        print(f"  ⚠️  {census.get('error', 'No data available')}")
    
    # Display weather
    weather = state.get("weather", {})
    if weather.get("success"):
        data = weather["data"]
        location = data["location"]
        current = data["current"]
        
        print("\n🌡️  WEATHER FORECAST:")
        print(f"  Location: {location['name']}, {location['country']}")
        print(f"  Coordinates: {location['latitude']:.2f}°N, {location['longitude']:.2f}°E")
        print(f"\n  Current Weather:")
        print(f"    Condition: {current['condition']}")
        print(f"    Temperature: {current['temperature']}°C")
        print(f"    Feels like: {current['feels_like']}°C")
        print(f"    Humidity: {current['humidity']}%")
        print(f"    Wind Speed: {current['wind_speed']} km/h")
        print(f"    Precipitation: {current['precipitation']} mm")
        
        print(f"\n  3-Day Forecast:")
        for day in data["forecast"]:
            print(f"    {day['date']}: {day['condition']}, {day['min_temp']}°C - {day['max_temp']}°C, Precipitation: {day['precipitation']}mm")
    else:
        print(f"\n🌡️  WEATHER FORECAST:")
        print(f"  ⚠️  {weather.get('error', 'No weather data available')}")
    
    # Display voice generation result
    voice_result = state.get("voice_result", {})
    if voice_result.get("success"):
        data = voice_result["data"]
        print("\n🔊 VOICE SUMMARY:")
        print(f"  ✅ {data['message']}")
        print(f"  📁 File: {data['filename']}")
        print(f"  📝 Text length: {data['text_length']} characters")
    else:
        print(f"\n🔊 VOICE SUMMARY:")
        print(f"  ⚠️  {voice_result.get('error', 'Voice generation not available')}")
    
    print("\n" + "="*60)
    
    return state


def create_agent():
    """Create and return the city information agent."""
    # Create the graph
    graph = StateGraph(AgentState)
    
    # Add nodes for each step
    graph.add_node("get_input", get_city_input)
    graph.add_node("fetch_city_info", fetch_city_info)
    graph.add_node("fetch_weather", fetch_weather)
    graph.add_node("fetch_census", fetch_census)
    graph.add_node("generate_voice", generate_voice_summary)
    graph.add_node("display_results", display_results)
    
    # Add edges to define the flow
    graph.add_edge(START, "get_input")
    graph.add_edge("get_input", "fetch_city_info")
    graph.add_edge("fetch_city_info", "fetch_weather")
    graph.add_edge("fetch_weather", "fetch_census")
    graph.add_edge("fetch_census", "generate_voice")
    graph.add_edge("generate_voice", "display_results")
    graph.add_edge("display_results", END)
    
    # Compile the graph
    return graph.compile()


def main():
    """Run the city information agent."""
    agent = create_agent()
    
    # Run the agent
    result = agent.invoke({
        "city": "",
        "city_info": {},
        "weather": {},
        "census": {},
        "voice_result": {},
        "error": ""
    })
    
    print("\n✅ Agent execution completed!")


if __name__ == "__main__":
    main()
