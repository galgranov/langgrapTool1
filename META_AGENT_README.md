# 🎯 MetaAgent - Company & Executive Research

## Overview

The MetaAgent is a sophisticated orchestration agent that combines the company research agent and person research agent to provide comprehensive analysis of companies and their leadership teams.

## What It Does

1. **Takes a stock ticker** as input (e.g., AAPL, GOOGL, TSLA)
2. **Researches the company** using the company agent:
   - Company profile and information
   - Current stock price and trading data
   - Financial metrics
3. **Fetches the top 10 company executives**
4. **Researches each executive** using the person agent:
   - Biographical information from Wikipedia
   - Career history and occupations
   - Awards and recognition
5. **Generates a comprehensive report** combining all data

## Architecture

```
MetaAgent
├── Phase 1: Company Research
│   ├── Get ticker input
│   ├── Fetch company info
│   └── Fetch stock price
│
├── Phase 2: Executive Identification
│   └── Fetch company executives (top 10)
│
├── Phase 3: Executive Research
│   └── For each executive:
│       ├── Fetch biographical data
│       └── Fetch career information
│
└── Phase 4: Comprehensive Report
    ├── Company Overview Section
    └── Executive Leadership Section
```

## Tools Used

### Company Tools
- `get_company_info_tool` - Company profile and details
- `get_stock_price_tool` - Current stock data
- `get_company_executives_tool` - Company executives list

### Person Tools
- `get_person_info_tool` - Biographical information
- `get_person_career_info_tool` - Career and professional history

## Usage

### Run the Agent

```bash
python meta_agent.py
```

### Example Session

```
================================================================================
🎯 META AGENT - Company & Executive Research
================================================================================

Enter a stock ticker (e.g., AAPL, GOOGL, TSLA): AAPL

🚀 Starting comprehensive research for AAPL...

────────────────────────────────────────────────────────────────────────────────
📊 PHASE 1: COMPANY RESEARCH
────────────────────────────────────────────────────────────────────────────────
  🏢 Fetching company profile...
  ✓ Company: Apple Inc.
  ✓ Sector: Technology
  ✓ Employees: 161,000
  💰 Fetching stock price data...
  ✓ Current Price: USD 223.45

  👥 Fetching company executives...
  ✓ Found 10 executives

────────────────────────────────────────────────────────────────────────────────
👤 PHASE 2: EXECUTIVE RESEARCH
────────────────────────────────────────────────────────────────────────────────

  [1/10] Researching: Tim Cook
      Title: Chief Executive Officer
      ✓ Found biographical data
      → American business executive, Chief Executive Officer of Apple Inc....

  [2/10] Researching: Luca Maestri
      Title: Chief Financial Officer
      ✓ Found biographical data
      → Italian-American businessman, Chief Financial Officer of Apple Inc....

... (continues for all executives)
```

## Output Report Format

The agent generates a comprehensive report with two main sections:

### 1. Company Overview
- Company name and ticker
- Sector and industry
- Market capitalization
- Employee count
- Headquarters location
- Website
- Current stock price and performance

### 2. Executive Leadership
For each executive:
- **Role at Company**
  - Title
  - Age (if available)
  - Compensation (if available)
  
- **Biographical Information**
  - Description
  - Summary from Wikipedia
  - Wikipedia link
  
- **Career & Occupations**
  - Professional roles
  
- **Awards & Recognition**
  - Notable achievements

## State Management

The agent uses LangGraph's StateGraph with the following state:

```python
class MetaAgentState(TypedDict):
    ticker: str                                    # Stock ticker
    company_info: dict                             # Company data
    stock_price: dict                              # Stock price data
    executives: dict                               # Executives list
    executives_research: List[Dict[str, Any]]      # Research results
    error: str                                     # Error tracking
```

## Workflow Nodes

1. **get_ticker_input** - Get stock ticker from user
2. **fetch_company_data** - Fetch company info and stock price
3. **fetch_executives** - Get list of company executives
4. **research_executives** - Research each executive (biographical + career)
5. **display_results** - Generate and display comprehensive report

## Error Handling

The agent gracefully handles:
- Invalid or non-existent tickers
- API failures or rate limiting
- Missing executive data
- Missing biographical information
- Network timeouts

When data is unavailable, the agent continues execution and clearly marks what's missing in the final report.

## API Dependencies

### Yahoo Finance API
Used for:
- Company information
- Stock prices
- Executive lists

**Note:** The executives endpoint may require authentication or have rate limits. A 401 error typically indicates API key requirements.

### Wikipedia API
Used for:
- Biographical information
- Career history

## Limitations

1. **Executive Data**: The Yahoo Finance executives endpoint may have authentication requirements or rate limits
2. **Person Data**: Biographical information quality depends on Wikipedia availability
3. **Rate Limits**: Multiple API calls are made; rate limiting may occur
4. **Data Accuracy**: Information is sourced from public APIs and may not be real-time

## Future Enhancements

Potential improvements:
- [ ] Add caching to reduce API calls
- [ ] Export reports to PDF or JSON
- [ ] Add visualization of company structure
- [ ] Include executive social media profiles
- [ ] Add executive relationship mapping
- [ ] Support for private companies
- [ ] Historical executive changes tracking

## Integration with Other Agents

The MetaAgent demonstrates how to:
- Orchestrate multiple specialized agents
- Chain agent outputs as inputs
- Combine different data sources
- Handle complex workflows
- Present unified results

## File Structure

```
lang/
├── meta_agent.py              # Main MetaAgent implementation
├── company_tools.py           # Company research tools
├── company_research_agent.py  # Company agent
├── person_tools.py            # Person research tools
├── person_research_agent.py   # Person agent
└── META_AGENT_README.md       # This file
```

## Example Use Cases

1. **Due Diligence**: Research companies and their leadership before investments
2. **Competitive Analysis**: Compare executive teams across companies
3. **Recruitment Research**: Understand potential candidates' backgrounds
4. **Business Intelligence**: Track executive movements and career paths
5. **Academic Research**: Study corporate leadership patterns

## Running Tests

Test with well-known companies:

```bash
# Technology companies
python meta_agent.py
# Enter: AAPL, GOOGL, MSFT, TSLA

# Financial companies
python meta_agent.py
# Enter: JPM, GS, BAC

# Retail companies
python meta_agent.py
# Enter: WMT, AMZN, TGT
```

## Dependencies

Ensure you have the required packages:

```bash
pip install langgraph langchain-core requests
```

## Contributing

To extend the MetaAgent:

1. Add new tools to `company_tools.py` or `person_tools.py`
2. Add new nodes to the state graph
3. Update the `MetaAgentState` TypedDict if needed
4. Add edges to define the workflow
5. Update the `display_results` function to show new data

## License

Part of the LangGraph agents project.

---

**Created**: 2025-12-26  
**Version**: 1.0.0  
**Author**: LangGraph Team
