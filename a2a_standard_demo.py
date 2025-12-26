"""
A2A Standard Protocol Demo
Demonstrates the official Agent2Agent protocol format from https://agent2agent.info/
"""
from a2a_standard_protocol import (
    A2AMessage, TextPart, JsonPart,
    AgentRole, AgentMessage, MessageBus,
    create_request_message, create_response_message, create_agent_message
)
from company_tools import get_stock_price_tool, get_company_info_tool
from person_tools import get_person_info_tool
import json


class StandardCompanyAgent:
    """Company agent using standard A2A message format."""
    
    def __init__(self, message_bus: MessageBus):
        self.role = AgentRole.COMPANY_AGENT
        self.message_bus = message_bus
        self.message_bus.register_agent(self.role, self.handle_message)
        print(f"🏢 Company Agent (A2A Standard) initialized")
    
    def handle_message(self, agent_msg: AgentMessage) -> AgentMessage:
        """Handle incoming A2A standard messages."""
        print(f"\n🏢 Company Agent processing A2A standard message...")
        
        msg = agent_msg.message
        
        # Check if this is a request (from user/coordinator)
        if msg.role == "user" and msg.metadata.get("message_type") == "request":
            # Extract request data from JsonPart
            for part in msg.parts:
                if isinstance(part, JsonPart):
                    request_data = part.json
                    action = request_data.get("action")
                    params = request_data.get("params", {})
                    
                    print(f"   Action: {action}")
                    print(f"   Params: {params}")
                    
                    # Handle different actions
                    if action == "get_stock_price":
                        ticker = params.get("ticker")
                        result = get_stock_price_tool.invoke({"ticker": ticker})
                        
                        # Create response in standard format
                        response_msg = create_response_message(
                            data={"stock_price": result},
                            metadata={"action": action, "ticker": ticker}
                        )
                        
                        return create_agent_message(
                            sender=self.role,
                            receiver=agent_msg.sender,
                            message=response_msg,
                            in_reply_to=agent_msg.message_id
                        )
                    
                    elif action == "get_company_info":
                        ticker = params.get("ticker")
                        result = get_company_info_tool.invoke({"ticker": ticker})
                        
                        response_msg = create_response_message(
                            data={"company_info": result},
                            metadata={"action": action, "ticker": ticker}
                        )
                        
                        return create_agent_message(
                            sender=self.role,
                            receiver=agent_msg.sender,
                            message=response_msg,
                            in_reply_to=agent_msg.message_id
                        )
        
        return None


class StandardPersonAgent:
    """Person agent using standard A2A message format."""
    
    def __init__(self, message_bus: MessageBus):
        self.role = AgentRole.PERSON_AGENT
        self.message_bus = message_bus
        self.message_bus.register_agent(self.role, self.handle_message)
        print(f"👤 Person Agent (A2A Standard) initialized")
    
    def handle_message(self, agent_msg: AgentMessage) -> AgentMessage:
        """Handle incoming A2A standard messages."""
        print(f"\n👤 Person Agent processing A2A standard message...")
        
        msg = agent_msg.message
        
        if msg.role == "user" and msg.metadata.get("message_type") == "request":
            for part in msg.parts:
                if isinstance(part, JsonPart):
                    request_data = part.json
                    action = request_data.get("action")
                    params = request_data.get("params", {})
                    
                    print(f"   Action: {action}")
                    print(f"   Params: {params}")
                    
                    if action == "get_person_info":
                        person_name = params.get("person_name")
                        result = get_person_info_tool.invoke({"person_name": person_name})
                        
                        response_msg = create_response_message(
                            data={"person_info": result},
                            metadata={"action": action, "person_name": person_name}
                        )
                        
                        return create_agent_message(
                            sender=self.role,
                            receiver=agent_msg.sender,
                            message=response_msg,
                            in_reply_to=agent_msg.message_id
                        )
        
        return None


def demo_standard_format():
    """Demonstrate the official A2A standard message format."""
    print("\n" + "="*80)
    print("  🤖 A2A Standard Protocol Demo")
    print("  Based on https://agent2agent.info/")
    print("="*80)
    
    # Initialize message bus and agents
    print("\n📡 Initializing Message Bus...")
    message_bus = MessageBus()
    
    print("\n🔧 Initializing Agents...")
    company_agent = StandardCompanyAgent(message_bus)
    person_agent = StandardPersonAgent(message_bus)
    
    print("\n" + "="*80)
    print("  DEMO 1: Standard A2A Message Format")
    print("="*80)
    
    # Create a standard request message
    print("\n📝 Creating standard A2A request message...")
    request_msg = create_request_message(
        action="get_stock_price",
        params={"ticker": "AAPL"},
        metadata={"client": "demo", "request_id": "req-001"}
    )
    
    print(f"\n✅ Standard A2A Message Created:")
    print(json.dumps(request_msg.to_dict(), indent=2))
    
    # Wrap in AgentMessage for routing
    agent_msg = create_agent_message(
        sender=AgentRole.COORDINATOR,
        receiver=AgentRole.COMPANY_AGENT,
        message=request_msg
    )
    
    print("\n📤 Sending message to Company Agent...")
    response = message_bus.send_message(agent_msg)
    
    if response:
        print(f"\n✅ Response Received:")
        print(json.dumps(response.to_dict(), indent=2))
    
    # Show conversation thread
    print("\n" + "="*80)
    print("  DEMO 2: Conversation Threading")
    print("="*80)
    message_bus.print_conversation(agent_msg.message_id)
    
    # Demo with person agent
    print("\n" + "="*80)
    print("  DEMO 3: Person Agent Request")
    print("="*80)
    
    person_request = create_request_message(
        action="get_person_info",
        params={"person_name": "Tim Cook"}
    )
    
    person_agent_msg = create_agent_message(
        sender=AgentRole.COORDINATOR,
        receiver=AgentRole.PERSON_AGENT,
        message=person_request
    )
    
    print("\n📤 Requesting person info for Tim Cook...")
    person_response = message_bus.send_message(person_agent_msg)
    
    if person_response:
        print(f"\n✅ Person Info Retrieved")
        # Extract data from response
        for part in person_response.message.parts:
            if isinstance(part, JsonPart):
                person_data = part.json.get("person_info", {})
                if person_data.get("success"):
                    info = person_data["data"]
                    print(f"   Name: {info.get('title', 'N/A')}")
                    print(f"   Description: {info.get('description', 'N/A')}")
    
    # Show statistics
    print("\n" + "="*80)
    print("  DEMO 4: Message Bus Statistics")
    print("="*80)
    
    stats = message_bus.get_statistics()
    print(f"\n📊 Statistics:")
    print(json.dumps(stats, indent=2))
    
    print("\n" + "="*80)
    print("  ✅ Demo Complete!")
    print("  🌐 This implementation follows the official A2A standard")
    print("  📖 Learn more at: https://agent2agent.info/")
    print("="*80)


if __name__ == "__main__":
    demo_standard_format()
