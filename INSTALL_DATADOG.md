# 🔧 Datadog Installation Instructions

## ✅ Recommended: Using UV (Your Project Setup)

Your project uses `uv` for package management. Simply run:

```bash
# Sync all dependencies including new Datadog packages
uv sync

# Or if you need to lock first
uv lock
uv sync
```

This will install all dependencies from `pyproject.toml` including the newly added Datadog packages:
- `ddtrace>=2.18.0`
- `datadog-api-client>=2.31.0`
- `python-json-logger>=2.0.7`

---

## Alternative Methods

### Option 1: Create Virtual Environment (Recommended if not using uv)

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
pip install -e .
```

### Option 2: Use pipx (For isolated installation)

```bash
# Install pipx if not already installed
brew install pipx

# Install packages
pipx install ddtrace
pipx install datadog-api-client
pipx install python-json-logger
```

### Option 3: User Installation (Not recommended)

```bash
pip install --user ddtrace datadog-api-client python-json-logger
```

---

## ✅ Verify Installation

After installation, verify it worked:

```bash
# Check configuration status
python datadog_config.py

# Should show Datadog modules are importable
python -c "import ddtrace, datadog_api_client, pythonjsonlogger; print('✅ All packages installed')"
```

---

## 🚀 Next Steps

Once packages are installed:

1. **Configure API Keys**:
   ```bash
   cp .env.example .env
   # Edit .env with your Datadog keys
   ```

2. **Start Datadog Agent** (for tracing):
   ```bash
   docker run -d --name dd-agent \
     -e DD_API_KEY=your_key \
     -e DD_APM_ENABLED=true \
     -p 8126:8126 \
     datadog/agent:latest
   ```

3. **Test the Integration**:
   ```bash
   python example_instrumented_agent.py
   ```

---

## 📚 Documentation

- **Quick Start**: [DATADOG_QUICKSTART.md](DATADOG_QUICKSTART.md)
- **Full Guide**: [DATADOG_README.md](DATADOG_README.md)
- **Example**: [example_instrumented_agent.py](example_instrumented_agent.py)
