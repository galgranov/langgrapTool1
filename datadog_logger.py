"""
Datadog Logging Utilities
Structured JSON logging with Datadog integration and trace correlation.
"""
import logging
import sys
from typing import Optional, Dict, Any
from pythonjsonlogger import jsonlogger
from datadog_config import DatadogConfig

# Global logger cache
_loggers: Dict[str, logging.Logger] = {}


class DatadogJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for Datadog with trace correlation."""
    
    def add_fields(self, log_record, record, message_dict):
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)
        
        # Add standard Datadog fields
        log_record['dd.service'] = DatadogConfig.SERVICE_NAME
        log_record['dd.env'] = DatadogConfig.ENV
        log_record['dd.version'] = DatadogConfig.VERSION
        
        # Add trace correlation if tracing is enabled
        if DatadogConfig.ENABLE_TRACING:
            try:
                from ddtrace import tracer
                span = tracer.current_span()
                if span:
                    log_record['dd.trace_id'] = str(span.trace_id)
                    log_record['dd.span_id'] = str(span.span_id)
            except (ImportError, Exception):
                pass
        
        # Add log level as status
        log_record['status'] = record.levelname
        
        # Ensure message field exists
        if 'message' not in log_record:
            log_record['message'] = record.getMessage()


def get_logger(
    name: str,
    agent_name: Optional[str] = None,
    additional_context: Optional[Dict[str, Any]] = None
) -> logging.Logger:
    """
    Get or create a logger with Datadog configuration.
    
    Args:
        name: Logger name (usually __name__)
        agent_name: Name of the agent (for tagging)
        additional_context: Additional context to include in all logs
        
    Returns:
        Configured logger instance
    """
    # Create cache key
    cache_key = f"{name}:{agent_name or 'default'}"
    
    # Return cached logger if exists
    if cache_key in _loggers:
        return _loggers[cache_key]
    
    # Create new logger
    logger = logging.getLogger(cache_key)
    logger.setLevel(getattr(logging, DatadogConfig.LOG_LEVEL.upper()))
    logger.propagate = False
    
    # Clear existing handlers
    logger.handlers.clear()
    
    if DatadogConfig.ENABLE_LOGGING and DatadogConfig.is_configured():
        # Use JSON formatter for Datadog
        handler = logging.StreamHandler(sys.stdout)
        
        # Create formatter with custom fields
        format_string = '%(asctime)s %(levelname)s %(name)s %(message)s'
        formatter = DatadogJsonFormatter(format_string)
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
    else:
        # Use standard formatter for development
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    # Add context filter if provided
    if agent_name or additional_context:
        context_filter = ContextFilter(agent_name, additional_context)
        logger.addFilter(context_filter)
    
    # Cache logger
    _loggers[cache_key] = logger
    
    return logger


class ContextFilter(logging.Filter):
    """Filter to add context to log records."""
    
    def __init__(self, agent_name: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.agent_name = agent_name
        self.context = context or {}
    
    def filter(self, record):
        """Add context fields to record."""
        if self.agent_name:
            record.agent = self.agent_name
        
        for key, value in self.context.items():
            setattr(record, key, value)
        
        return True


class LoggerContext:
    """Context manager for temporary logger context."""
    
    def __init__(self, logger: logging.Logger, **context):
        self.logger = logger
        self.context = context
        self.original_filters = []
    
    def __enter__(self):
        """Add context filter."""
        context_filter = ContextFilter(context=self.context)
        self.logger.addFilter(context_filter)
        self.original_filters.append(context_filter)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Remove context filter."""
        for filter in self.original_filters:
            self.logger.removeFilter(filter)
        self.original_filters.clear()


def log_agent_start(logger: logging.Logger, agent_name: str, **kwargs):
    """Log agent execution start."""
    logger.info(
        f"Agent started: {agent_name}",
        extra={
            'event.type': 'agent.start',
            'agent.name': agent_name,
            **kwargs
        }
    )


def log_agent_end(logger: logging.Logger, agent_name: str, success: bool = True, **kwargs):
    """Log agent execution end."""
    level = logging.INFO if success else logging.ERROR
    logger.log(
        level,
        f"Agent {'completed' if success else 'failed'}: {agent_name}",
        extra={
            'event.type': 'agent.end',
            'agent.name': agent_name,
            'agent.success': success,
            **kwargs
        }
    )


def log_tool_invocation(
    logger: logging.Logger,
    tool_name: str,
    success: bool = True,
    duration: Optional[float] = None,
    **kwargs
):
    """Log tool invocation."""
    level = logging.INFO if success else logging.WARNING
    message = f"Tool {'succeeded' if success else 'failed'}: {tool_name}"
    
    extra = {
        'event.type': 'tool.invocation',
        'tool.name': tool_name,
        'tool.success': success,
        **kwargs
    }
    
    if duration is not None:
        extra['tool.duration'] = duration
    
    logger.log(level, message, extra=extra)


def log_api_call(
    logger: logging.Logger,
    api_name: str,
    endpoint: str,
    success: bool = True,
    status_code: Optional[int] = None,
    duration: Optional[float] = None,
    **kwargs
):
    """Log external API call."""
    level = logging.INFO if success else logging.WARNING
    message = f"API call {'succeeded' if success else 'failed'}: {api_name} - {endpoint}"
    
    extra = {
        'event.type': 'api.call',
        'api.name': api_name,
        'api.endpoint': endpoint,
        'api.success': success,
        **kwargs
    }
    
    if status_code is not None:
        extra['api.status_code'] = status_code
    
    if duration is not None:
        extra['api.duration'] = duration
    
    logger.log(level, message, extra=extra)


def log_error(
    logger: logging.Logger,
    error: Exception,
    context: Optional[str] = None,
    **kwargs
):
    """Log an error with full context."""
    message = f"Error{f' in {context}' if context else ''}: {str(error)}"
    
    extra = {
        'event.type': 'error',
        'error.type': type(error).__name__,
        'error.message': str(error),
        **kwargs
    }
    
    if context:
        extra['error.context'] = context
    
    logger.error(message, extra=extra, exc_info=True)


def log_metric_event(
    logger: logging.Logger,
    metric_name: str,
    value: float,
    **kwargs
):
    """Log a metric event."""
    logger.info(
        f"Metric: {metric_name} = {value}",
        extra={
            'event.type': 'metric',
            'metric.name': metric_name,
            'metric.value': value,
            **kwargs
        }
    )


# Example usage and testing
if __name__ == "__main__":
    # Create test logger
    logger = get_logger(__name__, agent_name="test_agent")
    
    print("\n" + "="*80)
    print("🧪 DATADOG LOGGER TEST")
    print("="*80 + "\n")
    
    # Test basic logging
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")
    
    # Test agent logging
    log_agent_start(logger, "test_agent", input_data="sample_data")
    log_agent_end(logger, "test_agent", success=True, execution_time=1.5)
    
    # Test tool logging
    log_tool_invocation(logger, "test_tool", success=True, duration=0.5)
    
    # Test API logging
    log_api_call(
        logger,
        api_name="yahoo_finance",
        endpoint="/quote/AAPL",
        success=True,
        status_code=200,
        duration=0.3
    )
    
    # Test error logging
    try:
        raise ValueError("Test error")
    except Exception as e:
        log_error(logger, e, context="test_function")
    
    # Test context manager
    with LoggerContext(logger, ticker="AAPL", request_id="12345") as ctx_logger:
        ctx_logger.info("Message with temporary context")
    
    print("\n✅ Logger test complete!")
    print("="*80 + "\n")
