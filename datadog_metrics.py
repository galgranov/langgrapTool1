"""
Datadog Metrics Module
Send custom metrics to Datadog for monitoring agent performance and business metrics.
"""
import time
from typing import Optional, List, Dict, Any
from functools import wraps
from datadog_config import DatadogConfig

# Initialize metrics client
_metrics_client = None


def get_metrics_client():
    """Get or initialize Datadog metrics client."""
    global _metrics_client
    
    if _metrics_client is None and DatadogConfig.ENABLE_METRICS and DatadogConfig.is_configured():
        try:
            from datadog_api_client import ApiClient, Configuration
            from datadog_api_client.v2.api.metrics_api import MetricsApi
            
            configuration = Configuration()
            configuration.api_key["apiKeyAuth"] = DatadogConfig.API_KEY
            configuration.api_key["appKeyAuth"] = DatadogConfig.APP_KEY
            configuration.server_variables["site"] = DatadogConfig.SITE
            
            api_client = ApiClient(configuration)
            _metrics_client = MetricsApi(api_client)
        except ImportError:
            print("⚠️  datadog-api-client not installed. Metrics disabled.")
            return None
        except Exception as e:
            print(f"⚠️  Failed to initialize Datadog metrics client: {e}")
            return None
    
    return _metrics_client


def send_metric(
    metric_name: str,
    value: float,
    metric_type: str = "count",
    tags: Optional[List[str]] = None,
    timestamp: Optional[int] = None
):
    """
    Send a metric to Datadog.
    
    Args:
        metric_name: Metric name (will be prefixed with namespace)
        value: Metric value
        metric_type: Type of metric (count, gauge, rate, histogram)
        tags: List of tags
        timestamp: Unix timestamp (defaults to now)
    """
    if not DatadogConfig.ENABLE_METRICS or not DatadogConfig.is_configured():
        return
    
    client = get_metrics_client()
    if client is None:
        return
    
    try:
        from datadog_api_client.v2.model.metric_intake_type import MetricIntakeType
        from datadog_api_client.v2.model.metric_point import MetricPoint
        from datadog_api_client.v2.model.metric_series import MetricSeries
        from datadog_api_client.v2.model.metric_payload import MetricPayload
        
        # Add namespace prefix
        full_metric_name = f"{DatadogConfig.METRIC_NAMESPACE}.{metric_name}"
        
        # Get combined tags
        combined_tags = DatadogConfig.get_tags(tags)
        
        # Default timestamp to now
        if timestamp is None:
            timestamp = int(time.time())
        
        # Map metric type
        type_mapping = {
            "count": MetricIntakeType.COUNT,
            "gauge": MetricIntakeType.GAUGE,
            "rate": MetricIntakeType.RATE,
            "histogram": MetricIntakeType.DISTRIBUTION,
            "distribution": MetricIntakeType.DISTRIBUTION,
        }
        
        intake_type = type_mapping.get(metric_type.lower(), MetricIntakeType.COUNT)
        
        # Create metric payload
        series = MetricSeries(
            metric=full_metric_name,
            type=intake_type,
            points=[
                MetricPoint(
                    timestamp=timestamp,
                    value=value,
                )
            ],
            tags=combined_tags,
        )
        
        payload = MetricPayload(series=[series])
        
        # Send to Datadog
        client.submit_metrics(body=payload)
        
    except Exception as e:
        print(f"⚠️  Failed to send metric {metric_name}: {e}")


def increment(metric_name: str, value: int = 1, tags: Optional[List[str]] = None):
    """Increment a counter metric."""
    send_metric(metric_name, value, metric_type="count", tags=tags)


def gauge(metric_name: str, value: float, tags: Optional[List[str]] = None):
    """Set a gauge metric."""
    send_metric(metric_name, value, metric_type="gauge", tags=tags)


def histogram(metric_name: str, value: float, tags: Optional[List[str]] = None):
    """Send a histogram/distribution metric."""
    send_metric(metric_name, value, metric_type="histogram", tags=tags)


def timing(metric_name: str, duration: float, tags: Optional[List[str]] = None):
    """Send a timing metric (in seconds)."""
    send_metric(metric_name, duration, metric_type="histogram", tags=tags)


# Agent metrics
def track_agent_execution(agent_name: str, success: bool = True, duration: Optional[float] = None, tags: Optional[List[str]] = None):
    """Track agent execution metrics."""
    agent_tags = [f"agent:{agent_name}"] + (tags or [])
    
    increment("agent.execution.count", tags=agent_tags)
    
    if success:
        increment("agent.success.count", tags=agent_tags)
    else:
        increment("agent.error.count", tags=agent_tags)
    
    if duration is not None:
        histogram("agent.execution.duration", duration, tags=agent_tags)


# Tool metrics
def track_tool_invocation(tool_name: str, success: bool = True, duration: Optional[float] = None, tags: Optional[List[str]] = None):
    """Track tool invocation metrics."""
    tool_tags = [f"tool:{tool_name}"] + (tags or [])
    
    increment("tool.invocation.count", tags=tool_tags)
    
    if success:
        increment("tool.success.count", tags=tool_tags)
    else:
        increment("tool.error.count", tags=tool_tags)
    
    if duration is not None:
        histogram("tool.execution.duration", duration, tags=tool_tags)


