"""
Coordinator Agent with A2A Protocol
Orchestrates communication between multiple agents.
"""
from typing import Dict, Any, List
from a2a_protocol import (
    AgentRole, MessageType, A2AMessage, MessageBus,
    create_request, create_response, create_notification
)


class A2ACoordinator:
    """Coordinator agent that orchestrates multi-agent workflows."""
    
    def __init__(self, message_bus: MessageBus):
        self.role = AgentRole.COORDINATOR
        self.message_bus = message_bus
        self.message_bus.register_agent(self.role, self.handle_message)
        print(f"🎯 Coordinator Agent initialized")
    
    def handle_message(self, message: A2AMessage) -> A2AMessage:
        """Handle incoming messages."""
        print(f"\n🎯 Coordinator processing message...")
        
        if message.message_type == MessageType.REQUEST:
            return self._handle_request(message)
        elif message.message_type == MessageType.RESPONSE:
            return self._handle_response(message)
        
        return None
    
    def _handle_request(self, message: A2AMessage) -> A2AMessage:
        """Handle request messages."""
        content = message.content
        action = content.get("action")
        
        print(f"   Action: {action}")
        
        # Coordinator doesn't directly handle requests
        # It orchestrates them between other agents
        return None
    
    def _handle_response(self, message: A2AMessage) -> None:
        """Handle response messages."""
        print(f"   Processing response from {message.sender.value}")
        return None
    
    def research_company_and_executives(self, ticker: str) -> Dict[str, Any]:
        """
        Coordinate a complex workflow:
        1. Ask Company Agent for company info and executives
        2. For each executive, ask Person Agent for biographical info
        3. Compile and return all results
        """
        print(f"\n{'='*80}")
        print(f"🎯 COORDINATOR: Starting company & executive research for {ticker}")
        print(f"{'='*80}")
        
        results = {
            "ticker": ticker,
            "company_data": None,
            "executives_research": []
        }
        
        # Step 1: Request company data from Company Agent
        print(f"\n[Step 1] Requesting company data from Company Agent...")
        msg = create_request(
            sender=self.role,
            receiver=AgentRole.COMPANY_AGENT,
            action="full_research",
            params={"ticker": ticker}
        )
        
        response = self.message_bus.send_message(msg)
        
        if response and response.message_type == MessageType.RESPONSE:
            results["company_data"] = response.content["data"]
            
            # Step 2: Get executives list
            executives_data = results["company_data"].get("executives", {})
            
            if executives_data.get("success"):
                executives_list = executives_data["data"].get("executives", [])
                
                print(f"\n[Step 2] Found {len(executives_list)} executives")
                print(f"[Step 3] Requesting biographical research from Person Agent...")
                
                # Step 3: Research each executive via Person Agent
                for idx, exec_info in enumerate(executives_list[:5], 1):  # Limit to 5 for demo
                    name = exec_info.get("name")
                    title = exec_info.get("title")
                    
                    print(f"\n  [{idx}] Researching: {name}")
                    
                    msg = create_request(
                        sender=self.role,
                        receiver=AgentRole.PERSON_AGENT,
                        action="research_executive",
                        params={"name": name, "title": title}
                    )
                    
                    person_response = self.message_bus.send_message(msg)
                    
                    if person_response and person_response.message_type == MessageType.RESPONSE:
                        results["executives_research"].append({
                            "executive": exec_info,
                            "research": person_response.content["data"]
                        })
            else:
                print(f"\n  ⚠️  No executives data available")
        
        return results
    
    def request_person_research(self, person_name: str) -> Dict[str, Any]:
        """Request full person research from Person Agent."""
        print(f"\n{'='*80}")
        print(f"🎯 COORDINATOR: Requesting person research for {person_name}")
        print(f"{'='*80}")
        
        msg = create_request(
            sender=self.role,
            receiver=AgentRole.PERSON_AGENT,
            action="full_research",
            params={"person_name": person_name}
        )
        
        response = self.message_bus.send_message(msg)
        
        if response and response.message_type == MessageType.RESPONSE:
            return response.content["data"]
        
        return {}
    
    def request_company_research(self, ticker: str) -> Dict[str, Any]:
        """Request full company research from Company Agent."""
        print(f"\n{'='*80}")
        print(f"🎯 COORDINATOR: Requesting company research for {ticker}")
        print(f"{'='*80}")
        
        msg = create_request(
            sender=self.role,
            receiver=AgentRole.COMPANY_AGENT,
            action="full_research",
            params={"ticker": ticker}
        )
        
        response = self.message_bus.send_message(msg)
        
        if response and response.message_type == MessageType.RESPONSE:
            return response.content["data"]
        
        return {}
    
    def notify_agents(self, event: str, data: Dict[str, Any]):
        """Send notification to all registered agents."""
        print(f"\n🎯 COORDINATOR: Broadcasting notification - {event}")
        
        for agent_role in [AgentRole.COMPANY_AGENT, AgentRole.PERSON_AGENT]:
            msg = create_notification(
                sender=self.role,
                receiver=agent_role,
                event=event,
                data=data
            )
            self.message_bus.send_message(msg)
