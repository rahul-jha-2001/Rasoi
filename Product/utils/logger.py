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
        if error:
            message=f"""{message} 
                'error_type': {error.__class__.__name__},
                'error_message': {str(error)},
                'error_file': {error.__traceback__.tb_frame.f_code.co_filename},
                'error_lineOn':{error.__traceback__.tb_lineno}
            """
        self.logger.error(message)

    def warning(self,message:str,extra : Dict[str,Any]={}) -> None:
        self.logger.warning(message,extra=extra or {})    