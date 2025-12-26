# City Information Agent

A LangGraph-based agent that fetches comprehensive city information including Wikipedia data, weather forecasts, and census/demographic information using modular tools.

## Features

- 📍 **City Information**: Fetches city details from Wikipedia API
- 🌤️ **Weather Forecast**: Gets current weather and 3-day forecast using Open-Meteo API
- 📊 **Census & Demographics**: Retrieves population, geographic, and country data
- 🔊 **Voice Generation**: Automatically generates audio summary using text-to-speech
- 🔧 **Modular Tools**: Refactored architecture with reusable tool functions
- 🔄 **Interactive**: Prompts user for city name
- 🌍 **Global Coverage**: Works with cities worldwide
- 🆓 **No API Keys Required**: Uses free public APIs

## Architecture

The agent is built with a clean, modular architecture:

### Tools Module (`tools.py`)
Contains three independent tools decorated with `@tool` from LangChain:
- `get_city_info_tool(city)` - Wikipedia information
- `get_weather_tool(city)` - Weather data from Open-Meteo
- `get_census_tool(city)` - Census and demographic data

The `@tool` decorator automatically creates a `StructuredTool` object that includes:
- Automatic input validation
- Schema generation for tool parameters
- Better integration with LangChain/LangGraph agents
- Proper documentation extraction from docstrings

### Agent Module (`city_weather_agent.py`)
LangGraph workflow with nodes:
1. **get_input** - Prompts user for city name
2. **fetch_city_info** - Calls city info tool
3. **fetch_weather** - Calls weather tool
4. **fetch_census** - Calls census tool
5. **generate_voice** - Generates audio summary using TTS
6. **display_results** - Formats and displays all data

### Graph Flow
```
START → get_input → fetch_city_info → fetch_weather → fetch_census → generate_voice → display_results → END
```

## Usage

### Run the Agent

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the agent
python city_weather_agent.py
```

When prompted, enter any city name (e.g., "Paris", "Tokyo", "New York", "Tel Aviv").

### Example Output

```
============================================================
🌍 CITY INFORMATION AGENT
============================================================

Enter a city name: Tokyo

🔎 Gathering information about Tokyo...
  📍 Fetching city information...
  🌤️  Fetching weather forecast...
  📊 Fetching census & demographic data...

============================================================
📋 RESULTS
============================================================

📍 CITY INFORMATION:
  City: Tokyo
  Description: Tokyo, officially the Tokyo Metropolis, is the capital of Japan...
  Wikipedia: https://en.wikipedia.org/wiki/Tokyo

📊 CENSUS & DEMOGRAPHIC DATA:
  City: Tokyo
  Country: Japan
  City Population: 13,960,000
  Region: Tōkyō
  Elevation: 40 m
  Timezone: Asia/Tokyo

  Country Information:
    Capital: Tokyo
    Region: Asia (Eastern Asia)
    Population: 125,124,989
    Area: 377,930 km²
    Languages: Japanese
    Currency: Japanese yen

🌡️  WEATHER FORECAST:
  Location: Tokyo, Japan
  Coordinates: 35.69°N, 139.69°E

  Current Weather:
    Condition: Clear sky
    Temperature: 8.1°C
    Feels like: 5.4°C
    Humidity: 45%
    Wind Speed: 10.8 km/h
    Precipitation: 0.0 mm

  3-Day Forecast:
    2025-12-26: Clear sky, 2.5°C - 11.6°C, Precipitation: 0.0mm
    2025-12-27: Mainly clear, 1.5°C - 9.4°C, Precipitation: 0.0mm
    2025-12-28: Partly cloudy, 2.0°C - 10.9°C, Precipitation: 0.0mm

============================================================

✅ Agent execution completed!
```

## Tools Reference

### City Information Tool

**Function**: `get_city_info_tool(city: str) -> Dict[str, Any]`

Fetches city information from Wikipedia API.

**Returns**:
```python
{
    "success": True/False,
    "data": {
        "title": "City Name",
        "description": "City description from Wikipedia",
        "url": "https://en.wikipedia.org/wiki/City_Name"
    },
    "error": "Error message if failed"
}
```

### Weather Tool

**Function**: `get_weather_tool(city: str) -> Dict[str, Any]`

Fetches weather data from Open-Meteo API.

**Returns**:
```python
{
    "success": True/False,
    "data": {
        "location": {
            "name": "City Name",
            "country": "Country",
            "latitude": 0.0,
            "longitude": 0.0
        },
        "current": {
            "condition": "Clear sky",
            "temperature": 0.0,
            "feels_like": 0.0,
            "humidity": 0,
            "wind_speed": 0.0,
            "precipitation": 0.0
        },
        "forecast": [
            {
                "date": "2025-12-26",
                "max_temp": 0.0,
                "min_temp": 0.0,
                "precipitation": 0.0,
                "condition": "Clear sky"
            }
        ]
    },
    "error": "Error message if failed"
}
```

### Census Tool

**Function**: `get_census_tool(city: str) -> Dict[str, Any]`

Fetches census and demographic information.

**Returns**:
```python
{
    "success": True/False,
    "data": {
        "city": "City Name",
        "country": "Country",
        "city_population": 1000000,
        "admin1": "State/Province",
        "admin2": "County/District",
        "elevation": "100 m",
        "timezone": "Timezone",
        "country_info": {
            "country_name": "Country",
            "capital": "Capital City",
            "region": "Region",
            "subregion": "Subregion",
            "population": 10000000,
            "area": 100000.0,
            "languages": "Language1, Language2",
            "currency": "Currency Name",
            "timezone": "Timezone"
        }
    },
    "error": "Error message if failed"
}
```

### Voice Generation Tool

**Function**: `generate_voice_tool(text: str, city: str) -> Dict[str, Any]`

Generates an audio file from text using Google Text-to-Speech (gTTS).

**Parameters**:
- `text`: The text to convert to speech
- `city`: City name to use in the filename (optional, defaults to "output")

**Returns**:
```python
{
    "success": True/False,
    "data": {
        "filename": "audio_output/City_Name_report.mp3",
        "text_length": 246,
        "message": "Audio file saved successfully"
    },
    "error": "Error message if failed"
}
```

**Features**:
- Uses Google's Text-to-Speech API (gTTS)
- Automatically creates `audio_output/` directory
- Generates MP3 files named after the city
- English language with normal speed
- No API key required

**Output Location**: Audio files are saved in the `audio_output/` directory with the format `{city_name}_report.mp3`

## Dependencies

- **langgraph**: For building the agent workflow
- **requests**: For making API calls
- **typing**: For type hints

All dependencies are managed via `uv` and defined in `pyproject.toml`.

## APIs Used

### Wikipedia API
- **Endpoint**: `https://en.wikipedia.org/api/rest_v1/page/summary/{city}`
- **Purpose**: Fetch city descriptions and information
- **Rate Limiting**: Free, subject to Wikipedia's terms

