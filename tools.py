"""
Tools for the City Information Agent.
Each tool is a standalone function that can be used by the agent.
"""
import requests
from typing import Dict, Any
from langchain_core.tools import tool


@tool
def get_city_info_tool(city: str) -> Dict[str, Any]:
    """Fetch city information from Wikipedia.
    
    Args:
        city: Name of the city to get information about
        
    Returns:
        Dictionary with city information or error
    """
    if not city:
        return {"success": False, "error": "No city name provided", "data": None}
    
    try:
        # Use Wikipedia API to get city information
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + city.replace(" ", "_")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "data": {
                    "title": data.get('title', city),
                    "description": data.get('extract', 'No description available'),
                    "url": data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                }
            }
        else:
            return {
                "success": False,
                "error": f"Could not find information about {city}",
                "data": None
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching city info: {str(e)}",
            "data": None
        }


@tool
def get_weather_tool(city: str) -> Dict[str, Any]:
    """Fetch weather forecast for a city using Open-Meteo API.
    
    Args:
        city: Name of the city to get weather forecast for
        
    Returns:
        Dictionary with weather data or error
    """
    if not city:
        return {"success": False, "error": "No city name provided", "data": None}
    
    try:
        # Use Open-Meteo API (free, no API key required)
        # First, get coordinates using geocoding
        geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_response = requests.get(geocode_url, timeout=10)
        
        if geo_response.status_code != 200:
            return {
                "success": False,
                "error": "Could not find coordinates for the city",
                "data": None
            }
        
        geo_data = geo_response.json()
        
        if not geo_data.get("results"):
            return {
                "success": False,
                "error": f"Could not find {city} in the geocoding database",
                "data": None
            }
        
        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        country = location.get("country", "Unknown")
        
        # Get weather data
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
        weather_response = requests.get(weather_url, timeout=10)
        
        if weather_response.status_code != 200:
            return {
                "success": False,
                "error": "Could not fetch weather data",
                "data": None
            }
        
        weather_data = weather_response.json()
        current = weather_data.get("current", {})
        daily = weather_data.get("daily", {})
        
        # Weather code descriptions
        weather_codes = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Foggy", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
            80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
            95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
        }
        
        current_weather_code = current.get("weather_code", 0)
        current_condition = weather_codes.get(current_weather_code, "Unknown")
        
        # Format forecast data
        forecast = []
        for i in range(min(3, len(daily.get("time", [])))):
            daily_code = daily["weather_code"][i]
            forecast.append({
                "date": daily["time"][i],
                "max_temp": daily["temperature_2m_max"][i],
                "min_temp": daily["temperature_2m_min"][i],
                "precipitation": daily["precipitation_sum"][i],
                "condition": weather_codes.get(daily_code, "Unknown")
            })
        
        return {
            "success": True,
            "data": {
                "location": {
                    "name": location['name'],
                    "country": country,
                    "latitude": lat,
                    "longitude": lon
                },
                "current": {
                    "condition": current_condition,
                    "temperature": current.get('temperature_2m', 'N/A'),
                    "feels_like": current.get('apparent_temperature', 'N/A'),
                    "humidity": current.get('relative_humidity_2m', 'N/A'),
                    "wind_speed": current.get('wind_speed_10m', 'N/A'),
                    "precipitation": current.get('precipitation', 'N/A')
                },
                "forecast": forecast
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching weather: {str(e)}",
            "data": None
        }


@tool
def get_census_tool(city: str) -> Dict[str, Any]:
    """Fetch census and demographic information for a city.
    
    Uses geocoding and REST Countries API to gather population,
    geographic, and country-level demographic data.
    
    Args:
        city: Name of the city to get census data for
        
    Returns:
        Dictionary with census/demographic data or error
    """
    if not city:
        return {"success": False, "error": "No city name provided", "data": None}
    
    try:
        # First, try to get the city info to find the country
        geocode_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_response = requests.get(geocode_url, timeout=10)
        
        if geo_response.status_code != 200 or not geo_response.json().get("results"):
            return {
                "success": False,
                "error": f"Could not find location data for {city}",
                "data": None
            }
        
        location = geo_response.json()["results"][0]
        country = location.get("country", "Unknown")
        population = location.get("population", "N/A")
        
        # Try to get country-level data using REST Countries API
        country_data = None
        try:
            country_url = f"https://restcountries.com/v3.1/name/{country}"
            country_response = requests.get(country_url, timeout=10)
            
            if country_response.status_code == 200:
                countries = country_response.json()
                if countries:
                    country_info = countries[0]
                    country_data = {
                        "country_name": country_info.get("name", {}).get("common", country),
                        "capital": country_info.get("capital", ["N/A"])[0] if country_info.get("capital") else "N/A",
                        "region": country_info.get("region", "N/A"),
                        "subregion": country_info.get("subregion", "N/A"),
                        "population": country_info.get("population", "N/A"),
                        "area": country_info.get("area", "N/A"),
                        "languages": ", ".join(country_info.get("languages", {}).values()) if country_info.get("languages") else "N/A",
                        "currency": ", ".join([curr.get("name", "N/A") for curr in country_info.get("currencies", {}).values()]) if country_info.get("currencies") else "N/A",
                        "timezone": country_info.get("timezones", ["N/A"])[0] if country_info.get("timezones") else "N/A"
                    }
        except Exception:
            pass  # Country data is optional
        
        return {
            "success": True,
            "data": {
                "city": location.get("name", city),
                "country": country,
                "city_population": population,
                "admin1": location.get("admin1", "N/A"),  # State/Province
                "admin2": location.get("admin2", "N/A"),  # County/District
                "elevation": f"{location.get('elevation', 'N/A')} m" if location.get('elevation') else "N/A",
                "timezone": location.get("timezone", "N/A"),
                "country_info": country_data
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching census data: {str(e)}",
            "data": None
        }


@tool
def generate_voice_tool(text: str, city: str = "output") -> Dict[str, Any]:
    """Generate an audio file from text using text-to-speech.
    
    Args:
        text: The text to convert to speech
        city: City name to use in the filename (optional)
        
    Returns:
        Dictionary with audio file path or error
    """
    if not text:
        return {"success": False, "error": "No text provided for voice generation", "data": None}
    
    try:
        from gtts import gTTS
        import os
        
        # Create output directory if it doesn't exist
        output_dir = "audio_output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Generate filename with city name
        safe_city_name = "".join(c for c in city if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{output_dir}/{safe_city_name.replace(' ', '_')}_report.mp3"
        
        # Create TTS object and save to file
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filename)
        
        return {
            "success": True,
            "data": {
                "filename": filename,
                "text_length": len(text),
                "message": f"Audio file saved successfully"
            }
        }
    
    except ImportError:
        return {
            "success": False,
            "error": "gTTS library not installed. Install with: uv add gtts",
            "data": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error generating voice: {str(e)}",
            "data": None
        }


# Tool registry for easy access
TOOLS = {
    "city_info": get_city_info_tool,
    "weather": get_weather_tool,
    "census": get_census_tool,
    "voice": generate_voice_tool
}


def get_tool(tool_name: str):
    """Get a tool by name."""
    return TOOLS.get(tool_name)
