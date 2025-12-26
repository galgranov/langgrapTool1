"""
A2A (Agent-to-Agent) Communication Protocol
Enables direct communication between different agents in the system.
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime


class MessageType(Enum):
    """Types of messages that can be sent between agents."""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"


class AgentRole(Enum):
    """Roles of agents in the system."""
    COMPANY_AGENT = "company_agent"
    PERSON_AGENT = "person_agent"
    COORDINATOR = "coordinator"
    WEATHER_AGENT = "weather_agent"


@dataclass
class A2AMessage:
    """Standard message format for agent-to-agent communication."""
    sender: AgentRole
    receiver: AgentRole
    message_type: MessageType
    content: Dict[str, Any]
    message_id: str
    timestamp: str
    in_reply_to: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "sender": self.sender.value,
            "receiver": self.receiver.value,
            "message_type": self.message_type.value,
            "content": self.content,
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "in_reply_to": self.in_reply_to
        }
    
    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AMessage':
        """Create message from dictionary."""
        return cls(
            sender=AgentRole(data["sender"]),
            receiver=AgentRole(data["receiver"]),
            message_type=MessageType(data["message_type"]),
            content=data["content"],
            message_id=data["message_id"],
            timestamp=data["timestamp"],
            in_reply_to=data.get("in_reply_to")
        )


class MessageBus:
    """Central message bus for routing messages between agents."""
    
    def __init__(self):
        self.message_queue: List[A2AMessage] = []
        self.message_history: List[A2AMessage] = []
        self.agent_handlers: Dict[AgentRole, callable] = {}
    
    def register_agent(self, role: AgentRole, handler: callable):
        """Register an agent's message handler."""
        self.agent_handlers[role] = handler
        print(f"✓ Registered {role.value} with message bus")
    
    def send_message(self, message: A2AMessage):
        """Send a message to another agent."""
        print(f"\n📨 Message sent:")
        print(f"   From: {message.sender.value}")
        print(f"   To: {message.receiver.value}")
        print(f"   Type: {message.message_type.value}")
        print(f"   ID: {message.message_id}")
        
        self.message_history.append(message)
        
        # Route message to receiver
        if message.receiver in self.agent_handlers:
            handler = self.agent_handlers[message.receiver]
            response = handler(message)
            
            if response:
                self.message_history.append(response)
                print(f"\n📬 Response received:")
                print(f"   From: {response.sender.value}")
                print(f"   To: {response.receiver.value}")
                print(f"   In reply to: {response.in_reply_to}")
                return response
        else:
            print(f"   ⚠️  No handler registered for {message.receiver.value}")
        
        return None
    
    def get_conversation(self, message_id: str) -> List[A2AMessage]:
        """Get all messages in a conversation thread."""
        conversation = []
        
        # Find initial message
        initial = next((m for m in self.message_history if m.message_id == message_id), None)
        if initial:
            conversation.append(initial)
            
            # Find all replies
            current_id = message_id
            while True:
                reply = next((m for m in self.message_history if m.in_reply_to == current_id), None)
                if not reply:
                    break
                conversation.append(reply)
                current_id = reply.message_id
        
        return conversation
    
    def print_conversation(self, message_id: str):
        """Print a conversation thread."""
        conversation = self.get_conversation(message_id)
        
        if not conversation:
            print(f"No conversation found for message ID: {message_id}")
            return
        
        print("\n" + "="*80)
        print("CONVERSATION THREAD")
        print("="*80)
        
        for i, msg in enumerate(conversation, 1):
            print(f"\n[{i}] {msg.sender.value} → {msg.receiver.value}")
            print(f"    Type: {msg.message_type.value}")
            print(f"    Time: {msg.timestamp}")
            print(f"    Content: {json.dumps(msg.content, indent=6)}")
        
        print("\n" + "="*80)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get message bus statistics."""
        return {
            "total_messages": len(self.message_history),
            "registered_agents": len(self.agent_handlers),
            "agents": [role.value for role in self.agent_handlers.keys()],
            "message_types": {
                msg_type.value: sum(1 for m in self.message_history if m.message_type == msg_type)
                for msg_type in MessageType
            }
        }


def create_message(
    sender: AgentRole,
    receiver: AgentRole,
    message_type: MessageType,
    content: Dict[str, Any],
    in_reply_to: Optional[str] = None
) -> A2AMessage:
    """Helper function to create a new message."""
    import uuid
    
    return A2AMessage(
        sender=sender,
        receiver=receiver,
        message_type=message_type,
        content=content,
        message_id=str(uuid.uuid4()),
        timestamp=datetime.now().isoformat(),
        in_reply_to=in_reply_to
    )


def create_request(sender: AgentRole, receiver: AgentRole, action: str, params: Dict[str, Any]) -> A2AMessage:
    """Create a request message."""
    return create_message(
        sender=sender,
        receiver=receiver,
        message_type=MessageType.REQUEST,
        content={"action": action, "params": params}
    )


def create_response(sender: AgentRole, receiver: AgentRole, data: Dict[str, Any], in_reply_to: str) -> A2AMessage:
    """Create a response message."""
    return create_message(
        sender=sender,
        receiver=receiver,
        message_type=MessageType.RESPONSE,
        content={"data": data},
        in_reply_to=in_reply_to
    )


def create_notification(sender: AgentRole, receiver: AgentRole, event: str, data: Dict[str, Any]) -> A2AMessage:
    """Create a notification message."""
    return create_message(
        sender=sender,
        receiver=receiver,
        message_type=MessageType.NOTIFICATION,
        content={"event": event, "data": data}
    )


def create_error(sender: AgentRole, receiver: AgentRole, error: str, in_reply_to: str) -> A2AMessage:
    """Create an error message."""
    return create_message(
        sender=sender,
        receiver=receiver,
        message_type=MessageType.ERROR,
        content={"error": error},
        in_reply_to=in_reply_to
    )
