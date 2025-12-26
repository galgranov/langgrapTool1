"""
Datadog Configuration Module
Centralized configuration for Datadog monitoring, logging, and metrics.
"""
import os
from typing import Optional


class DatadogConfig:
    """Configuration for Datadog integration."""
    
    # Service Configuration
    SERVICE_NAME = os.getenv("DD_SERVICE", "lang-agents")
    ENV = os.getenv("DD_ENV", "development")
    VERSION = os.getenv("DD_VERSION", "0.1.0")
    
    # Datadog API Configuration
    API_KEY = os.getenv("DD_API_KEY", "")
    APP_KEY = os.getenv("DD_APP_KEY", "")
    SITE = os.getenv("DD_SITE", "datadoghq.com")
    
    # Feature Flags
    ENABLE_TRACING = os.getenv("DD_TRACE_ENABLED", "true").lower() == "true"
    ENABLE_METRICS = os.getenv("DD_METRICS_ENABLED", "true").lower() == "true"
    ENABLE_LOGGING = os.getenv("DD_LOGGING_ENABLED", "true").lower() == "true"
    
    # Tracing Configuration
    TRACE_SAMPLE_RATE = float(os.getenv("DD_TRACE_SAMPLE_RATE", "1.0"))
    TRACE_DEBUG = os.getenv("DD_TRACE_DEBUG", "false").lower() == "true"
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("DD_LOG_LEVEL", "INFO")
    
    # Metric Configuration
    METRIC_NAMESPACE = "lang_agents"
    
    # Tags
    COMMON_TAGS = [
        f"service:{SERVICE_NAME}",
        f"env:{ENV}",
        f"version:{VERSION}",
    ]
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if Datadog is properly configured."""
        return bool(cls.API_KEY)
    
    @classmethod
    def get_tags(cls, additional_tags: Optional[list] = None) -> list:
        """Get combined tags."""
        tags = cls.COMMON_TAGS.copy()
        if additional_tags:
            tags.extend(additional_tags)
        return tags
    
    @classmethod
    def validate(cls) -> tuple[bool, list[str]]:
        """
        Validate Datadog configuration.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not cls.API_KEY:
            errors.append("DD_API_KEY is not set")
        
        if cls.ENABLE_METRICS and not cls.APP_KEY:
            errors.append("DD_APP_KEY is required for metrics (or disable with DD_METRICS_ENABLED=false)")
        
        if cls.TRACE_SAMPLE_RATE < 0 or cls.TRACE_SAMPLE_RATE > 1:
            errors.append("DD_TRACE_SAMPLE_RATE must be between 0 and 1")
        
        return len(errors) == 0, errors


# Agent-specific configurations
AGENT_CONFIGS = {
    "meta_agent": {
        "description": "Orchestrates company and executive research",
        "tags": ["agent:meta"],
    },
    "company_agent": {
        "description": "Company research and financial data",
        "tags": ["agent:company"],
    },
    "person_agent": {
        "description": "Person biographical research",
        "tags": ["agent:person"],
    },
    "a2a_coordinator": {
        "description": "A2A protocol coordinator",
        "tags": ["agent:a2a_coordinator"],
    },
    "a2a_company": {
        "description": "A2A-enabled company agent",
        "tags": ["agent:a2a_company"],
    },
    "a2a_person": {
        "description": "A2A-enabled person agent",
        "tags": ["agent:a2a_person"],
    },
    "weather_agent": {
        "description": "City weather information",
        "tags": ["agent:weather"],
    },
}


# Tool-specific configurations
TOOL_CONFIGS = {
    "yahoo_finance": {
        "description": "Yahoo Finance API calls",
        "tags": ["tool:yahoo_finance", "api:external"],
    },
    "wikipedia": {
        "description": "Wikipedia API calls",
        "tags": ["tool:wikipedia", "api:external"],
    },
    "wikidata": {
        "description": "Wikidata API calls",
        "tags": ["tool:wikidata", "api:external"],
    },
    "openmeteo": {
        "description": "OpenMeteo weather API",
        "tags": ["tool:openmeteo", "api:external"],
    },
}


