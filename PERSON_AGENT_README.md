# Person Research Agent

A LangGraph-based agent that researches people using multiple data sources including Wikipedia, Wikidata, and provides comprehensive biographical, career, and social media information.

## Features

- 📖 **Biographical Information**: Fetches detailed info from Wikipedia
- 💼 **Career Data**: Gets occupation, awards, and achievements from Wikidata
- 📰 **News Search**: Placeholder for news API integration
- 🌐 **Social Media Links**: Generates search links for major platforms
- 🔧 **Modular Tools**: Clean architecture with reusable tool functions
- 🔄 **Interactive**: Prompts user for person name
- 🆓 **No API Keys Required**: Core features use free public APIs

## Architecture

### Tools Module (`person_tools.py`)
Contains four independent tools decorated with `@tool` from LangChain:
- `get_person_info_tool(person_name)` - Wikipedia biographical information
- `get_person_career_info_tool(person_name)` - Wikidata career data (occupations, awards)
- `search_person_news_tool(person_name)` - News search (placeholder)
- `get_person_social_media_tool(person_name)` - Social media search links

### Agent Module (`person_research_agent.py`)
LangGraph workflow with nodes:
1. **get_input** - Prompts user for person name
2. **fetch_person_info** - Calls Wikipedia API
3. **fetch_career_info** - Calls Wikidata API
4. **fetch_news_info** - Searches for news (placeholder)
5. **fetch_social_media** - Generates social media search links
6. **display_results** - Formats and displays all data

### Graph Flow
```
START → get_input → fetch_person_info → fetch_career_info → fetch_news_info → fetch_social_media → display_results → END
```

## Usage

### Run the Agent

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the agent
python person_research_agent.py
```

When prompted, enter a person's name (e.g., "Albert Einstein", "Marie Curie", "Elon Musk").

### Example Output

```
============================================================
👤 PERSON RESEARCH AGENT
============================================================

Enter a person's name: Albert Einstein

🔎 Researching Albert Einstein...
  📖 Fetching biographical information...
  💼 Fetching career information...
  📰 Searching for news...
  🌐 Gathering social media links...

============================================================
📋 RESEARCH RESULTS
============================================================

📖 BIOGRAPHICAL INFORMATION:
  Name: Albert Einstein
  Description: German-born theoretical physicist (1879-1955)

  Summary:
  Albert Einstein was a German-born theoretical physicist who is widely 
  held to be one of the greatest and most influential scientists of all time...

  Wikipedia: https://en.wikipedia.org/wiki/Albert_Einstein
  Photo: https://upload.wikimedia.org/...

💼 CAREER INFORMATION:
  Name: Albert Einstein
  Description: German-born theoretical physicist

  Occupations:
    • Physicist
    • Mathematician
    • University teacher
    • Philosopher of science

  Awards & Recognition:
    🏆 Nobel Prize in Physics
    🏆 Copley Medal
    🏆 Max Planck Medal

📰 NEWS & MEDIA:
  ℹ️  News search would require a news API key (e.g., NewsAPI, NewsData.io)

🌐 SOCIAL MEDIA & ONLINE PRESENCE:
  ℹ️  Social media search would require API authentication

  Search Links:
    Twitter: Search: https://twitter.com/search?q=Albert%20Einstein
    Linkedin: Search: https://www.linkedin.com/search/results/people/?keywords=Albert%20Einstein
    Github: Search: https://github.com/search?q=Albert+Einstein&type=users

============================================================

