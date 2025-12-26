"""
A2A Standard Protocol Implementation
Based on the official Agent2Agent protocol specification from https://agent2agent.info/

This implementation follows the standard message format with:
- Message: role + parts[] + metadata
- Part: Atomic content units (TextPart, JsonPart, FilePart, etc.)
"""
from typing import Dict, Any, List, Optional, Union, Literal
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime
import uuid


# ============================================================================
# Part Types (Atomic Content Units)
# ============================================================================

@dataclass
class TextPart:
    """Plain text content part."""
    type: Literal["text", "text/plain"] = "text"
    text: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "text": self.text}


@dataclass
class JsonPart:
    """Structured JSON data part."""
    type: Literal["json", "application/json"] = "json"
    json: Any = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "json": self.json}


@dataclass
class FilePart:
    """File reference or content part."""
    type: str = "file"  # Can be "file" or MIME type like "image/jpeg"
    uri: Optional[str] = None
    data: Optional[str] = None  # Base64 encoded content
    filename: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"type": self.type}
        if self.uri:
            result["uri"] = self.uri
        if self.data:
            result["data"] = self.data
        if self.filename:
            result["filename"] = self.filename
        return result


# Type alias for any Part type
Part = Union[TextPart, JsonPart, FilePart]


# ============================================================================
# Message (Standard A2A Format)
# ============================================================================

@dataclass
class A2AMessage:
    """
    Standard A2A Message format.
    
    A Message is the fundamental communication unit used to transmit
    non-Artifact content between agents.
    
    Structure:
    - role: The role of the message sender ("user" or "agent")
    - parts: Array of Part objects (text, json, file, etc.)
    - metadata: Optional metadata for additional information
    """
    role: Literal["user", "agent"]
    parts: List[Part] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "role": self.role,
            "parts": [part.to_dict() for part in self.parts],
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AMessage':
        """Create message from dictionary."""
        parts = []
        for part_data in data.get("parts", []):
            part_type = part_data.get("type", "")
            
            if part_type in ["text", "text/plain"]:
                parts.append(TextPart(type=part_type, text=part_data.get("text", "")))
            elif part_type in ["json", "application/json"]:
                parts.append(JsonPart(type=part_type, json=part_data.get("json")))
            elif "file" in part_type or "/" in part_type:
                parts.append(FilePart(
                    type=part_type,
                    uri=part_data.get("uri"),
                    data=part_data.get("data"),
                    filename=part_data.get("filename")
                ))
        
        return cls(
            role=data["role"],
            parts=parts,
            metadata=data.get("metadata", {})
        )


# ============================================================================
# Agent Communication Layer
# ============================================================================

class AgentRole(Enum):
    """Agent roles in the system."""
    COMPANY_AGENT = "company_agent"
    PERSON_AGENT = "person_agent"
    COORDINATOR = "coordinator"
    WEATHER_AGENT = "weather_agent"


@dataclass
class AgentMessage:
    """
    Extended message format for agent-to-agent routing.
    
    Wraps the standard A2A Message with routing information.
    """
    message: A2AMessage
    sender: AgentRole
    receiver: AgentRole
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    in_reply_to: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message.to_dict(),
            "sender": self.sender.value,
            "receiver": self.receiver.value,
            "message_id": self.message_id,
            "timestamp": self.timestamp,
            "in_reply_to": self.in_reply_to
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# ============================================================================
# Message Bus
# ============================================================================

