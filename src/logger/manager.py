from typing import Optional, Any, Unpack

from logger import base
from logger.decorators import classproperty
from logger.enums import LogLevel
from logger.models import LoggerSession
from logger.session import session_logger_scope, async_session_logger_scope, install_record_factory
from logger.settings import LoggerSettings, LoggerSettingsKwargs


class LoggerManager:
    settings = LoggerSettings()
    _cached_names = {}
    session_scope = staticmethod(session_logger_scope)
    async_session_scope = staticmethod(async_session_logger_scope)

    @classmethod
    def init_global_logger(cls, settings: Optional[LoggerSettings] = None, **kwargs: Unpack[LoggerSettingsKwargs]):
        cls.settings = LoggerSettings.create_or_update(settings, **kwargs)
        install_record_factory()
        base.basicConfig(**cls.settings.config)

    @classmethod
    def set_log_level(cls, level: LogLevel):
        base.getLogger().setLevel(level.value)

    @classmethod
    def trim_name(cls, name: str, name_size: int) -> str:
        if 0 < name_size < len(name):
            chunks = name.split(".")
            for i, chunk in enumerate(chunks[0:-1]):
                chunks[i] = chunk[0]
                name = ".".join(chunks)
                if len(name) <= name_size:
                    break
        return name

    @classmethod
    def create_name(cls, obj_or_type) -> str:
        class_ = obj_or_type if isinstance(obj_or_type, type) else obj_or_type.__class__
        return f"{class_.__module__}.{class_.__name__}"

    @classmethod
    def get_logger_name(cls, obj: Any):
        key = obj if isinstance(obj, str) else cls.create_name(obj)
        if key not in cls._cached_names:
            cls._cached_names[key] = cls.trim_name(key, cls.settings.name_size)
        return cls._cached_names.get(key)

    @classmethod
    def get_logger(cls, name: str) -> base.Logger:
        return base.getLogger(name)

    @classmethod
    def get_named_logger(cls, name: Any) -> base.Logger:
        return cls.get_logger(cls.get_logger_name(name))

    @classproperty
    def global_filepath(cls):
        return cls.settings.filename

    @classmethod
    def session_filepath(cls, session: LoggerSession):
        return session.path / cls.settings.session_filename