✅ Research completed!
```

## Tools Reference

### Person Info Tool

**Function**: `get_person_info_tool(person_name: str) -> Dict[str, Any]`

Fetches biographical information from Wikipedia.

**Returns**:
```python
{
    "success": True/False,
    "data": {
        "title": "Person Name",
        "description": "Brief description",
        "extract": "Full biographical text",
        "url": "https://en.wikipedia.org/wiki/Person_Name",
        "thumbnail": "https://upload.wikimedia.org/.../photo.jpg"
    },
    "error": "Error message if failed"
}
```

### Career Info Tool

**Function**: `get_person_career_info_tool(person_name: str) -> Dict[str, Any]`

Fetches career information from Wikidata including occupations and awards.

**Returns**:
```python
{
    "success": True/False,
    "data": {
        "name": "Person Name",
        "description": "Brief description",
        "occupations": ["Occupation1", "Occupation2"],
        "awards": ["Award1", "Award2"],
        "notable_works": []
    },
    "error": "Error message if failed"
}
```

### News Search Tool

**Function**: `search_person_news_tool(person_name: str) -> Dict[str, Any]`

Placeholder for news API integration.

**Note**: Requires a news API key for production use (e.g., NewsAPI.org, NewsData.io)

### Social Media Tool

**Function**: `get_person_social_media_tool(person_name: str) -> Dict[str, Any]`

Generates search links for major social media platforms.

**Returns**:
```python
{
    "success": True,
    "data": {
        "person": "Person Name",
        "note": "Social media search would require API authentication",
        "platforms": {
            "twitter": "https://twitter.com/search?q=...",
            "linkedin": "https://www.linkedin.com/search/...",
            "github": "https://github.com/search?..."
        }
    }
}
```

## Dependencies

- **langgraph**: For building the agent workflow
- **langchain-core**: For the @tool decorator
- **requests**: For making API calls
- **gtts**: For text-to-speech generation
- **typing**: For type hints

All dependencies are managed via `uv` and defined in `pyproject.toml`.

## APIs Used

### Wikipedia API
- **Endpoint**: `https://en.wikipedia.org/api/rest_v1/page/summary/{person}`
- **Purpose**: Fetch biographical information
- **Rate Limiting**: Free, subject to Wikipedia's terms

### Wikidata API
- **Endpoints**: 
  - Search: `https://www.wikidata.org/w/api.php?action=wbsearchentities`
  - Entity: `https://www.wikidata.org/w/api.php?action=wbgetentities`
- **Purpose**: Get structured data (occupations, awards, etc.)
- **Rate Limiting**: Free, no API key required

### Google Text-to-Speech (gTTS)
- **Purpose**: Generate audio summaries
- **Rate Limiting**: Free, no API key required

## Using Tools Independently

You can use the tools independently in your own code:

```python
from person_tools import get_person_info_tool, get_person_career_info_tool

# Get person information
person_info = get_person_info_tool.invoke({"person_name": "Marie Curie"})
if person_info["success"]:
    print(person_info["data"]["extract"])

# Get career info
career = get_person_career_info_tool.invoke({"person_name": "Marie Curie"})
if career["success"]:
    print(f"Occupations: {career['data']['occupations']}")
    print(f"Awards: {career['data']['awards']}")
```

## Customization

### Add News API Integration

To integrate a real news API:

1. Get an API key from NewsAPI.org or similar service
2. Update `search_person_news_tool` in `person_tools.py`:

```python
@tool
def search_person_news_tool(person_name: str) -> Dict[str, Any]:
    api_key = "YOUR_API_KEY"
    url = f"https://newsapi.org/v2/everything?q={person_name}&apiKey={api_key}"
    response = requests.get(url)
    # Process and return articles
```

### Add Social Media API Integration

For real social media data:

1. Register for Twitter API, LinkedIn API, etc.
2. Implement OAuth authentication
3. Update `get_person_social_media_tool` with actual API calls

## Comparison with City Agent

| Feature | City Agent | Person Agent |
|---------|------------|--------------|
| Primary Source | Wikipedia, OpenMeteo, REST Countries | Wikipedia, Wikidata |
| Data Types | Geographic, Weather, Demographics | Biographical, Career, Awards |
| Voice Generation | ✅ Yes | ❌ No |
| Free APIs | ✅ All features | ⚠️ News/Social require keys |
| Use Case | Travel, Research | Biography, Professional research |

## Future Enhancements

- Integrate real news APIs (NewsAPI, NewsData.io)
- Add social media API authentication
- Include academic publications (Google Scholar)
- Add image search and photo gallery
- Implement fact-checking and verification
- Add timeline visualization
- Support for multiple people comparison
- Add family tree and relationships
- Include notable quotes
- Add video content search

## Troubleshooting

**Issue**: Person not found in Wikipedia
- **Solution**: Try full name with middle names or try alternative spellings

**Issue**: Limited career information from Wikidata
- **Solution**: Not all people have complete Wikidata entries; this is normal for less notable individuals

**Issue**: No news results
- **Solution**: News API integration requires an API key (not implemented by default)

**Issue**: Social media links don't work
- **Solution**: Links are search URLs, not direct profiles; manual verification needed

## Project Structure

```
/Users/galg/dev/lang/
├── person_research_agent.py   # Main person research agent
├── person_tools.py             # Person-specific tools
├── city_weather_agent.py       # City information agent
├── tools.py                    # Shared tools (voice generation)
├── pyproject.toml              # Project dependencies
└── audio_output/               # Generated audio files
```

## License

This project uses free public APIs. Please respect their terms of service and rate limits.