### Open-Meteo Geocoding API
- **Endpoint**: `https://geocoding-api.open-meteo.com/v1/search`
- **Purpose**: Convert city names to coordinates and get basic location data
- **Rate Limiting**: Free, no API key required

### Open-Meteo Weather API
- **Endpoint**: `https://api.open-meteo.com/v1/forecast`
- **Purpose**: Get current weather and forecasts
- **Rate Limiting**: Free, no API key required

### REST Countries API
- **Endpoint**: `https://restcountries.com/v3.1/name/{country}`
- **Purpose**: Get country-level demographic and geographic data
- **Rate Limiting**: Free, no API key required

## Visualizing the Graph

Run the visualization script to see the agent's workflow:

```bash
python visualize_graph.py
```

This generates:
- `city_weather_agent_graph.png` - Visual diagram
- Mermaid code for https://mermaid.live

## Using Tools Independently

You can use the tools independently in your own code:

```python
from tools import get_city_info_tool, get_weather_tool, get_census_tool

# Get city information
city_info = get_city_info_tool("Paris")
if city_info["success"]:
    print(city_info["data"]["description"])

# Get weather
weather = get_weather_tool("Paris")
if weather["success"]:
    print(f"Temperature: {weather['data']['current']['temperature']}°C")

# Get census data
census = get_census_tool("Paris")
if census["success"]:
    print(f"Population: {census['data']['city_population']}")
```

## Customization

### Add New Tools

1. Create a new tool function in `tools.py`:
```python
def get_new_tool(city: str) -> Dict[str, Any]:
    # Your implementation
    return {"success": True, "data": {...}}
```

2. Add to the TOOLS registry:
```python
TOOLS = {
    "city_info": get_city_info_tool,
    "weather": get_weather_tool,
    "census": get_census_tool,
    "new_tool": get_new_tool  # Add your tool
}
```

3. Update the agent in `city_weather_agent.py`:
```python
def fetch_new_data(state: AgentState) -> AgentState:
    city = state.get("city", "")
    result = get_new_tool(city)
    return {**state, "new_data": result}

# Add to graph
graph.add_node("fetch_new_data", fetch_new_data)
graph.add_edge("fetch_census", "fetch_new_data")
graph.add_edge("fetch_new_data", "display_results")
```

### Modify Forecast Days

In `tools.py`, `get_weather_tool()` function:
```python
for i in range(min(3, len(daily.get("time", [])))):  # Change 3 to desired number
```

### Change Display Format

Edit the `display_results()` function in `city_weather_agent.py`.

## Error Handling

All tools return a consistent structure with `success` and `error` fields:
- Network timeouts (10-second timeout on all requests)
- API failures (gracefully handled)
- Missing data (returns "N/A" instead of failing)
- Invalid city names (clear error messages)

## Testing Tools

You can test individual tools:

```bash
python -c "from tools import get_weather_tool; import json; print(json.dumps(get_weather_tool('London'), indent=2))"
```

## Future Enhancements

- Add LLM integration for natural language responses
- Implement parallel tool execution for faster results
- Add caching to reduce API calls
- Include more data sources (air quality, events, attractions)
- Add conditional routing based on available data
- Create a web interface
- Support multiple cities in one query
- Add data visualization charts

## Troubleshooting

**Issue**: Tool returns error
- **Solution**: Check your internet connection and try again

**Issue**: City not found
- **Solution**: Try the official city name (e.g., "New York City" not "NYC")

**Issue**: Missing census data
- **Solution**: Small towns may not have complete data; this is normal

**Issue**: Import errors
- **Solution**: Ensure you're in the virtual environment: `source .venv/bin/activate`

## Project Structure

```
/Users/galg/dev/lang/
├── city_weather_agent.py     # Main agent with LangGraph workflow
├── tools.py                   # Modular tool functions
├── visualize_graph.py         # Graph visualization script
├── helo.py                    # Original example file
├── pyproject.toml             # Project dependencies
├── README.md                  # Project overview
├── AGENT_README.md            # This file
└── .venv/                     # Virtual environment
```

## License

This project uses free public APIs. Please respect their terms of service and rate limits.
