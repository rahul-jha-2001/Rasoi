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
    
    def error(self, message: str, error: Exception = None, extra: Dict[str, Any] = None, 
            include_locals: bool = True, max_stack_depth: int = 20):
        """
        Log an error message with complete stack trace information.
        
        Args:
            message (str): The base error message
            error (Exception, optional): The exception object to extract stack trace from
            extra (Dict[str, Any], optional): Additional context to include in the log
            include_locals (bool): Whether to include local variables in stack frames
            max_stack_depth (int): Maximum number of stack frames to process
        """
        extra = extra or {}
        log_data = {
            'message': message,
            'extra': extra
        }

        if error:
            error_info = {
                'type': error.__class__.__name__,
                'message': str(error),
                'args': getattr(error, 'args', ()),
                'stack_trace': [],
                'chain': []
            }
            log_data['error'] = error_info

            # Process exception chain
            current_error = error
            while current_error and len(error_info['chain']) < 8:  # Limit chain depth
                tb = current_error.__traceback__
                frames = []
                frame_count = 0

                while tb is not None and frame_count < max_stack_depth:
                    frame = tb.tb_frame
                    code = frame.f_code
                    
                    frame_info = {
                        'file': code.co_filename,
                        'line': tb.tb_lineno,
                        'function': code.co_name,
                    }

                    frames.append(frame_info)
                    tb = tb.tb_next
                    frame_count += 1

                error_info['stack_trace'] = frames
                
                # Get next exception in chain
                current_error = current_error.__cause__ or current_error.__context__
                if current_error:
                    error_info['chain'].append({
                        'type': current_error.__class__.__name__,
                        'message': str(current_error)
                    })

        # Choose format based on logger capabilities
        if hasattr(self.logger, 'log_struct'):  # For JSON logging
            self.logger.error("Error occurred", **log_data)
        else:
            # Format as text
            msg_parts = [message]
            if 'error' in log_data:
                err = log_data['error']
                msg_parts.append(f"Error: {err['type']}: {err['message']}")
                for i, frame in enumerate(err['stack_trace']):
                    msg_parts.append(
                        f"  {i}: {frame['function']} at {frame['file']}:{frame['line']}"
                    )
            if extra:
                msg_parts.append("Extra context: " + ", ".join(f"{k}={v}" for k, v in extra.items()))
            
            self.logger.error("\n".join(msg_parts))

    def warning(self,message:str,extra : Dict[str,Any]={}) -> None:
        self.logger.warning(message,extra=extra or {}) 

    def critical(self, message: str, error: Exception = None, extra: Dict[str,Any] = {}):
        """
        Log critical errors that require immediate attention with detailed stack trace.
        
        Args:
            message (str): The critical error message
            error (Exception, optional): The exception object to extract stack trace from
            extra (Dict[str, Any], optional): Additional context to include in the log
        """
        extra = extra or {}
        formatted_message = self._format_detailed_trace(message, error, extra, level="CRITICAL")
        self.logger.critical(formatted_message)

    def severe(self, message: str, error: Exception = None, extra: Dict[str,Any] = {}):
        """
        Log severe system errors with detailed execution context and stack trace.
        
        Args:
            message (str): The severe error message
            error (Exception, optional): The exception object to extract stack trace from
            extra (Dict[str, Any], optional): Additional context to include in the log
        """
        extra = extra or {}
        formatted_message = self._format_detailed_trace(message, error, extra, level="SEVERE")
        self.logger.error(formatted_message)  # Using error level since severe isn't standard

    def _format_detailed_trace(self, message: str, error: Exception = None, extra: Dict[str,Any] = {}, level: str = "ERROR") -> str:
        """
        Helper method to format detailed stack trace information.
        
        Args:
            message (str): Base message
            error (Exception): Exception object
            extra (dict): Additional context
            level (str): Log level
        Returns:
            str: Formatted message with stack trace
        """
        if not error:
            return message

        import inspect
        import datetime

        # Get current timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Basic error info
        error_info = {
            'timestamp': timestamp,
            'level': level,
            'error_type': error.__class__.__name__,
            'error_message': str(error),
            'stack_trace': []
        }

        # Get the full stack trace
        tb = error.__traceback__
        while tb is not None:
            frame = tb.tb_frame
            code = frame.f_code
            
            # Get source code context
            try:
                source_lines, start_line = inspect.getsourcelines(frame.f_code)
                relevant_code = ''.join(source_lines[tb.tb_lineno - start_line - 2:tb.tb_lineno - start_line + 1])
            except:
                relevant_code = "Source code unavailable"

            frame_info = {
                'filename': code.co_filename,
                'line_number': tb.tb_lineno,
                'function': code.co_name,
                'source_code': relevant_code.strip(),
                'context': {},
                'locals': {}
            }

            # Add local variables
            for key, value in frame.f_locals.items():
                if not key.startswith('__') and not key.startswith('_'):
                    try:
                        if isinstance(value, (str, int, float, bool, type(None))):
                            if len(str(value)) < 500:
                                frame_info['locals'][key] = str(value)
                    except:
                        continue

            error_info['stack_trace'].append(frame_info)
            tb = tb.tb_next

        # Format the detailed message
        formatted_message = f"""
{level} EVENT
Timestamp: {error_info['timestamp']}
Message: {message}
Error Type: {error_info['error_type']}
Error Details: {error_info['error_message']}

Stack Trace:
"""
        
        for frame in error_info['stack_trace']:
            formatted_message += f"""
File: {frame['filename']}
Line: {frame['line_number']}
Function: {frame['function']}
Source:
{frame['source_code']}
Local Variables: {frame['locals']}
-------------------"""

        if extra:
            extra_context = "\n".join([f"  {k}: {v}" for k, v in extra.items()])
            formatted_message += f"\n\nAdditional Context:\n{extra_context}"

        return formatted_message