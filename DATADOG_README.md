# 📊 Datadog Integration Guide

Complete monitoring, logging, and tracing for your LangGraph multi-agent system.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Metrics Reference](#metrics-reference)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## 🎯 Overview

This integration provides comprehensive observability for your multi-agent system with:

- **📈 Custom Metrics**: Business and performance metrics
- **🔍 Distributed Tracing**: APM traces across agent workflows
- **📝 Structured Logging**: JSON logs with trace correlation
- **🎨 Pre-configured Dashboards**: Ready-to-use monitoring views

### What Gets Monitored

- ✅ Agent execution (success/failure, duration)
- ✅ Tool invocations (company, person, weather tools)
- ✅ External API calls (Yahoo Finance, Wikipedia, etc.)
- ✅ Business metrics (executives researched, companies analyzed)
- ✅ A2A protocol messages (inter-agent communication)
- ✅ Error tracking with full context

---

## ✨ Features

### 1. **Automatic Instrumentation**
Decorators that automatically track:
- Agent workflows
- Tool executions
- API calls
- Custom operations

### 2. **Trace Correlation**
Logs are automatically correlated with traces for easy debugging.

### 3. **Business Metrics**
Track domain-specific metrics like:
- Number of executives researched
- Companies analyzed
- Successful vs failed operations

### 4. **Flexible Configuration**
Enable/disable features individually without code changes.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install ddtrace datadog-api-client python-json-logger
```

Or update from `pyproject.toml`:

```bash
pip install -e .
```

### 2. Get Datadog API Keys

1. Sign up at [Datadog](https://www.datadoghq.com/) (free trial available)
2. Navigate to: **Organization Settings** → **API Keys**
3. Create or copy your **API Key**
4. Navigate to: **Organization Settings** → **Application Keys**
5. Create or copy your **Application Key**

### 3. Configure Environment

Copy the example configuration:

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```bash
DD_API_KEY=your_actual_api_key_here
DD_APP_KEY=your_actual_app_key_here
DD_SITE=datadoghq.com  # or your region
```

### 4. Start Datadog Agent (for Tracing)

**Option A: Docker (Recommended)**

```bash
docker run -d \
  --name dd-agent \
  -e DD_API_KEY=your_api_key \
  -e DD_APM_ENABLED=true \
  -e DD_APM_NON_LOCAL_TRAFFIC=true \
  -p 8126:8126 \
  datadog/agent:latest
```

**Option B: Native Install**

Follow the [official installation guide](https://docs.datadoghq.com/agent/).

### 5. Run Your Agents

```bash
# Check configuration status
python datadog_config.py

# Run an agent (monitoring happens automatically)
python meta_agent.py
```

---

## 📦 Installation

### Dependencies Added

The integration requires these packages (already in `pyproject.toml`):

```toml
dependencies = [
    "ddtrace>=2.18.0",           # APM tracing
    "datadog-api-client>=2.31.0", # Metrics API
    "python-json-logger>=2.0.7",  # Structured logging
]
```

### Module Structure

```
lang/
├── datadog_config.py      # Configuration management
├── datadog_logger.py      # Logging utilities
├── datadog_metrics.py     # Metrics client
├── datadog_tracing.py     # APM tracing
├── .env.example           # Configuration template
└── DATADOG_README.md      # This file
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DD_API_KEY` | ✅ Yes | - | Datadog API key |
| `DD_APP_KEY` | ✅ Yes* | - | Datadog Application key (*for metrics) |
| `DD_SITE` | ✅ Yes | `datadoghq.com` | Datadog site (region) |
| `DD_SERVICE` | No | `lang-agents` | Service name |
| `DD_ENV` | No | `development` | Environment (dev/staging/prod) |
| `DD_VERSION` | No | `0.1.0` | Application version |
| `DD_TRACE_ENABLED` | No | `true` | Enable tracing |
| `DD_METRICS_ENABLED` | No | `true` | Enable metrics |
| `DD_LOGGING_ENABLED` | No | `true` | Enable structured logging |
| `DD_TRACE_SAMPLE_RATE` | No | `1.0` | Trace sample rate (0.0-1.0) |
| `DD_LOG_LEVEL` | No | `INFO` | Log level |

### Feature Toggle

You can disable individual features without removing the integration:

```bash
# Disable tracing but keep metrics and logging
DD_TRACE_ENABLED=false

# Disable metrics
DD_METRICS_ENABLED=false

# Use standard logging instead of JSON
DD_LOGGING_ENABLED=false
```

### Validation

Check your configuration:

```bash
python datadog_config.py
```

Output:
```
🔧 DATADOG CONFIGURATION STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Service: lang-agents
🌍 Environment: development
📦 Version: 0.1.0
...
```

---

## 💡 Usage Examples

### 1. Instrumenting Agents

```python
from datadog_tracing import trace_agent
from datadog_metrics import track_agent_execution
from datadog_logger import get_logger, log_agent_start, log_agent_end

logger = get_logger(__name__, agent_name="my_agent")

@trace_agent("my_agent")
def run_my_agent(state: dict):
    log_agent_start(logger, "my_agent", ticker=state.get("ticker"))
    
    try:
        # Your agent logic here
        result = process_data(state)
        
        log_agent_end(logger, "my_agent", success=True)
        return result
    except Exception as e:
        log_agent_end(logger, "my_agent", success=False)
        raise
```

### 2. Instrumenting Tools

```python
from datadog_tracing import trace_tool
from langchain_core.tools import tool

@tool
@trace_tool("get_data", api_name="external_api")
def get_data_tool(query: str):
    """Fetch data from external API."""
    # Tool implementation
    return {"success": True, "data": result}
```

### 3. Custom Metrics

```python
from datadog_metrics import increment, histogram, gauge

# Count events
increment("custom.events", tags=["event_type:user_action"])

# Track timing
histogram("custom.operation.duration", duration_seconds)

# Set gauge values
gauge("custom.queue.size", queue_length)
```

### 4. Custom Tracing

```python
from datadog_tracing import TraceSpan

with TraceSpan("custom_operation", span_type="custom") as span:
    span.set_tag("user_id", user_id)
    span.set_tag("operation_type", "data_processing")
    
    # Your code here
    result = process_data()
```

### 5. Contextual Logging

```python
from datadog_logger import get_logger, LoggerContext

logger = get_logger(__name__)

with LoggerContext(logger, ticker="AAPL", request_id="12345") as ctx_logger:
    ctx_logger.info("Processing request")
    # All logs in this context will include ticker and request_id
```

---

## 📊 Metrics Reference

### Agent Metrics

| Metric Name | Type | Description | Tags |
|-------------|------|-------------|------|
| `lang_agents.agent.execution.count` | Count | Total agent runs | `agent:<name>` |
| `lang_agents.agent.execution.duration` | Histogram | Agent execution time | `agent:<name>` |
| `lang_agents.agent.success.count` | Count | Successful runs | `agent:<name>` |
| `lang_agents.agent.error.count` | Count | Failed runs | `agent:<name>` |

### Tool Metrics

| Metric Name | Type | Description | Tags |
|-------------|------|-------------|------|
| `lang_agents.tool.invocation.count` | Count | Tool invocations | `tool:<name>` |
| `lang_agents.tool.execution.duration` | Histogram | Tool execution time | `tool:<name>` |
| `lang_agents.tool.success.count` | Count | Successful invocations | `tool:<name>` |
| `lang_agents.tool.error.count` | Count | Failed invocations | `tool:<name>` |

### API Metrics

| Metric Name | Type | Description | Tags |
|-------------|------|-------------|------|
| `lang_agents.api.call.count` | Count | External API calls | `api:<name>`, `endpoint:<path>`, `status_code:<code>` |
| `lang_agents.api.call.duration` | Histogram | API latency | `api:<name>`, `endpoint:<path>` |
| `lang_agents.api.error.count` | Count | API errors | `api:<name>` |

### Business Metrics

| Metric Name | Type | Description | Tags |
|-------------|------|-------------|------|
| `lang_agents.business.executives.researched` | Count | Executives researched | `ticker:<symbol>` |
| `lang_agents.business.companies.analyzed` | Count | Companies analyzed | `ticker:<symbol>` |
| `lang_agents.business.persons.researched` | Count | Persons researched | `person:<name>` |

### A2A Protocol Metrics

| Metric Name | Type | Description | Tags |
|-------------|------|-------------|------|
| `lang_agents.a2a.message.count` | Count | Inter-agent messages | `sender:<agent>`, `receiver:<agent>`, `message_type:<type>` |
| `lang_agents.a2a.message.latency` | Histogram | Message routing time | `sender:<agent>`, `receiver:<agent>` |
| `lang_agents.a2a.conversation.depth` | Gauge | Conversation depth | - |

---

## 🐛 Troubleshooting

### Issue: "DD_API_KEY is not set"

**Solution**: Export your API key:
```bash
export DD_API_KEY=your_key_here
export DD_APP_KEY=your_app_key_here
```

Or create a `.env` file with the keys.

### Issue: No traces appearing in Datadog

**Possible causes**:
1. **Datadog Agent not running**: Start the agent (see Quick Start)
2. **Tracing disabled**: Check `DD_TRACE_ENABLED=true`
3. **Agent listening on wrong port**: Ensure agent is on `localhost:8126`

**Check agent status**:
```bash
docker logs dd-agent
```

### Issue: No metrics appearing

**Possible causes**:
1. **APP_KEY not set**: Metrics require `DD_APP_KEY`
2. **Metrics disabled**: Check `DD_METRICS_ENABLED=true`
3. **API key invalid**: Verify keys in Datadog UI

**Test metrics manually**:
```bash
python datadog_metrics.py
```

### Issue: Logs not correlated with traces

**Solution**: Ensure both tracing and logging are enabled:
```bash
DD_TRACE_ENABLED=true
DD_LOGGING_ENABLED=true
```

### Issue: Import errors

**Solution**: Install missing dependencies:
```bash
pip install ddtrace datadog-api-client python-json-logger
```

---

## 🎯 Best Practices

### 1. Use Appropriate Sample Rates

For high-traffic applications, reduce costs with sampling:

```bash
# Production: 10% sampling
DD_TRACE_SAMPLE_RATE=0.1

# Development: 100% sampling
DD_TRACE_SAMPLE_RATE=1.0
```

### 2. Tag Everything

Use meaningful tags for filtering:

```python
track_agent_execution(
    "meta_agent",
    success=True,
    duration=2.5,
    tags=["ticker:AAPL", "workflow:executive_research"]
)
```

### 3. Use Environments

Separate dev, staging, and production:

```bash
# Development
DD_ENV=development

# Production
DD_ENV=production
```

### 4. Monitor Business Metrics

Track what matters to your business:

```python
track_executive_researched(count=10, ticker="AAPL")
track_company_analyzed("GOOGL")
```

### 5. Log Strategically

Don't log everything—focus on key events:

```python
# Good: Log significant events
log_agent_start(logger, "meta_agent", ticker="AAPL")

# Avoid: Logging every loop iteration
for item in large_list:
    logger.debug(f"Processing {item}")  # Too verbose
```

### 6. Handle Errors Gracefully

Always track failures:

```python
try:
    result = risky_operation()
except Exception as e:
    log_error(logger, e, context="risky_operation")
    track_agent_execution("my_agent", success=False)
    raise
```

---

## 📚 Additional Resources

- [Datadog Documentation](https://docs.datadoghq.com/)
- [ddtrace Python Guide](https://ddtrace.readthedocs.io/)
- [Datadog APM](https://docs.datadoghq.com/tracing/)
- [Custom Metrics Guide](https://docs.datadoghq.com/metrics/custom_metrics/)

---

## 🤝 Support

For issues specific to this integration:
1. Check the troubleshooting section above
2. Run `python datadog_config.py` to validate configuration
3. Test individual modules (e.g., `python datadog_logger.py`)

For Datadog-specific issues:
- [Datadog Support](https://docs.datadoghq.com/help/)
- [Community Forums](https://datadoghq.com/community/)

---

**Last Updated**: 2025-12-26  
**Integration Version**: 1.0.0