# API metrics
def track_api_call(
    api_name: str,
    endpoint: str,
    success: bool = True,
    status_code: Optional[int] = None,
    duration: Optional[float] = None,
    tags: Optional[List[str]] = None
):
    """Track external API call metrics."""
    api_tags = [f"api:{api_name}", f"endpoint:{endpoint}"] + (tags or [])
    
    if status_code is not None:
        api_tags.append(f"status_code:{status_code}")
    
    increment("api.call.count", tags=api_tags)
    
    if not success:
        increment("api.error.count", tags=api_tags)
    
    if duration is not None:
        histogram("api.call.duration", duration, tags=api_tags)


# Business metrics
def track_executive_researched(count: int = 1, ticker: Optional[str] = None, tags: Optional[List[str]] = None):
    """Track number of executives researched."""
    exec_tags = tags or []
    if ticker:
        exec_tags.append(f"ticker:{ticker}")
    
    increment("business.executives.researched", value=count, tags=exec_tags)


def track_company_analyzed(ticker: str, tags: Optional[List[str]] = None):
    """Track company analysis."""
    company_tags = [f"ticker:{ticker}"] + (tags or [])
    increment("business.companies.analyzed", tags=company_tags)


def track_person_researched(person_name: str, tags: Optional[List[str]] = None):
    """Track person research."""
    person_tags = [f"person:{person_name}"] + (tags or [])
    increment("business.persons.researched", tags=person_tags)


# A2A Protocol metrics
def track_a2a_message(sender: str, receiver: str, message_type: str, duration: Optional[float] = None, tags: Optional[List[str]] = None):
    """Track A2A protocol message."""
    a2a_tags = [
        f"sender:{sender}",
        f"receiver:{receiver}",
        f"message_type:{message_type}"
    ] + (tags or [])
    
    increment("a2a.message.count", tags=a2a_tags)
    
    if duration is not None:
        histogram("a2a.message.latency", duration, tags=a2a_tags)


def track_conversation_depth(depth: int, tags: Optional[List[str]] = None):
    """Track A2A conversation depth."""
    gauge("a2a.conversation.depth", depth, tags=tags)


# Decorators
def track_execution_time(metric_name: str, tags: Optional[List[str]] = None):
    """Decorator to track function execution time."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                timing(metric_name, duration, tags=tags)
                return result
            except Exception as e:
                duration = time.time() - start_time
                error_tags = (tags or []) + [f"error:{type(e).__name__}"]
                timing(metric_name, duration, tags=error_tags)
                raise
        return wrapper
    return decorator


def track_agent_metric(agent_name: str, tags: Optional[List[str]] = None):
    """Decorator to track agent execution metrics."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                raise
            finally:
                duration = time.time() - start_time
                track_agent_execution(agent_name, success=success, duration=duration, tags=tags)
        
        return wrapper
    return decorator


def track_tool_metric(tool_name: str, tags: Optional[List[str]] = None):
    """Decorator to track tool invocation metrics."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = False
            
            try:
                result = func(*args, **kwargs)
                # Check if result indicates success
                if isinstance(result, dict):
                    success = result.get("success", True)
                else:
                    success = True
                return result
            except Exception as e:
                raise
            finally:
                duration = time.time() - start_time
                track_tool_invocation(tool_name, success=success, duration=duration, tags=tags)
        
        return wrapper
    return decorator


# Context manager for tracking operations
class MetricTimer:
    """Context manager for tracking operation duration."""
    
    def __init__(self, metric_name: str, tags: Optional[List[str]] = None):
        self.metric_name = metric_name
        self.tags = tags
        self.start_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration = time.time() - self.start_time
        
        metric_tags = self.tags or []
        if exc_type is not None:
            metric_tags = metric_tags + [f"error:{exc_type.__name__}"]
        
        timing(self.metric_name, self.duration, tags=metric_tags)


# Example usage and testing
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 DATADOG METRICS TEST")
    print("="*80 + "\n")
    
    if not DatadogConfig.is_configured():
        print("⚠️  Datadog not configured. Set DD_API_KEY and DD_APP_KEY to test metrics.")
        print("    Metrics calls will be no-ops without configuration.")
        print("="*80 + "\n")
    
    # Test basic metrics
    print("Testing metric functions...")
    increment("test.counter", value=1, tags=["test:true"])
    gauge("test.gauge", value=42.5, tags=["test:true"])
    histogram("test.histogram", value=123.45, tags=["test:true"])
    timing("test.timing", duration=1.5, tags=["test:true"])
    
    # Test agent metrics
    print("Testing agent metrics...")
    track_agent_execution("test_agent", success=True, duration=2.5)
    
    # Test tool metrics
    print("Testing tool metrics...")
    track_tool_invocation("test_tool", success=True, duration=0.5)
    
    # Test API metrics
    print("Testing API metrics...")
    track_api_call("yahoo_finance", "/quote/AAPL", success=True, status_code=200, duration=0.3)
    
    # Test business metrics
    print("Testing business metrics...")
    track_company_analyzed("AAPL")
    track_executive_researched(count=10, ticker="AAPL")
    track_person_researched("Tim Cook")
    
    # Test A2A metrics
    print("Testing A2A metrics...")
    track_a2a_message("company_agent", "person_agent", "request", duration=0.1)
    track_conversation_depth(3)
    
    # Test decorator
    print("Testing decorator...")
    @track_execution_time("test.decorated_function")
    def test_function():
        time.sleep(0.1)
        return "success"
    
    result = test_function()
    
    # Test context manager
    print("Testing context manager...")
    with MetricTimer("test.context_operation", tags=["operation:test"]):
        time.sleep(0.1)
    
    print("\n✅ Metrics test complete!")
    if DatadogConfig.is_configured():
        print("   Check your Datadog dashboard for test metrics.")
    print("="*80 + "\n")
