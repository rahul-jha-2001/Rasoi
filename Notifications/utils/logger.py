import logging
import functools
from typing import Any,Dict,Optional
from django.conf import settings

class Logger:

    _loggers = {}  # Store multiple logger instances

    def __init__(self, name: str = None):
        self.logger_name = name or __name__
        if self.logger_name not in self._loggers:
            logging.config.dictConfig(settings.LOGGING)
            self._loggers[self.logger_name] = logging.getLogger(self.logger_name)
        self.logger = self._loggers[self.logger_name]
    
    def info(self, message: str, extra: Dict[str, Any] = {}) -> None:
        self.logger.info(message, extra=extra)
    
    def error(self, message: str, error: Exception = None, extra: Dict[str, Any] = {}) -> None:
        error_details = extra.get('error_details', {})
        if error:
            error_details.update({
                'error_type': error.__class__.__name__,
                'error_message': str(error),
                'error_traceback': error.__traceback__,
            })
        self.logger.error(message, extra=error_details)

    def debug(self, message: str, extra: Dict[str, Any] = {}) -> None:
        self.logger.debug(message, extra=extra or {})

    def warning(self, message: str, extra: Dict[str, Any] = {}) -> None:
        self.logger.warning(message, extra=extra or {})


def log_operation(operation_name: str):
    """Decorator to log the operation of a function"""
    logger = Logger(__name__)
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                logger.info(f"Starting {operation_name}")
                result = func(*args, **kwargs)
                logger.info(f"Finished {operation_name}")
                return result
            except Exception as e:
                logger.error(
                    f"Error during {operation_name}",
                    error=e,
                    extra={'args': args, 'kwargs': kwargs}
                )
                raise
        return wrapper
    return decorator
