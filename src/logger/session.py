from __future__ import annotations

from contextlib import asynccontextmanager
from contextvars import ContextVar, Token
from typing import AsyncIterator, Optional

from logger import base
from logger.models import LoggerSession


_current_session: ContextVar[Optional[LoggerSession]] = ContextVar(
    "logger_session", default=None
)

_record_factory_installed = False


def install_record_factory() -> None:
    global _record_factory_installed
    if _record_factory_installed:
        return

    original_factory = base.getLogRecordFactory()

    def factory(*args, **kwargs) -> base.LogRecord:
        record = original_factory(*args, **kwargs)
        session = _current_session.get()
        if session is not None:
            record.name = f"{record.name}:{session.id}"
        return record

    base.setLogRecordFactory(factory)
    _record_factory_installed = True


class _SessionLoggerFilter(base.Filter):
    def __init__(self, session_id: str) -> None:
        super().__init__(name="")
        self.session_id = session_id

    def filter(self, record: base.LogRecord) -> bool:
        session = _current_session.get()
        return session is not None and session.id == self.session_id


class _SessionLoggerScope:
    def __init__(self, session: LoggerSession) -> None:
        self.session = session
        self._token: Optional[Token] = None
        self._handler: Optional[base.Handler] = None

    def __enter__(self) -> "_SessionLoggerScope":
        from .manager import LoggerManager

        self._token = _current_session.set(self.session)

        settings = LoggerManager.settings
        if settings.enable_file_handlers and self.session.path is not None:
            filepath = self.session.path / settings.session_filename
            filepath.parent.mkdir(parents=True, exist_ok=True)

            handler = base.FileHandler(filepath, encoding="utf-8")
            handler.setLevel(settings.session_level.numeric)
            handler.setFormatter(settings.formatter)
            handler.addFilter(_SessionLoggerFilter(self.session.id))

            base.getLogger().addHandler(handler)
            self._handler = handler

        return self

    def __exit__(self, *exc) -> None:
        if self._handler is not None:
            base.getLogger().removeHandler(self._handler)
            self._handler.close()
            self._handler = None
        if self._token is not None:
            _current_session.reset(self._token)
            self._token = None


def session_logger_scope(session: LoggerSession) -> _SessionLoggerScope:
    return _SessionLoggerScope(session)


@asynccontextmanager
async def async_session_logger_scope(session: LoggerSession) -> AsyncIterator[None]:
    with _SessionLoggerScope(session):
        yield
