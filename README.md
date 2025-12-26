# lang

A LangGraph project featuring multiple AI agents for research and data gathering.

## 🤖 Available Agents

### 1. 🌤️ City Weather Agent
Provides detailed weather information for cities worldwide.

**Run:**
```bash
python city_weather_agent.py
```

**See:** [City Weather Documentation](AGENT_README.md)

---

### 2. 👤 Person Research Agent
Comprehensive research on individuals using Wikipedia and Wikidata.

**Features:**
- Biographical information
- Career history
- Awards and achievements
- Social media links

**Run:**
```bash
python person_research_agent.py
```

**See:** [Person Agent Documentation](PERSON_AGENT_README.md)

---

### 3. 📈 Company Research Agent
Financial and company analysis using stock tickers.

**Features:**
- Company profile
- Stock prices and metrics
- Financial ratios
- Recent news

**Run:**
```bash
python company_research_agent.py
```

---

### 4. 🎯 MetaAgent
Orchestrates company and person agents for comprehensive executive research.

**Features:**
- Company analysis
- Top 10 executives identification
- Biographical research on each executive
- Comprehensive leadership report

**Run:**
```bash
python meta_agent.py
```

**See:** [MetaAgent Documentation](META_AGENT_README.md)

---

### 5. 🤖 A2A Protocol (NEW!)
Agent-to-Agent communication protocol enabling direct communication between agents.

**Features:**
- Message bus for routing between agents
- Request/Response communication pattern
- Broadcast notifications
- Conversation threading
- Multi-agent workflow orchestration
- Interactive demo mode

**Run:**
```bash
python a2a_demo.py
```

**See:** [A2A Protocol Documentation](A2A_README.md)

---

## 📁 Project Structure

```
lang/
├── README.md                      # This file
├── pyproject.toml                 # Project dependencies
├── uv.lock                        # Lock file
│
├── city_weather_agent.py          # Weather agent
├── tools.py                       # Weather tools
├── AGENT_README.md                # Weather agent docs
│
├── person_research_agent.py       # Person agent
├── person_tools.py                # Person tools
├── PERSON_AGENT_README.md         # Person agent docs
│
├── company_research_agent.py      # Company agent
├── company_tools.py               # Company tools
│
├── meta_agent.py                  # MetaAgent orchestrator
├── META_AGENT_README.md           # MetaAgent docs
│
├── a2a_protocol.py                # A2A protocol core
├── a2a_company_agent.py           # Company agent with A2A
├── a2a_person_agent.py            # Person agent with A2A
├── a2a_coordinator.py             # Coordinator agent
├── a2a_demo.py                    # A2A interactive demo
├── A2A_README.md                  # A2A documentation
│
├── visualize_graph.py             # Graph visualization
└── audio_output/                  # Generated audio reports
```

## 🚀 Getting Started

### Installation

```bash
# Install dependencies
pip install langgraph langchain-core requests
```

### Quick Start

1. **Try the A2A Protocol Demo** (Agent-to-Agent communication):
   ```bash
   python a2a_demo.py
   # Select interactive mode and try: company AAPL, person Tim Cook, full TSLA
   ```

2. **Try the MetaAgent** (Orchestrated workflow):
   ```bash
   python meta_agent.py
   # Enter a stock ticker: AAPL
   ```

3. **Research a person**:
   ```bash
   python person_research_agent.py
   # Enter a name: Elon Musk
   ```

4. **Research a company**:
   ```bash
   python company_research_agent.py
   # Enter a ticker: GOOGL
   ```

5. **Check weather**:
   ```bash
   python city_weather_agent.py
   # Enter a city: Paris
   ```

## 🔧 Tools & APIs

### Company Tools
- Yahoo Finance API (company data, stock prices, executives)

### Person Tools
- Wikipedia API (biographical information)
- Wikidata API (career information)
- Google Search (news and social media)

### Weather Tools
- OpenMeteo API (weather data)

## 🎯 Use Cases

### Investment Research
Use MetaAgent to research companies and their leadership before making investment decisions.

### Competitive Intelligence
Analyze executive teams across different companies in your industry.

### Background Research
Gather comprehensive information on individuals and organizations.

### Due Diligence
Perform thorough research on companies and their key personnel.

## 📊 Agent Architecture

All agents use **LangGraph's StateGraph** for:
- State management
- Sequential workflow execution
- Error handling
- Result aggregation

### Example: MetaAgent Workflow

```
Input (Ticker) → Company Research → Executive Fetch → 
→ Person Research (×10) → Comprehensive Report
```

## 🔍 Features

- ✅ Modular tool architecture
- ✅ Error handling and graceful degradation
- ✅ Rich console output with emojis
- ✅ Orchestration of multiple agents
- ✅ **Agent-to-Agent communication protocol**
- ✅ **Message bus for routing**
- ✅ **Request/Response patterns**
- ✅ **Conversation threading**
- ✅ Real-time API data
- ✅ Comprehensive reporting

## 🛠️ Development

### Adding New Tools

1. Create tool function in appropriate `*_tools.py` file
2. Decorate with `@tool`
3. Add to tool registry
4. Update agent to use new tool

### Creating New Agents

1. Define state using `TypedDict`
2. Create workflow nodes
3. Build StateGraph
4. Add edges to define flow
5. Compile and run

## 📝 License

Part of the LangGraph agents project.

## 🤝 Contributing

To extend the project:
1. Add new tools to existing tool files
2. Create new specialized agents
3. Enhance the MetaAgent orchestration
4. Add new data sources and APIs
5. Improve error handling and reporting

---

**Last Updated**: 2025-12-26
