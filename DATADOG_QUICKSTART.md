# 🚀 Datadog Quick Start Guide

Get up and running with Datadog monitoring in 5 minutes!

---

## ⚡ Quick Setup

### 1. Install Dependencies (1 minute)

```bash
pip install ddtrace datadog-api-client python-json-logger
```

### 2. Configure API Keys (2 minutes)

```bash
# Copy template
cp .env.example .env

# Edit .env and add your keys
# Get keys from: https://app.datadoghq.com/organization-settings/api-keys
```

Your `.env` should look like:
```bash
DD_API_KEY=abc123def456...
DD_APP_KEY=xyz789uvw012...
DD_SITE=datadoghq.com
```

### 3. Start Datadog Agent (1 minute)

**Using Docker:**
```bash
docker run -d \
  --name dd-agent \
  -e DD_API_KEY=your_api_key \
  -e DD_APM_ENABLED=true \
  -e DD_APM_NON_LOCAL_TRAFFIC=true \
  -p 8126:8126 \
  datadog/agent:latest
```

**Verify it's running:**
```bash
docker ps | grep dd-agent
```

### 4. Test the Integration (1 minute)

```bash
# Check configuration
python datadog_config.py

# Run example agent
python example_instrumented_agent.py
```

---

## 📊 View Your Data

### Traces (APM)
Go to: [Datadog APM](https://app.datadoghq.com/apm/traces)
- Filter by service: `lang-agents`
- See execution flows and performance

### Metrics
Go to: [Metrics Explorer](https://app.datadoghq.com/metric/explorer)
- Search for: `lang_agents.*`
- View: agent execution, API calls, business metrics

### Logs
Go to: [Log Explorer](https://app.datadoghq.com/logs)
- Filter by: `service:lang-agents`
- Correlated with traces automatically

---

## 🎯 Next Steps

### Add Monitoring to Your Agents

**Option 1: Use Decorators (Easiest)**
```python
from datadog_tracing import trace_agent

@trace_agent("my_agent")
def my_agent_function(state):
    # Your code here
    return result
```

**Option 2: Manual Instrumentation (More Control)**
```python
from datadog_tracing import TraceSpan
from datadog_metrics import track_agent_execution
from datadog_logger import get_logger

logger = get_logger(__name__, agent_name="my_agent")

def my_agent_function(state):
    with TraceSpan("my_operation") as span:
        span.set_tag("ticker", state["ticker"])
        logger.info("Processing...")
        # Your code here
        track_agent_execution("my_agent", success=True, duration=1.5)
```

### Instrument Your Tools

```python
from datadog_tracing import trace_tool
from langchain_core.tools import tool

@tool
@trace_tool("my_tool", api_name="external_api")
def my_tool(param: str):
    # Tool implementation
    return result
```

---

## 🐛 Troubleshooting

### No traces appearing?

1. **Is the agent running?**
   ```bash
   docker logs dd-agent
   ```

2. **Is tracing enabled?**
   ```bash
   echo $DD_TRACE_ENABLED  # Should be 'true'
   ```

3. **Check agent connection:**
   ```bash
   curl http://localhost:8126/info
   ```

### No metrics appearing?

1. **Are API keys set?**
   ```bash
   python datadog_config.py
   ```

2. **Test metrics manually:**
   ```bash
   python datadog_metrics.py
   ```

---

## 📚 Learn More

- **Full Documentation**: [DATADOG_README.md](DATADOG_README.md)
- **Example Agent**: [example_instrumented_agent.py](example_instrumented_agent.py)
- **Configuration**: [datadog_config.py](datadog_config.py)

---

## 💡 Pro Tips

1. **Development Mode**: Keep all features enabled
   ```bash
   DD_TRACE_ENABLED=true
   DD_METRICS_ENABLED=true
   DD_LOGGING_ENABLED=true
   ```

2. **Production Mode**: Use sampling to reduce costs
   ```bash
   DD_TRACE_SAMPLE_RATE=0.1  # Sample 10% of traces
   ```

3. **Disable if Needed**: Turn off without code changes
   ```bash
   DD_TRACE_ENABLED=false  # Disables tracing only
   ```

4. **Check Status Anytime**:
   ```bash
   python datadog_config.py
   ```

---

**Need Help?** See [DATADOG_README.md](DATADOG_README.md) for detailed documentation.
