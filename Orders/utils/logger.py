import logging.config
import os 
import logging
import functools
from typing import Any,Dict,Optional
from django.conf import settings

class Logger:
    
    _loggers = {}

    def __init__(self,name:str =None):
        self.logger_name = name or __name__
        if self.logger_name not in self._loggers:
            logging.config.dictConfig(settings.LOGGING)
            self._loggers[self.logger_name] = logging.getLogger(self.logger_name)
        self.logger = self._loggers[self.logger_name]

    def debug(self,message:str,extra:Dict[str,Any] = {})->None:
        self.logger.debug(message,extra = extra or {})

    def info(self,message:str,extra:Dict[str,Any]={}) -> None:
        self.logger.info(message,extra=extra)
    
    def error(self,message:str,error:Exception = None, extra:Dict[str,Any]={}):
        """
            Log an error message with complete stack trace information.
            
            Args:
                message (str): The base error message
                error (Exception, optional): The exception object to extract stack trace from
                extra (Dict[str, Any], optional): Additional context to include in the log
            """
        extra = extra or {}
        
        if error:
            # Start with the basic error info
            error_info = {
                'error_type': error.__class__.__name__,
                'error_message': str(error),
                'stack_trace': []
            }
            
            # Traverse the full stack trace
            tb = error.__traceback__
            while tb is not None:
                frame = tb.tb_frame
                code = frame.f_code
                
                # Extract useful information from each frame
                frame_info = {
                    'filename': code.co_filename,
                    'line_number': tb.tb_lineno,
                    'function': code.co_name,
                    'context': {},
                }
                
                # Add relevant local variables from the frame (optional)
                # Only include safe-to-log variables to avoid sensitive data
                for key, value in frame.f_locals.items():
                    # Skip private variables and objects that might be large or sensitive
                    if not key.startswith('__') and not key.startswith('_') and isinstance(value, (str, int, float, bool, type(None))):
                        try:
                            # Only add serializable values with reasonable size
                            if len(str(value)) < 500:  # Limit size of values
                                frame_info['context'][key] = value
                        except:
                            pass
                
                # Add this frame to our stack trace
                error_info['stack_trace'].append(frame_info)
                
                # Move to the next frame
                tb = tb.tb_next
            
            # Format the error message with the stack trace info
            stack_trace_msg = "\n".join([
                f"  File '{frame['filename']}', line {frame['line_number']}, in {frame['function']}"
                for frame in error_info['stack_trace']
            ])
            
            message = f"""{message}
                            Error Details:{str(error)}
                            Type: {error_info['error_type']}
                            Message: {error_info['error_message']}
                            
                            Stack Trace:
                            {stack_trace_msg}
                        """

            # Add any extra context
            if extra:
                extra_context = "\n".join([f"  {k}: {v}" for k, v in extra.items()])
                message += f"\nAdditional Context:\n{extra_context}"
                
        self.logger.error(message)

    def warning(self,message:str,extra : Dict[str,Any]={}) -> None:
        self.logger.warning(message,extra=extra or {})    