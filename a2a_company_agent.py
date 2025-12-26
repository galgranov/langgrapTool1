"""
Company Agent with A2A Protocol Support
Handles company research requests via agent-to-agent communication.
"""
from typing import Dict, Any
from a2a_protocol import (
    AgentRole, MessageType, A2AMessage, MessageBus,
    create_response, create_error, create_notification
)
from company_tools import (
    get_company_info_tool,
    get_stock_price_tool,
    get_company_executives_tool
)


class A2ACompanyAgent:
    """Company research agent with A2A communication."""
    
    def __init__(self, message_bus: MessageBus):
        self.role = AgentRole.COMPANY_AGENT
        self.message_bus = message_bus
        self.message_bus.register_agent(self.role, self.handle_message)
        print(f"🏢 Company Agent initialized")
    
    def handle_message(self, message: A2AMessage) -> A2AMessage:
        """Handle incoming messages."""
        print(f"\n🏢 Company Agent processing message...")
        
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
            if action == "get_company_info":
                ticker = params.get("ticker")
                result = get_company_info_tool.invoke({"ticker": ticker})
                
                return create_response(
                    sender=self.role,
                    receiver=message.sender,
                    data={"company_info": result},
                    in_reply_to=message.message_id
                )
            
            elif action == "get_stock_price":
                ticker = params.get("ticker")
                result = get_stock_price_tool.invoke({"ticker": ticker})
                
                return create_response(
                    sender=self.role,
                    receiver=message.sender,
                    data={"stock_price": result},
                    in_reply_to=message.message_id
                )
            
            elif action == "get_executives":
                ticker = params.get("ticker")
                result = get_company_executives_tool.invoke({"ticker": ticker})
                
                return create_response(
                    sender=self.role,
                    receiver=message.sender,
                    data={"executives": result},
                    in_reply_to=message.message_id
                )
            
            elif action == "full_research":
                ticker = params.get("ticker")
                
                # Get all company data
                company_info = get_company_info_tool.invoke({"ticker": ticker})
                stock_price = get_stock_price_tool.invoke({"ticker": ticker})
                executives = get_company_executives_tool.invoke({"ticker": ticker})
                
                return create_response(
                    sender=self.role,
                    receiver=message.sender,
                    data={
                        "ticker": ticker,
                        "company_info": company_info,
                        "stock_price": stock_price,
                        "executives": executives
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
