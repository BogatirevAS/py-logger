from typing import Type

from logger.decorators import classproperty
from logger.manager import LoggerManager


class LoggerMixin:
    @property
    def logger_name(self):
        return LoggerManager.get_logger_name(self)

    @property
    def logger(self):
        return LoggerManager.get_logger(self.logger_name)


class ClassLoggerMixin:
    @classproperty
    def logger_name(cls):
        return LoggerManager.get_logger_name(cls)

    @classproperty
    def logger(cls):
        return LoggerManager.get_logger(cls.logger_name)


class ValidateMixin(LoggerMixin):
    def __init__(self, validate=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate = validate

    def validate_msg(self, msg, exc: Type[Exception] = AttributeError):
        if self.validate:
            raise exc(msg)
        self.logger.warning(msg)
