"""
A2A Task and Context Implementation
Based on the official Agent2Agent protocol specification.

Task provides stateful context management for multi-turn conversations.
"""
from typing import Dict, Any, List, Optional, Literal
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid

from a2a_standard_protocol import A2AMessage, AgentRole


# ============================================================================
# Task State
# ============================================================================

class TaskState(Enum):
    """Task lifecycle states as defined in A2A standard."""
    SUBMITTED = "submitted"      # Task has been submitted
    WORKING = "working"          # Task is being processed
    INPUT_REQUIRED = "input-required"  # Requires client input
    COMPLETED = "completed"      # Successfully completed
    CANCELED = "canceled"        # Task was canceled
    FAILED = "failed"           # Task execution failed
    UNKNOWN = "unknown"         # Unknown state


@dataclass
class TaskStatus:
    """Task status with message and timestamp."""
    state: TaskState
    message: Optional[A2AMessage] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "message": self.message.to_dict() if self.message else None,
            "timestamp": self.timestamp
        }


# ============================================================================
# Task (Context Management)
# ============================================================================

@dataclass
class Task:
    """
    Task represents a stateful interaction context.
    
    Key features:
    - Maintains conversation history for context
    - Links related interactions via sessionId
    - Tracks task state through lifecycle
    - Stores artifacts (outputs)
    - Enables multi-turn conversations
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = field(default_factory=lambda: TaskStatus(state=TaskState.SUBMITTED))
    history: List[A2AMessage] = field(default_factory=list)
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, message: A2AMessage):
        """Add a message to the conversation history."""
        self.history.append(message)
        print(f"📝 [Task {self.id[:8]}] Message added to history (total: {len(self.history)})")
    
    def update_status(self, state: TaskState, message: Optional[A2AMessage] = None):
        """Update task status."""
        old_state = self.status.state
        self.status = TaskStatus(state=state, message=message)
        print(f"🔄 [Task {self.id[:8]}] State: {old_state.value} → {state.value}")
    
    def add_artifact(self, artifact: Dict[str, Any]):
        """Add an artifact (output) to the task."""
        self.artifacts.append(artifact)
        print(f"📦 [Task {self.id[:8]}] Artifact added (total: {len(self.artifacts)})")
    
    def get_context(self, max_messages: Optional[int] = None) -> List[A2AMessage]:
        """
        Get conversation context (history).
        
        Args:
            max_messages: Limit to N most recent messages (optional)
        
        Returns:
            List of messages providing context for the current interaction
        """
        if max_messages:
            return self.history[-max_messages:]
        return self.history.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "status": self.status.to_dict(),
            "history": [msg.to_dict() for msg in self.history],
            "artifacts": self.artifacts,
            "metadata": self.metadata
        }
    
    def summary(self) -> str:
        """Get a summary string of the task."""
        return (
            f"Task {self.id[:8]}\n"
            f"  Session: {self.session_id[:8]}\n"
            f"  State: {self.status.state.value}\n"
            f"  Messages: {len(self.history)}\n"
            f"  Artifacts: {len(self.artifacts)}"
        )


# ============================================================================
# Task Manager
# ============================================================================

class TaskManager:
    """
    Manages tasks and sessions for context-aware agent interactions.
    """
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.sessions: Dict[str, List[str]] = {}  # session_id -> task_ids
        print("🎯 Task Manager initialized")
    
    def create_task(self, session_id: Optional[str] = None, metadata: Optional[Dict] = None) -> Task:
        """Create a new task, optionally linked to a session."""
        task = Task(
            session_id=session_id or str(uuid.uuid4()),
            metadata=metadata or {}
        )
        
        self.tasks[task.id] = task
        
        # Link to session
        if task.session_id not in self.sessions:
            self.sessions[task.session_id] = []
        self.sessions[task.session_id].append(task.id)
        
        print(f"✨ [TaskManager] Created task {task.id[:8]} in session {task.session_id[:8]}")
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def get_session_tasks(self, session_id: str) -> List[Task]:
        """Get all tasks in a session."""
        task_ids = self.sessions.get(session_id, [])
        return [self.tasks[tid] for tid in task_ids if tid in self.tasks]
    
    def get_session_context(self, session_id: str, max_messages: Optional[int] = None) -> List[A2AMessage]:
        """
        Get complete context across all tasks in a session.
        
        This enables agents to maintain context across multiple related tasks.
        """
        all_messages = []
        for task in self.get_session_tasks(session_id):
            all_messages.extend(task.history)
        
        if max_messages:
            return all_messages[-max_messages:]
        return all_messages
    
    def print_statistics(self):
        """Print task manager statistics."""
        print("\n" + "="*60)
        print("📊 TASK MANAGER STATISTICS")
        print("="*60)
        print(f"Total Tasks: {len(self.tasks)}")
        print(f"Total Sessions: {len(self.sessions)}")
        print(f"\nTask States:")
        state_counts = {}
        for task in self.tasks.values():
            state = task.status.state.value
            state_counts[state] = state_counts.get(state, 0) + 1
        for state, count in state_counts.items():
            print(f"  {state}: {count}")
        print("="*60)


# ============================================================================
# Context-Aware Message Builder
# ============================================================================

def create_message_with_context(
    role: Literal["user", "agent"],
    text: str,
    task: Task,
    include_context: bool = True,
    max_context_messages: int = 5
) -> A2AMessage:
    """
    Create a message with conversation context from task history.
    
    This allows agents to maintain context across multiple turns.
    """
    from a2a_standard_protocol import TextPart, JsonPart, A2AMessage
    
    parts = []
    
    # Add context summary if requested
    if include_context and task.history:
        context_msgs = task.get_context(max_context_messages)
        context_summary = f"[Context: {len(context_msgs)} previous messages in this conversation]"
        parts.append(TextPart(text=context_summary))
    
    # Add main text
    parts.append(TextPart(text=text))
    
    # Add metadata with task info
    metadata = {
        "task_id": task.id,
        "session_id": task.session_id,
        "message_number": len(task.history) + 1,
        "has_context": include_context
    }
    
    return A2AMessage(role=role, parts=parts, metadata=metadata)


# ============================================================================
# Example Usage
# ============================================================================

def demo_task_context():
    """Demonstrate task and context management."""
    from a2a_standard_protocol import TextPart, A2AMessage
    
    print("\n" + "="*80)
    print("  🎯 A2A TASK & CONTEXT DEMO")
    print("="*80)
    
    # Create task manager
    manager = TaskManager()
    
    # Create a task (automatically creates a session)
    task1 = manager.create_task(metadata={"purpose": "research"})
    print(f"\n{task1.summary()}")
    
    # Simulate a multi-turn conversation
    print("\n--- Multi-Turn Conversation ---")
    
    # Turn 1
    task1.update_status(TaskState.WORKING)
    msg1 = A2AMessage(role="user", parts=[TextPart(text="Research AAPL stock")])
    task1.add_message(msg1)
    
    # Turn 2
    msg2 = A2AMessage(role="agent", parts=[TextPart(text="AAPL price: $273.81")])
    task1.add_message(msg2)
    
    # Turn 3 - with context
    msg3 = create_message_with_context(
        role="user",
        text="What about its competitors?",
        task=task1,
        include_context=True
    )
    task1.add_message(msg3)
    
    print(f"\n📜 Context available: {len(task1.get_context())} messages")
    
    # Create related task in same session
    task2 = manager.create_task(
        session_id=task1.session_id,  # Link to same session
        metadata={"purpose": "follow-up"}
    )
    
    print(f"\n🔗 Tasks in session {task1.session_id[:8]}: {len(manager.get_session_tasks(task1.session_id))}")
    
    # Complete task
    task1.update_status(TaskState.COMPLETED)
    task1.add_artifact({"type": "stock_data", "ticker": "AAPL"})
    
    # Show statistics
    manager.print_statistics()
    
    print("\n✅ Demo Complete!")


if __name__ == "__main__":
    demo_task_context()
