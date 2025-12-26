"""
Person Agent with A2A Protocol Support
Handles person research requests via agent-to-agent communication.
"""
from typing import Dict, Any
from a2a_protocol import (
    AgentRole, MessageType, A2AMessage, MessageBus,
    create_response, create_error, create_notification
)
from person_tools import (
    get_person_info_tool,
    get_person_career_info_tool,
    search_person_news_tool,
    get_person_social_media_tool
)


class A2APersonAgent:
    """Person research agent with A2A communication."""
    
    def __init__(self, message_bus: MessageBus):
        self.role = AgentRole.PERSON_AGENT
        self.message_bus = message_bus
        self.message_bus.register_agent(self.role, self.handle_message)
        print(f"👤 Person Agent initialized")
    
    def handle_message(self, message: A2AMessage) -> A2AMessage:
        """Handle incoming messages."""
        print(f"\n👤 Person Agent processing message...")
        
        if message.message_type == MessageType.REQUEST:
            return self._handle_request(message)
        elif message.message_type == MessageType.NOTIFICATION:
            return self._handle_notification(message)
        
        return None
    
    def _handle_request(self, message: A2AMessage) -> A2AMessage:
        """Handle request messages."""
        content = message.content
        action = content.get("action")
        params = content.get("params", {})
        
        print(f"   Action: {action}")
        print(f"   Params: {params}")
        
        try:
            if action == "get_person_info":
                person_name = params.get("person_name")
                result = get_person_info_tool.invoke({"person_name": person_name})
                
                return create_response(
                    sender=self.role,
                    receiver=message.sender,
                    data={"person_info": result},
                    in_reply_to=message.message_id
                )
            
            elif action == "get_career_info":
                person_name = params.get("person_name")
                result = get_person_career_info_tool.invoke({"person_name": person_name})
                
                return create_response(
                    sender=self.role,
                    receiver=message.sender,
                    data={"career_info": result},
                    in_reply_to=message.message_id
                )
            
            elif action == "get_news":
                person_name = params.get("person_name")
                result = search_person_news_tool.invoke({"person_name": person_name})
                
                return create_response(
                    sender=self.role,
                    receiver=message.sender,
                    data={"news_info": result},
                    in_reply_to=message.message_id
                )
            
            elif action == "get_social_media":
                person_name = params.get("person_name")
                result = get_person_social_media_tool.invoke({"person_name": person_name})
                
                return create_response(
                    sender=self.role,
                    receiver=message.sender,
                    data={"social_media": result},
                    in_reply_to=message.message_id
                )
            
            elif action == "full_research":
                person_name = params.get("person_name")
                
                # Get all person data
                person_info = get_person_info_tool.invoke({"person_name": person_name})
                career_info = get_person_career_info_tool.invoke({"person_name": person_name})
                news_info = search_person_news_tool.invoke({"person_name": person_name})
                social_media = get_person_social_media_tool.invoke({"person_name": person_name})
                
                return create_response(
                    sender=self.role,
                    receiver=message.sender,
                    data={
                        "person_name": person_name,
                        "person_info": person_info,
                        "career_info": career_info,
                        "news_info": news_info,
                        "social_media": social_media
                    },
                    in_reply_to=message.message_id
                )
            
            elif action == "research_executive":
                # Special action for researching company executives
                name = params.get("name")
                title = params.get("title", "")
                
                print(f"   Researching executive: {name} ({title})")
                
                person_info = get_person_info_tool.invoke({"person_name": name})
                career_info = get_person_career_info_tool.invoke({"person_name": name})
                
                return create_response(
                    sender=self.role,
                    receiver=message.sender,
                    data={
                        "name": name,
                        "title": title,
                        "person_info": person_info,
                        "career_info": career_info
                    },
                    in_reply_to=message.message_id
                )
            
            else:
                return create_error(
                    sender=self.role,
                    receiver=message.sender,
                    error=f"Unknown action: {action}",
                    in_reply_to=message.message_id
                )
        
        except Exception as e:
            return create_error(
                sender=self.role,
                receiver=message.sender,
                error=f"Error processing request: {str(e)}",
                in_reply_to=message.message_id
            )
    
    def _handle_notification(self, message: A2AMessage) -> None:
        """Handle notification messages."""
        event = message.content.get("event")
        print(f"   Notification: {event}")
        return None
