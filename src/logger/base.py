from logging import *
from logging.handlers import RotatingFileHandler
from typing import override

from logger.enums import LogLevel


class Logger(Logger):
    @override
    def isEnabledFor(self, level: LogLevel) -> bool:
        if isinstance(level, LogLevel):
            level = level.numeric
        return super().isEnabledFor(level)

    @override
    def log(
        self,
        level: LogLevel,
        msg,
        *args,
        exc_info=None,
        stack_info=False,
        stacklevel=1,
        extra=None,
    ):
        if isinstance(level, LogLevel):
            level = level.numeric
        return super().log(level, msg, *args, exc_info=exc_info, stack_info=stack_info, extra=extra)


setLoggerClass(Logger)
