"""
Datadog Tracing Module
Distributed tracing and APM instrumentation using ddtrace.
"""
import time
from typing import Optional, Dict, Any, Callable
from functools import wraps
from datadog_config import DatadogConfig

# Initialize tracer
_tracer = None


def get_tracer():
    """Get or initialize ddtrace tracer."""
    global _tracer
    
    if _tracer is None and DatadogConfig.ENABLE_TRACING:
        try:
            from ddtrace import tracer, patch
            
            # Configure tracer
            tracer.configure(
                hostname="localhost",
                port=8126,
                enabled=DatadogConfig.ENABLE_TRACING,
                debug=DatadogConfig.TRACE_DEBUG,
            )
            
            # Set service info
            tracer.set_tags({
                "service": DatadogConfig.SERVICE_NAME,
                "env": DatadogConfig.ENV,
                "version": DatadogConfig.VERSION,
            })
            
            # Auto-patch common libraries
            patch(requests=True)
            
            _tracer = tracer
            
        except ImportError:
            print("⚠️  ddtrace not installed. Tracing disabled.")
            return None
        except Exception as e:
            print(f"⚠️  Failed to initialize ddtrace: {e}")
            return None
    
    return _tracer


def trace_operation(
    operation_name: str,
    service: Optional[str] = None,
    resource: Optional[str] = None,
    span_type: Optional[str] = None,
    tags: Optional[Dict[str, Any]] = None
):
    """
    Decorator to trace a function or operation.
    
    Args:
        operation_name: Name of the operation/span
        service: Service name (defaults to configured service)
        resource: Resource being accessed
        span_type: Type of span (web, db, cache, custom)
        tags: Additional tags for the span
    
    Example:
        @trace_operation("fetch_company_data", resource="yahoo_finance", span_type="http")
        def get_company_info(ticker):
            # function code
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            
            # If tracing is disabled, just execute the function
            if tracer is None or not DatadogConfig.ENABLE_TRACING:
                return func(*args, **kwargs)
            
            # Create span
            with tracer.trace(
                operation_name,
                service=service or DatadogConfig.SERVICE_NAME,
                resource=resource or func.__name__,
                span_type=span_type
            ) as span:
                # Add tags
                if tags:
                    span.set_tags(tags)
                
                # Add function metadata
                span.set_tag("function.name", func.__name__)
                span.set_tag("function.module", func.__module__)
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Mark as successful
                    span.set_tag("operation.success", True)
                    
                    # Add result metadata if it's a dict with success info
                    if isinstance(result, dict):
                        if "success" in result:
                            span.set_tag("result.success", result["success"])
                        if "error" in result and result.get("error"):
                            span.set_tag("result.error", result["error"])
                    
                    return result
                
                except Exception as e:
                    # Mark as failed and add error info
                    span.set_tag("operation.success", False)
                    span.set_tag("error.type", type(e).__name__)
                    span.set_tag("error.message", str(e))
                    span.set_tag("error", True)
                    raise
        
        return wrapper
    return decorator


def trace_agent(agent_name: str, tags: Optional[Dict[str, Any]] = None):
    """
    Decorator to trace agent execution.
    
    Args:
        agent_name: Name of the agent
        tags: Additional tags
    
    Example:
        @trace_agent("meta_agent")
        def run_meta_agent(ticker):
            # agent code
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            
            if tracer is None or not DatadogConfig.ENABLE_TRACING:
                return func(*args, **kwargs)
            
            with tracer.trace(
                f"agent.{agent_name}",
                service=DatadogConfig.SERVICE_NAME,
                resource=agent_name,
                span_type="agent"
            ) as span:
                # Add agent tags
                span.set_tag("agent.name", agent_name)
                span.set_tag("agent.type", "langgraph")
                
                if tags:
                    span.set_tags(tags)
                
                # Extract input parameters if available
                if args:
                    if isinstance(args[0], dict):
                        # Likely a state dict
                        for key in ["ticker", "person_name", "city"]:
                            if key in args[0]:
                                span.set_tag(f"input.{key}", args[0][key])
                
                try:
                    result = func(*args, **kwargs)
                    span.set_tag("agent.success", True)
                    return result
                except Exception as e:
                    span.set_tag("agent.success", False)
                    span.set_tag("error.type", type(e).__name__)
                    span.set_tag("error.message", str(e))
                    span.set_tag("error", True)
                    raise
        
        return wrapper
    return decorator