# Metric definitions
METRIC_DEFINITIONS = {
    # Agent metrics
    "agent.execution.count": {
        "type": "count",
        "description": "Total number of agent executions",
        "unit": "execution",
    },
    "agent.execution.duration": {
        "type": "histogram",
        "description": "Agent execution time",
        "unit": "second",
    },
    "agent.success.count": {
        "type": "count",
        "description": "Successful agent executions",
        "unit": "execution",
    },
    "agent.error.count": {
        "type": "count",
        "description": "Failed agent executions",
        "unit": "execution",
    },
    
    # Tool metrics
    "tool.invocation.count": {
        "type": "count",
        "description": "Tool invocation count",
        "unit": "invocation",
    },
    "tool.execution.duration": {
        "type": "histogram",
        "description": "Tool execution time",
        "unit": "second",
    },
    "tool.success.count": {
        "type": "count",
        "description": "Successful tool invocations",
        "unit": "invocation",
    },
    "tool.error.count": {
        "type": "count",
        "description": "Failed tool invocations",
        "unit": "invocation",
    },
    
    # API metrics
    "api.call.count": {
        "type": "count",
        "description": "External API calls",
        "unit": "call",
    },
    "api.call.duration": {
        "type": "histogram",
        "description": "API call latency",
        "unit": "second",
    },
    "api.error.count": {
        "type": "count",
        "description": "API errors",
        "unit": "error",
    },
    "api.rate_limit.hit": {
        "type": "count",
        "description": "API rate limit hits",
        "unit": "hit",
    },
    
    # Business metrics
    "business.executives.researched": {
        "type": "count",
        "description": "Number of executives researched",
        "unit": "executive",
    },
    "business.companies.analyzed": {
        "type": "count",
        "description": "Number of companies analyzed",
        "unit": "company",
    },
    "business.persons.researched": {
        "type": "count",
        "description": "Number of persons researched",
        "unit": "person",
    },
    
    # A2A Protocol metrics
    "a2a.message.count": {
        "type": "count",
        "description": "Inter-agent messages sent",
        "unit": "message",
    },
    "a2a.message.latency": {
        "type": "histogram",
        "description": "Message routing time",
        "unit": "second",
    },
    "a2a.conversation.depth": {
        "type": "gauge",
        "description": "Conversation thread depth",
        "unit": "level",
    },
}


def print_configuration_status():
    """Print current Datadog configuration status."""
    is_valid, errors = DatadogConfig.validate()
    
    print("\n" + "="*80)
    print("🔧 DATADOG CONFIGURATION STATUS")
    print("="*80)
    
    print(f"\n📊 Service: {DatadogConfig.SERVICE_NAME}")
    print(f"🌍 Environment: {DatadogConfig.ENV}")
    print(f"📦 Version: {DatadogConfig.VERSION}")
    print(f"🏢 Site: {DatadogConfig.SITE}")
    
    print("\n🎛️  Features:")
    print(f"   Tracing: {'✅' if DatadogConfig.ENABLE_TRACING else '❌'}")
    print(f"   Metrics: {'✅' if DatadogConfig.ENABLE_METRICS else '❌'}")
    print(f"   Logging: {'✅' if DatadogConfig.ENABLE_LOGGING else '❌'}")
    
    print("\n🔑 API Keys:")
    print(f"   API Key: {'✅ Set' if DatadogConfig.API_KEY else '❌ Not Set'}")
    print(f"   APP Key: {'✅ Set' if DatadogConfig.APP_KEY else '❌ Not Set'}")
    
    print(f"\n🎯 Status: {'✅ Ready' if is_valid and DatadogConfig.is_configured() else '⚠️  Not Configured'}")
    
    if errors:
        print("\n❌ Configuration Errors:")
        for error in errors:
            print(f"   • {error}")
        print("\n💡 See DATADOG_README.md for setup instructions")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    print_configuration_status()
