import logging.config
import os 
import logging
import functools
import django
from typing import Any,Dict,Optional

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UserAuth.settings')
django.setup()
from django.conf import settings

class Logger:
    
    _loggers = {}

    def __init__(self,name:str =None):
        self.logger_name = name or __name__
        if self.logger_name not in self._loggers:
            logging.config.dictConfig(settings.LOGGING)
            self._loggers[self.logger_name] = logging.getLogger(self.logger_name)
        self.logger = self._loggers[self.logger_name]

    def debug(self, msg: str, **extra):
        self.logger.debug(msg, extra=extra)

    def info(self, msg: str, **extra):
        self.logger.info(msg, extra=extra)

    def warning(self, msg: str, **extra):
        self.logger.warning(msg, extra=extra)

    def error(self, msg: str, exc: Exception = None, **extra):
        """
        If exc is provided, logs with stack trace.
        Otherwise just a normal error log.
        """
        if exc is None:
            self.logger.error(msg, extra=extra)
        else:
            # This will automatically include the traceback:
            self.logger.exception(msg, extra={"error": str(exc), **extra})

    def critical(self, msg: str, exc: Exception = None, **extra):
        if exc is None:
            self.logger.critical(msg, extra=extra)
        else:
            self.logger.exception(msg, extra={"error": str(exc), **extra})