def trace_tool(tool_name: str, api_name: Optional[str] = None, tags: Optional[Dict[str, Any]] = None):
    """
    Decorator to trace tool invocation.
    
    Args:
        tool_name: Name of the tool
        api_name: External API being called
        tags: Additional tags
    
    Example:
        @trace_tool("get_company_info", api_name="yahoo_finance")
        def get_company_info_tool(ticker):
            # tool code
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            
            if tracer is None or not DatadogConfig.ENABLE_TRACING:
                return func(*args, **kwargs)
            
            with tracer.trace(
                f"tool.{tool_name}",
                service=DatadogConfig.SERVICE_NAME,
                resource=tool_name,
                span_type="tool"
            ) as span:
                # Add tool tags
                span.set_tag("tool.name", tool_name)
                
                if api_name:
                    span.set_tag("tool.api", api_name)
                
                if tags:
                    span.set_tags(tags)
                
                # Extract parameters
                if args:
                    if isinstance(args[0], dict):
                        for key, value in args[0].items():
                            if isinstance(value, (str, int, float, bool)):
                                span.set_tag(f"tool.param.{key}", value)
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Add result info
                    if isinstance(result, dict):
                        span.set_tag("tool.success", result.get("success", True))
                        if result.get("error"):
                            span.set_tag("tool.error", result["error"])
                    
                    return result
                except Exception as e:
                    span.set_tag("tool.success", False)
                    span.set_tag("error.type", type(e).__name__)
                    span.set_tag("error.message", str(e))
                    span.set_tag("error", True)
                    raise
        
        return wrapper
    return decorator


def trace_api_call(api_name: str, tags: Optional[Dict[str, Any]] = None):
    """
    Decorator to trace external API calls.
    
    Args:
        api_name: Name of the external API
        tags: Additional tags
    
    Example:
        @trace_api_call("yahoo_finance")
        def call_yahoo_api(url):
            # API call code
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = get_tracer()
            
            if tracer is None or not DatadogConfig.ENABLE_TRACING:
                return func(*args, **kwargs)
            
            with tracer.trace(
                f"api.{api_name}",
                service=DatadogConfig.SERVICE_NAME,
                resource=api_name,
                span_type="http"
            ) as span:
                # Add API tags
                span.set_tag("api.name", api_name)
                span.set_tag("api.type", "external")
                
                if tags:
                    span.set_tags(tags)
                
                try:
                    result = func(*args, **kwargs)
                    
                    # Check for status code in result
                    if hasattr(result, "status_code"):
                        span.set_tag("http.status_code", result.status_code)
                        span.set_tag("api.success", 200 <= result.status_code < 300)
                    
                    return result
                except Exception as e:
                    span.set_tag("api.success", False)
                    span.set_tag("error.type", type(e).__name__)
                    span.set_tag("error.message", str(e))
                    span.set_tag("error", True)
                    raise
        
        return wrapper
    return decorator


class TraceSpan:
    """Context manager for creating custom trace spans."""
    
    def __init__(
        self,
        operation_name: str,
        service: Optional[str] = None,
        resource: Optional[str] = None,
        span_type: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None
    ):
        self.operation_name = operation_name
        self.service = service or DatadogConfig.SERVICE_NAME
        self.resource = resource
        self.span_type = span_type
        self.tags = tags or {}
        self.span = None
        self.tracer = get_tracer()
    
    def __enter__(self):
        if self.tracer is None or not DatadogConfig.ENABLE_TRACING:
            return self
        
        self.span = self.tracer.trace(
            self.operation_name,
            service=self.service,
            resource=self.resource,
            span_type=self.span_type
        )
        
        if self.tags:
            self.span.set_tags(self.tags)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.span is None:
            return
        
        if exc_type is not None:
            self.span.set_tag("error", True)
            self.span.set_tag("error.type", exc_type.__name__)
            self.span.set_tag("error.message", str(exc_val))
        
        self.span.finish()
    
    def set_tag(self, key: str, value: Any):
        """Set a tag on the span."""
        if self.span:
            self.span.set_tag(key, value)
    
    def set_tags(self, tags: Dict[str, Any]):
        """Set multiple tags on the span."""
        if self.span:
            self.span.set_tags(tags)


def get_current_trace_id() -> Optional[str]:
    """Get the current trace ID if available."""
    tracer = get_tracer()
    if tracer is None:
        return None
    
    try:
        span = tracer.current_span()
        if span:
            return str(span.trace_id)
    except Exception:
        pass
    
    return None


def get_current_span_id() -> Optional[str]:
    """Get the current span ID if available."""
    tracer = get_tracer()
    if tracer is None:
        return None
    
    try:
        span = tracer.current_span()
        if span:
            return str(span.span_id)
    except Exception:
        pass
    
    return None


# Example usage and testing
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🧪 DATADOG TRACING TEST")
    print("="*80 + "\n")
    
    if not DatadogConfig.ENABLE_TRACING:
        print("⚠️  Tracing is disabled. Set DD_TRACE_ENABLED=true to enable.")
        print("="*80 + "\n")
    
    # Test basic tracing
    @trace_operation("test_operation", span_type="custom")
    def test_function(value: int):
        time.sleep(0.1)
        return {"success": True, "value": value * 2}
    
    print("Testing basic tracing...")
    result = test_function(5)
    print(f"Result: {result}")
    
    # Test agent tracing
    @trace_agent("test_agent")
    def test_agent(state: dict):
        time.sleep(0.1)
        return {"ticker": "AAPL", "result": "success"}
    
    print("\nTesting agent tracing...")
    agent_result = test_agent({"ticker": "AAPL"})
    print(f"Agent result: {agent_result}")
    
    # Test tool tracing
    @trace_tool("test_tool", api_name="test_api")
    def test_tool(params: dict):
        time.sleep(0.1)
        return {"success": True, "data": "test data"}
    
    print("\nTesting tool tracing...")
    tool_result = test_tool({"ticker": "GOOGL"})
    print(f"Tool result: {tool_result}")
    
    # Test context manager
    print("\nTesting trace context manager...")
    with TraceSpan("custom_operation", span_type="custom") as span:
        span.set_tag("custom.tag", "value")
        time.sleep(0.1)
        print("Inside trace span")
    
    # Test trace ID retrieval
    print("\nTesting trace ID retrieval...")
    trace_id = get_current_trace_id()
    span_id = get_current_span_id()
    print(f"Current Trace ID: {trace_id or 'None'}")
    print(f"Current Span ID: {span_id or 'None'}")
    
    print("\n✅ Tracing test complete!")
    if DatadogConfig.ENABLE_TRACING:
        print("   Check your Datadog APM for traces.")
    print("="*80 + "\n")
