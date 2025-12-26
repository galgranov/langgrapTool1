# 🤖 A2A (Agent-to-Agent) Communication Protocol

## Overview

The A2A Protocol enables direct communication between different AI agents in a distributed system. Agents can send requests, receive responses, broadcast notifications, and coordinate complex multi-step workflows without central orchestration.

## Key Concepts

### Message Bus
A central routing system that:
- Routes messages between agents
- Maintains message history
- Tracks conversation threads
- Provides statistics and monitoring

### Message Types

1. **REQUEST** - Request an action or data from another agent
2. **RESPONSE** - Reply to a request with data or results
3. **NOTIFICATION** - Broadcast information to other agents
4. **ERROR** - Report errors in processing

### Agent Roles

- **COMPANY_AGENT** - Handles company research and financial data
- **PERSON_AGENT** - Handles biographical and person research
- **COORDINATOR** - Orchestrates multi-agent workflows
- **WEATHER_AGENT** - Handles weather information (extensible)

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Message Bus                          │
│  - Routes messages between agents                        │
│  - Maintains conversation history                        │
│  - Provides statistics and monitoring                    │
└─────────────────────────────────────────────────────────┘
           │              │              │
           ▼              ▼              ▼
    ┌───────────┐  ┌───────────┐  ┌──────────────┐
    │ Company   │  │  Person   │  │ Coordinator  │
    │  Agent    │  │  Agent    │  │    Agent     │
    └───────────┘  └───────────┘  └──────────────┘
```

## Message Format

```python
{
  "sender": "coordinator",
  "receiver": "company_agent",
  "message_type": "request",
  "content": {
    "action": "get_stock_price",
    "params": {"ticker": "AAPL"}
  },
  "message_id": "uuid-string",
  "timestamp": "2025-12-26T12:00:00",
  "in_reply_to": "parent-message-id"  # Optional
}
```

## Components

### 1. a2a_protocol.py
Core protocol implementation with:
- **A2AMessage** - Message dataclass
- **MessageBus** - Central message router
- **MessageType** - Enum of message types
- **AgentRole** - Enum of agent roles
- Helper functions for creating messages

### 2. a2a_company_agent.py
Company research agent supporting:
- `get_company_info` - Company profile
- `get_stock_price` - Stock prices
- `get_executives` - Company executives
- `full_research` - Complete company analysis

### 3. a2a_person_agent.py
Person research agent supporting:
- `get_person_info` - Biographical information
- `get_career_info` - Career history
- `get_news` - Recent news
- `get_social_media` - Social media links
- `full_research` - Complete person analysis
- `research_executive` - Research company executives

### 4. a2a_coordinator.py
Orchestrator agent that:
- Coordinates multi-agent workflows
- Manages complex research pipelines
- Broadcasts notifications
- Compiles results from multiple agents

### 5. a2a_demo.py
Interactive demo with:
- Direct communication examples
- Multi-agent workflow demonstrations
- Interactive mode for testing
- Statistics and monitoring

## Usage Examples

### Example 1: Direct Agent Communication

```python
from a2a_protocol import MessageBus, create_request, AgentRole
from a2a_company_agent import A2ACompanyAgent

# Initialize
message_bus = MessageBus()
company_agent = A2ACompanyAgent(message_bus)

# Send request
msg = create_request(
    sender=AgentRole.COORDINATOR,
    receiver=AgentRole.COMPANY_AGENT,
    action="get_stock_price",
    params={"ticker": "AAPL"}
)

response = message_bus.send_message(msg)
print(response.content)
```

### Example 2: Coordinator Workflow

```python
from a2a_protocol import MessageBus
from a2a_company_agent import A2ACompanyAgent
from a2a_person_agent import A2APersonAgent
from a2a_coordinator import A2ACoordinator

# Initialize system
message_bus = MessageBus()
company_agent = A2ACompanyAgent(message_bus)
person_agent = A2APersonAgent(message_bus)
coordinator = A2ACoordinator(message_bus)

# Execute complex workflow
results = coordinator.research_company_and_executives("AAPL")
```

### Example 3: Broadcasting Notifications

```python
coordinator.notify_agents(
    event="research_started",
    data={"ticker": "TSLA", "timestamp": "2025-12-26"}
)
```

## Running the Demo

### All Demos Mode
```bash
python a2a_demo.py
# Select: 1 (Run all demos)
```

### Interactive Mode
```bash
python a2a_demo.py
# Select: 2 (Interactive mode)

