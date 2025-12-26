# 🌐 A2A Standard Protocol Implementation

## Overview

This implementation follows the **official Agent2Agent (A2A) protocol** specification from **https://agent2agent.info/** for maximum interoperability with other A2A-compatible systems.

## What is the A2A Standard?

The Agent2Agent protocol is an open standard that enables agents to discover, interact, and collaborate. It defines:

- **Message Format** - Standard structure for communication
- **Part Types** - Atomic content units (text, JSON, files)
- **Roles** - Agent vs User/Client communication patterns
- **Tasks** - Stateful interaction processes
- **Artifacts** - Final outputs and results

## Our Implementation

We've implemented the **Message** and **Part** concepts from the A2A standard for agent-to-agent communication.

### Standard Message Format

```python
{
  "role": "user" | "agent",  # Sender role
  "parts": [                  # Array of content parts
    {"type": "text", "text": "..."},
    {"type": "json", "json": {...}}
  ],
  "metadata": {...}           # Additional information
}
```

### Part Types Supported

1. **TextPart** - Plain text content
   ```python
   {"type": "text", "text": "Request: get_stock_price"}
   ```

2. **JsonPart** - Structured JSON data
   ```python
   {"type": "json", "json": {"action": "...", "params": {...}}}
   ```

3. **FilePart** - File references or embedded content
   ```python
   {"type": "image/jpeg", "uri": "...", "filename": "..."}
   ```

## Key Differences from Custom Format

### Before (Custom Format)
```python
{
  "sender": "coordinator",
  "receiver": "company_agent",
  "message_type": "request",
  "content": {"action": "...", "params": {...}}
}
```

### After (A2A Standard)
```python
{
  "role": "user",
  "parts": [
    {"type": "text", "text": "Request: ..."},
    {"type": "json", "json": {"action": "...", "params": {...}}}
  ],
  "metadata": {"message_type": "request"}
}
```

## Benefits of Standard Compliance

### 1. **Interoperability**
Compatible with any A2A-compliant agent or system

### 2. **Multi-Modal Support**
Easily combine text, JSON, files, and other content types

### 3. **Extensibility**
Add new Part types without breaking existing code

### 4. **Community Standard**
Part of a growing ecosystem of compatible agents

### 5. **Future-Proof**
Aligned with industry standards and best practices

## Files

- **a2a_standard_protocol.py** - Core implementation following official spec
- **a2a_standard_demo.py** - Interactive demo showing standard format
- **A2A_STANDARD_README.md** - This file

## Usage Example

```python
from a2a_standard_protocol import (
    create_request_message,
    create_agent_message,
    AgentRole, MessageBus
)

# Create standard A2A message
request = create_request_message(
    action="get_stock_price",
    params={"ticker": "AAPL"}
)

# Wrap for routing
agent_msg = create_agent_message(
    sender=AgentRole.COORDINATOR,
    receiver=AgentRole.COMPANY_AGENT,
    message=request
)

# Send via message bus
response = message_bus.send_message(agent_msg)
```

## Running the Demo

```bash
python a2a_standard_demo.py
```

**Output shows:**
- Standard A2A message format
- Request/Response pattern
- Conversation threading
- Multi-part messages
- Statistics tracking

## Comparison: Custom vs Standard

| Feature | Custom | A2A Standard |
|---------|--------|--------------|
| **Interoperability** | Internal only | Any A2A system |
| **Message Structure** | Flat | Hierarchical (parts) |
| **Content Types** | Limited | Extensible |
| **Roles** | Custom enum | Standard (user/agent) |
| **Metadata** | Mixed with content | Separate field |
| **File Support** | Basic | Rich (URI, data, MIME) |
| **Multi-modal** | No | Yes |

## Standard Compliance

✅ **Message Format** - role + parts[] + metadata  
✅ **TextPart** - Plain text content  
✅ **JsonPart** - Structured data  
✅ **FilePart** - File references  
✅ **Metadata** - Extensible information  
✅ **Routing Layer** - Agent-to-agent communication  
✅ **Conversation Threading** - Message relationships  
✅ **Message History** - Complete audit trail  

## Future Enhancements

Following additional A2A concepts:

- [ ] **Task** - Stateful interaction processes
- [ ] **Artifact** - Final output representation
- [ ] **AgentCard** - Agent capability description
- [ ] **FormPart** - Interactive forms
- [ ] **IFramePart** - Embedded content
- [ ] **Streaming** - Real-time updates

## Resources

- **Official Specification**: https://agent2agent.info/
- **Message Concept**: https://agent2agent.info/docs/concepts/message/
- **Part Concept**: https://agent2agent.info/docs/concepts/part/
- **Core Concepts**: https://agent2agent.info/docs/concepts/

## Example Output

```json
{
  "role": "user",
  "parts": [
    {
      "type": "text",
      "text": "Request: get_stock_price"
    },
    {
      "type": "json",
      "json": {
        "action": "get_stock_price",
        "params": {"ticker": "AAPL"}
      }
    }
  ],
  "metadata": {
    "message_type": "request",
    "client": "demo"
  }
}
```

## Integration

Both implementations coexist:
- **a2a_protocol.py** - Original custom format (backwards compatible)
- **a2a_standard_protocol.py** - Official A2A standard (interoperable)

Choose based on your needs:
- Use **standard** for interoperability with other A2A systems
- Use **custom** for internal-only agent communication

## Contributing

To add new Part types:

1. Create dataclass extending base Part structure
2. Implement `to_dict()` method
3. Add to `from_dict()` parser
4. Update type hints
5. Document usage

## License

Part of the LangGraph agents project, following A2A open standard.

---

**Created**: 2025-12-26  
**Standard Version**: A2A v1.0 (https://agent2agent.info/)  
**Implementation**: Python 3.13+
