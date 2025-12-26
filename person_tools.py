"""
Tools for the Person Research Agent.
Each tool is a standalone function that can be used by the agent.
"""
import requests
from typing import Dict, Any
from langchain_core.tools import tool


@tool
def get_person_info_tool(person_name: str) -> Dict[str, Any]:
    """Fetch person information from Wikipedia.
    
    Args:
        person_name: Name of the person to research
        
    Returns:
        Dictionary with person information or error
    """
    if not person_name:
        return {"success": False, "error": "No person name provided", "data": None}
    
    try:
        # Use Wikipedia API to get person information
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + person_name.replace(" ", "_")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "data": {
                    "title": data.get('title', person_name),
                    "description": data.get('description', 'No description available'),
                    "extract": data.get('extract', 'No information available'),
                    "url": data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                    "thumbnail": data.get('thumbnail', {}).get('source', '') if data.get('thumbnail') else None,
                }
            }
        else:
            return {
                "success": False,
                "error": f"Could not find information about {person_name}",
                "data": None
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching person info: {str(e)}",
            "data": None
        }


@tool
def search_person_news_tool(person_name: str) -> Dict[str, Any]:
    """Search for recent news about a person using a free news API.
    
    Args:
        person_name: Name of the person to search news for
        
    Returns:
        Dictionary with news articles or error
    """
    if not person_name:
        return {"success": False, "error": "No person name provided", "data": None}
    
    try:
        # Using NewsData.io free tier or similar
        # For this example, we'll use a simpler approach with RSS/web scraping simulation
        # In production, you'd want to use a proper news API
        
        # Simplified version - return a note that this would require an API key
        return {
            "success": True,
            "data": {
                "person": person_name,
                "note": "News search would require a news API key (e.g., NewsAPI, NewsData.io)",
                "articles": []
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error searching news: {str(e)}",
            "data": None
        }


@tool
def get_person_social_media_tool(person_name: str) -> Dict[str, Any]:
    """Get social media presence information for a person.
    
    Args:
        person_name: Name of the person to search
        
    Returns:
        Dictionary with social media info or error
    """
    if not person_name:
        return {"success": False, "error": "No person name provided", "data": None}
    
    try:
        # This is a placeholder - real implementation would use social media APIs
        # Most social media APIs require authentication and have rate limits
        
        return {
            "success": True,
            "data": {
                "person": person_name,
                "note": "Social media search would require API authentication",
                "platforms": {
                    "twitter": f"Search: https://twitter.com/search?q={person_name.replace(' ', '%20')}",
                    "linkedin": f"Search: https://www.linkedin.com/search/results/people/?keywords={person_name.replace(' ', '%20')}",
                    "github": f"Search: https://github.com/search?q={person_name.replace(' ', '+')}&type=users"
                }
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching social media info: {str(e)}",
            "data": None
        }


@tool
def get_person_career_info_tool(person_name: str) -> Dict[str, Any]:
    """Get career and professional information about a person.
    
    Uses Wikidata API to fetch structured data about occupation, education, awards, etc.
    
    Args:
        person_name: Name of the person
        
    Returns:
        Dictionary with career information or error
    """
    if not person_name:
        return {"success": False, "error": "No person name provided", "data": None}
    
    try:
        # Search Wikidata for the person
        search_url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={person_name}&language=en&format=json"
        search_response = requests.get(search_url, timeout=10)
        
        if search_response.status_code != 200:
            return {
                "success": False,
                "error": "Could not search Wikidata",
                "data": None
            }
        
        search_data = search_response.json()
        
        if not search_data.get("search"):
            return {
                "success": False,
                "error": f"Could not find {person_name} in Wikidata",
                "data": None
            }
        
        # Get the first result (most relevant)
        entity_id = search_data["search"][0]["id"]
        entity_label = search_data["search"][0].get("label", person_name)
        entity_description = search_data["search"][0].get("description", "No description")
        
        # Get detailed entity data
        entity_url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={entity_id}&format=json&props=claims"
        entity_response = requests.get(entity_url, timeout=10)
        
        if entity_response.status_code != 200:
            return {
                "success": True,
                "data": {
                    "name": entity_label,
                    "description": entity_description,
                    "note": "Limited information available"
                }
            }
        
        entity_data = entity_response.json()
        claims = entity_data.get("entities", {}).get(entity_id, {}).get("claims", {})
        
        # Extract relevant information
        career_info = {
            "name": entity_label,
            "description": entity_description,
            "occupations": [],
            "awards": [],
            "notable_works": []
        }
        
        # Get occupations (P106)
        if "P106" in claims:
            for claim in claims["P106"][:5]:  # Limit to 5
                try:
                    occupation_id = claim["mainsnak"]["datavalue"]["value"]["id"]
                    # Get occupation label
                    occ_url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={occupation_id}&format=json&props=labels"
                    occ_response = requests.get(occ_url, timeout=5)
                    if occ_response.status_code == 200:
                        occ_data = occ_response.json()
                        occ_label = occ_data.get("entities", {}).get(occupation_id, {}).get("labels", {}).get("en", {}).get("value", "Unknown")
                        career_info["occupations"].append(occ_label)
                except:
                    pass
        
        # Get awards (P166)
        if "P166" in claims:
            for claim in claims["P166"][:5]:  # Limit to 5
                try:
                    award_id = claim["mainsnak"]["datavalue"]["value"]["id"]
                    award_url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&ids={award_id}&format=json&props=labels"
                    award_response = requests.get(award_url, timeout=5)
                    if award_response.status_code == 200:
                        award_data = award_response.json()
                        award_label = award_data.get("entities", {}).get(award_id, {}).get("labels", {}).get("en", {}).get("value", "Unknown")
                        career_info["awards"].append(award_label)
                except:
                    pass
        
        return {
            "success": True,
            "data": career_info
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching career info: {str(e)}",
            "data": None
        }


# Tool registry for easy access
PERSON_TOOLS = {
    "person_info": get_person_info_tool,
    "person_news": search_person_news_tool,
    "social_media": get_person_social_media_tool,
    "career_info": get_person_career_info_tool
}


def get_person_tool(tool_name: str):
    """Get a tool by name."""
    return PERSON_TOOLS.get(tool_name)