class MessageBus:
    """Central message bus for routing A2A messages between agents."""
    
    def __init__(self, verbose: bool = True):
        self.message_history: List[AgentMessage] = []
        self.agent_handlers: Dict[AgentRole, callable] = {}
        self.verbose = verbose
        self._log("🚀 Message Bus initialized")
    
    def _log(self, message: str, level: str = "INFO"):
        """Internal logging method."""
        if self.verbose:
            icons = {"INFO": "ℹ️", "SEND": "📤", "RECV": "📥", "SUCCESS": "✅", "ERROR": "❌", "WARN": "⚠️"}
            icon = icons.get(level, "•")
            print(f"{icon} [MessageBus] {message}")
    
    def register_agent(self, role: AgentRole, handler: callable):
        """Register an agent's message handler."""
        self.agent_handlers[role] = handler
        self._log(f"Agent registered: {role.value}", "SUCCESS")
    
    def send_message(self, agent_message: AgentMessage) -> Optional[AgentMessage]:
        """Send a message to another agent with detailed logging."""
        self._log("="*60, "INFO")
        self._log(f"SENDING MESSAGE", "SEND")
        self._log(f"  Message ID: {agent_message.message_id}", "INFO")
        self._log(f"  From: {agent_message.sender.value}", "INFO")
        self._log(f"  To: {agent_message.receiver.value}", "INFO")
        self._log(f"  Role: {agent_message.message.role}", "INFO")
        self._log(f"  Timestamp: {agent_message.timestamp}", "INFO")
        
        # Log message parts
        self._log(f"  Parts ({len(agent_message.message.parts)}):", "INFO")
        for i, part in enumerate(agent_message.message.parts, 1):
            part_type = part.type
            if isinstance(part, TextPart):
                preview = part.text[:50] + "..." if len(part.text) > 50 else part.text
                self._log(f"    [{i}] TextPart: \"{preview}\"", "INFO")
            elif isinstance(part, JsonPart):
                self._log(f"    [{i}] JsonPart: {list(part.json.keys()) if isinstance(part.json, dict) else 'data'}", "INFO")
            elif isinstance(part, FilePart):
                self._log(f"    [{i}] FilePart: {part.filename or part.uri or 'embedded'}", "INFO")
        
        # Log metadata if present
        if agent_message.message.metadata:
            self._log(f"  Metadata: {agent_message.message.metadata}", "INFO")
        
        if agent_message.in_reply_to:
            self._log(f"  In Reply To: {agent_message.in_reply_to}", "INFO")
        
        # Add to history
        self.message_history.append(agent_message)
        self._log(f"Message added to history (total: {len(self.message_history)})", "INFO")
        
        # Route message to receiver
        if agent_message.receiver in self.agent_handlers:
            self._log(f"Routing to handler: {agent_message.receiver.value}", "INFO")
            handler = self.agent_handlers[agent_message.receiver]
            
            try:
                response = handler(agent_message)
                
                if response:
                    self.message_history.append(response)
                    self._log("="*60, "INFO")
                    self._log(f"RESPONSE RECEIVED", "RECV")
                    self._log(f"  Message ID: {response.message_id}", "INFO")
                    self._log(f"  From: {response.sender.value}", "INFO")
                    self._log(f"  To: {response.receiver.value}", "INFO")
                    self._log(f"  Role: {response.message.role}", "INFO")
                    self._log(f"  Parts: {len(response.message.parts)}", "INFO")
                    self._log(f"  In Reply To: {response.in_reply_to}", "INFO")
                    self._log("="*60, "INFO")
                    return response
                else:
                    self._log("No response generated", "WARN")
            except Exception as e:
                self._log(f"Error in handler: {str(e)}", "ERROR")
                raise
        else:
            self._log(f"No handler registered for: {agent_message.receiver.value}", "ERROR")
        
        return None
    
    def get_conversation(self, message_id: str) -> List[AgentMessage]:
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
        print("CONVERSATION THREAD (A2A Standard Format)")
        print("="*80)
        
        for i, agent_msg in enumerate(conversation, 1):
            msg = agent_msg.message
            print(f"\n[{i}] {agent_msg.sender.value} → {agent_msg.receiver.value}")
            print(f"    Role: {msg.role}")
            print(f"    Time: {agent_msg.timestamp}")
            print(f"    Parts:")
            for j, part in enumerate(msg.parts, 1):
                print(f"      [{j}] {part.to_dict()}")
            if msg.metadata:
                print(f"    Metadata: {msg.metadata}")
        
        print("\n" + "="*80)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get message bus statistics."""
        role_counts = {}
        for msg in self.message_history:
            role = msg.message.role
            role_counts[role] = role_counts.get(role, 0) + 1
        
        return {
            "total_messages": len(self.message_history),
            "registered_agents": len(self.agent_handlers),
            "agents": [role.value for role in self.agent_handlers.keys()],
            "message_roles": role_counts
        }


# ============================================================================
# Helper Functions
# ============================================================================

def create_text_message(role: Literal["user", "agent"], text: str, metadata: Optional[Dict] = None) -> A2AMessage:
    """Create a message with text content."""
    return A2AMessage(
        role=role,
        parts=[TextPart(text=text)],
        metadata=metadata or {}
    )


def create_json_message(role: Literal["user", "agent"], data: Any, metadata: Optional[Dict] = None) -> A2AMessage:
    """Create a message with JSON content."""
    return A2AMessage(
        role=role,
        parts=[JsonPart(json=data)],
        metadata=metadata or {}
    )


def create_request_message(action: str, params: Dict[str, Any], metadata: Optional[Dict] = None) -> A2AMessage:
    """Create a request message with action and parameters."""
    request_data = {
        "action": action,
        "params": params
    }
    meta = metadata or {}
    meta["message_type"] = "request"
    
    return A2AMessage(
        role="user",  # Client/coordinator role
        parts=[
            TextPart(text=f"Request: {action}"),
            JsonPart(json=request_data)
        ],
        metadata=meta
    )


def create_response_message(data: Any, metadata: Optional[Dict] = None) -> A2AMessage:
    """Create a response message with data."""
    meta = metadata or {}
    meta["message_type"] = "response"
    
    return A2AMessage(
        role="agent",  # Agent role
        parts=[JsonPart(json=data)],
        metadata=meta
    )


def create_agent_message(
    sender: AgentRole,
    receiver: AgentRole,
    message: A2AMessage,
    in_reply_to: Optional[str] = None
) -> AgentMessage:
    """Create an agent message for routing."""
    return AgentMessage(
        message=message,
        sender=sender,
        receiver=receiver,
        in_reply_to=in_reply_to
    )
