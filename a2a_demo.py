"""
A2A Protocol Demo
Demonstrates agent-to-agent communication with the message bus.
"""
from a2a_protocol import MessageBus, AgentRole, create_request
from a2a_company_agent import A2ACompanyAgent
from a2a_person_agent import A2APersonAgent
from a2a_coordinator import A2ACoordinator
import json


def print_section(title: str):
    """Print a section header."""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def print_results(results: dict, title: str):
    """Print formatted results."""
    print_section(title)
    print(json.dumps(results, indent=2, default=str))


def demo_direct_communication(message_bus: MessageBus):
    """Demo 1: Direct agent-to-agent communication."""
    print_section("DEMO 1: Direct Agent-to-Agent Communication")
    
    # Coordinator requests data directly from Company Agent
    print("\n📋 Scenario: Coordinator asks Company Agent for stock price")
    
    msg = create_request(
        sender=AgentRole.COORDINATOR,
        receiver=AgentRole.COMPANY_AGENT,
        action="get_stock_price",
        params={"ticker": "AAPL"}
    )
    
    response = message_bus.send_message(msg)
    
    if response:
        print(f"\n✅ Received response:")
        print(f"   Stock Price Data: {response.content['data']}")
    
    # Show conversation thread
    message_bus.print_conversation(msg.message_id)


def demo_coordinator_workflow(coordinator: A2ACoordinator):
    """Demo 2: Coordinator orchestrating multi-agent workflow."""
    print_section("DEMO 2: Coordinator Orchestrating Multi-Agent Workflow")
    
    print("\n📋 Scenario: Research company and its executives")
    print("   The coordinator will:")
    print("   1. Ask Company Agent for company info and executives")
    print("   2. Ask Person Agent to research each executive")
    print("   3. Compile all results")
    
    results = coordinator.research_company_and_executives("TSLA")
    
    print_results(results, "Final Compiled Results")


def demo_person_research(coordinator: A2ACoordinator):
    """Demo 3: Person research via coordinator."""
    print_section("DEMO 3: Person Research via Coordinator")
    
    print("\n📋 Scenario: Research a specific person")
    
    results = coordinator.request_person_research("Tim Cook")
    
    print_results(results, "Person Research Results")


def demo_notifications(coordinator: A2ACoordinator):
    """Demo 4: Broadcasting notifications."""
    print_section("DEMO 4: Broadcasting Notifications to All Agents")
    
    print("\n📋 Scenario: Coordinator broadcasts a system event")
    
    coordinator.notify_agents(
        event="research_completed",
        data={"ticker": "AAPL", "timestamp": "2025-12-26T12:00:00"}
    )


def demo_message_bus_stats(message_bus: MessageBus):
    """Demo 5: Message bus statistics."""
    print_section("DEMO 5: Message Bus Statistics")
    
    stats = message_bus.get_statistics()
    
    print(f"\n📊 Message Bus Statistics:")
    print(f"   Total Messages: {stats['total_messages']}")
    print(f"   Registered Agents: {stats['registered_agents']}")
    print(f"   Agents: {', '.join(stats['agents'])}")
    print(f"\n   Message Types:")
    for msg_type, count in stats['message_types'].items():
        print(f"      {msg_type}: {count}")


def interactive_mode(coordinator: A2ACoordinator, message_bus: MessageBus):
    """Interactive mode for testing A2A communication."""
    print_section("INTERACTIVE MODE")
    
    print("\nAvailable commands:")
    print("  1. Research company (e.g., 'company AAPL')")
    print("  2. Research person (e.g., 'person Tim Cook')")
    print("  3. Company + Executives (e.g., 'full TSLA')")
    print("  4. Show statistics (e.g., 'stats')")
    print("  5. Exit (e.g., 'exit')")
    
    while True:
        print("\n" + "-"*80)
        command = input("\nEnter command: ").strip()
        
        if not command:
            continue
        
        if command.lower() == 'exit':
            print("\n👋 Exiting interactive mode...")
            break
        
        elif command.lower() == 'stats':
            demo_message_bus_stats(message_bus)
        
        elif command.lower().startswith('company '):
            ticker = command.split(' ', 1)[1].strip().upper()
            results = coordinator.request_company_research(ticker)
            print_results(results, f"Company Research: {ticker}")
        
        elif command.lower().startswith('person '):
            person_name = command.split(' ', 1)[1].strip()
            results = coordinator.request_person_research(person_name)
            print_results(results, f"Person Research: {person_name}")
        
        elif command.lower().startswith('full '):
            ticker = command.split(' ', 1)[1].strip().upper()
            results = coordinator.research_company_and_executives(ticker)
            print_results(results, f"Full Research: {ticker}")
        
        else:
            print("❌ Unknown command. Try 'company AAPL', 'person Tim Cook', 'full TSLA', 'stats', or 'exit'")


def main():
    """Run the A2A demo."""
    print("\n" + "="*80)
    print("  🤖 A2A (Agent-to-Agent) Communication Protocol Demo")
    print("="*80)
    
    # Initialize the message bus
    print("\n📡 Initializing Message Bus...")
    message_bus = MessageBus()
    
    print("\n🔧 Initializing Agents...")
    # Initialize agents (they auto-register with the message bus)
    company_agent = A2ACompanyAgent(message_bus)
    person_agent = A2APersonAgent(message_bus)
    coordinator = A2ACoordinator(message_bus)
    
    print("\n✅ System Ready!")
    print("\nChoose demo mode:")
    print("  1. Run all demos")
    print("  2. Interactive mode")
    print("  3. Specific demo")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        # Run all demos
        demo_direct_communication(message_bus)
        demo_person_research(coordinator)
        demo_notifications(coordinator)
        demo_message_bus_stats(message_bus)
        demo_coordinator_workflow(coordinator)  # This one last as it makes many requests
    
    elif choice == '2':
        # Interactive mode
        interactive_mode(coordinator, message_bus)
    
    elif choice == '3':
        # Specific demo
        print("\nAvailable demos:")
        print("  1. Direct communication")
        print("  2. Coordinator workflow (company + executives)")
        print("  3. Person research")
        print("  4. Notifications")
        print("  5. Statistics")
        
        demo_choice = input("\nEnter demo number (1-5): ").strip()
        
        if demo_choice == '1':
            demo_direct_communication(message_bus)
        elif demo_choice == '2':
            demo_coordinator_workflow(coordinator)
        elif demo_choice == '3':
            demo_person_research(coordinator)
        elif demo_choice == '4':
            demo_notifications(coordinator)
        elif demo_choice == '5':
            demo_message_bus_stats(message_bus)
        else:
            print("❌ Invalid choice")
    
    else:
        print("❌ Invalid choice")
    
    print("\n" + "="*80)
    print("  ✅ Demo Complete!")
    print("="*80)


if __name__ == "__main__":
    main()
