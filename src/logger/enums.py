from enum import StrEnum

from logger import base


class LogLevel(StrEnum):
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    WARN = "WARN"
    INFO = "INFO"
    DEBUG = "DEBUG"
    NOTSET = "NOTSET"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            upper = value.upper()
            if upper in cls.__members__:
                return cls.__members__[upper]
        return None

    @property
    def numeric(self) -> int:
        return getattr(base, self.value)


class LoggerFormatType(StrEnum):
    DEFAULT = "default"
    DEBUG = "debug"