# Available commands:
company AAPL          # Research company
person Tim Cook       # Research person
full TSLA            # Company + executives
stats                # Show statistics
exit                 # Exit
```

### Specific Demo Mode
```bash
python a2a_demo.py
# Select: 3 (Specific demo)
# Choose demo number
```

## Features

### ✅ Implemented

1. **Message Routing** - Automatic routing between agents
2. **Request/Response** - Synchronous communication pattern
3. **Notifications** - Broadcast messages to all agents
4. **Error Handling** - Standardized error reporting
5. **Conversation Threading** - Track related messages
6. **Message History** - Complete audit trail
7. **Statistics** - Monitor system activity
8. **Multi-Agent Workflows** - Coordinator orchestration

### 🚧 Future Enhancements

1. **Async Communication** - Non-blocking message handling
2. **Message Queuing** - Priority and delayed messages
3. **Agent Discovery** - Dynamic agent registration
4. **Message Persistence** - Database storage
5. **Authentication** - Agent identity verification
6. **Rate Limiting** - Prevent agent overload
7. **Message Encryption** - Secure communication
8. **Event Subscriptions** - Subscribe to specific events
9. **Distributed Bus** - Multi-node support
10. **WebSocket Support** - Real-time communication

## Benefits of A2A Protocol

### 1. Decoupling
Agents don't need to know implementation details of other agents, only their message interface.

### 2. Scalability
Easy to add new agents without modifying existing ones.

### 3. Flexibility
Agents can be written in different languages (with proper message bus adapters).

### 4. Testability
Easy to test agents in isolation by mocking messages.

### 5. Observability
Complete message history provides audit trail and debugging.

### 6. Extensibility
New message types and agents can be added without breaking changes.

## Message Flow Example

```
Coordinator: "I need company info and executives for TSLA"
     │
     ├─► Company Agent: "Get company info for TSLA"
     │        └─► Returns company profile
     │
     ├─► Company Agent: "Get executives for TSLA"
     │        └─► Returns list of 10 executives
     │
     ├─► Person Agent: "Research Elon Musk"
     │        └─► Returns biographical info
     │
     ├─► Person Agent: "Research Zachary Kirkhorn"
     │        └─► Returns biographical info
     │
     └─► [Repeats for all executives...]
     
Coordinator: Compiles all results and returns
```

## Error Handling

The protocol handles errors gracefully:

```python
# Agent returns error message
return create_error(
    sender=self.role,
    receiver=message.sender,
    error="Failed to fetch data: API timeout",
    in_reply_to=message.message_id
)
```

## Monitoring & Statistics

```python
stats = message_bus.get_statistics()
# {
#   "total_messages": 45,
#   "registered_agents": 3,
#   "agents": ["company_agent", "person_agent", "coordinator"],
#   "message_types": {
#     "request": 20,
#     "response": 20,
#     "notification": 3,
#     "error": 2
#   }
# }
```

## Conversation Threading

View entire conversation threads:

```python
message_bus.print_conversation(message_id)
```

Output:
```
==================================================
CONVERSATION THREAD
==================================================

[1] coordinator → company_agent
    Type: request
    Time: 2025-12-26T12:00:00
    Content: {"action": "get_stock_price", ...}

[2] company_agent → coordinator
    Type: response
    Time: 2025-12-26T12:00:01
    Content: {"data": {"stock_price": ...}}
==================================================
```

## Best Practices

### 1. Always Handle Errors
```python
try:
    result = process_request(message)
    return create_response(...)
except Exception as e:
    return create_error(...)
```

### 2. Use Meaningful Message IDs
Message IDs are UUIDs for unique identification.

### 3. Check Message Types
```python
if message.message_type == MessageType.REQUEST:
    return self._handle_request(message)
elif message.message_type == MessageType.NOTIFICATION:
    self._handle_notification(message)
```

### 4. Reply to Requests
Always include `in_reply_to` in responses:
```python
return create_response(
    sender=self.role,
    receiver=message.sender,
    data=result,
    in_reply_to=message.message_id
)
```

### 5. Log Important Events
```python
print(f"Processing {message.message_type.value} from {message.sender.value}")
```

## Integration with Existing Agents

The A2A system works alongside existing standalone agents:
- Original agents continue to work independently
- A2A versions enable agent-to-agent communication
- Both can coexist in the same codebase

## Performance Considerations

- Messages are processed synchronously (blocking)
- Large message volumes may require async implementation
- Consider implementing message queuing for high-throughput scenarios

## File Structure

```
lang/
├── a2a_protocol.py          # Core A2A protocol
├── a2a_company_agent.py     # Company agent with A2A
├── a2a_person_agent.py      # Person agent with A2A
├── a2a_coordinator.py       # Coordinator agent
├── a2a_demo.py              # Interactive demo
└── A2A_README.md            # This file
```

## Contributing

To add a new agent:

1. Create agent class with `__init__(message_bus)`
2. Register with message bus in `__init__`
3. Implement `handle_message(message)` method
4. Add agent role to `AgentRole` enum
5. Handle REQUEST, RESPONSE, and NOTIFICATION types

## License

Part of the LangGraph agents project.

---

**Created**: 2025-12-26  
**Version**: 1.0.0  
**Author**: LangGraph Team
