import logging
import functools
from typing import Any,Dict,Optional

logger = logging.getLogger('notifications')

class Logger:

    @staticmethod
    def info(message:str,extra:Dict[str,Any]={}) -> None:
        logger.info(message,extra=extra)
    
    @staticmethod
    def  error(message:str,error :Exception = None,extra:Dict[str,Any]={}) -> None:
        error_details = extra.get('error_details',{})
        if error:
            error_details.update(
                {
                    'error_type':   error.__class__.__name__,
                    'error_message':    str(error),
                    'error_traceback': error.__traceback__,
                }
            )
        logger.error(message,extra=error_details)

    @staticmethod
    def debug(message:str,extra:Dict[str,Any]={}) -> None:
        logger.debug(message,extra=extra or {})


def log_operation(operation_name:str):
    """Decorator to log the operation of a function"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            try:

                Logger.info(f"starting {operation_name}")

                result = func(*args,*kwargs)

                Logger.info(f"Finished {operation_name}")

                return result
            except Exception as e:
                Logger.error(
                    f"Error during {operation_name}",
                    error=e,
                    extra={'args':args,'kwargs':kwargs}
                )
                raise
        return wrapper
    return decorator


if __name__ == "__main__":
    Logger.info("Logger initialized")