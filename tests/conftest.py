import logging
import os
import pytest
from pathlib import Path


@pytest.fixture(autouse=True)
def reset_logger_manager():
    from logger import LoggerManager

    root = logging.getLogger()
    saved_handlers = root.handlers[:]
    saved_level = root.level

    saved_settings = getattr(LoggerManager, "settings", None)
    saved_cached = getattr(LoggerManager, "_cached_names", None)

    root.handlers.clear()

    yield

    root.handlers.clear()
    root.handlers.extend(saved_handlers)
    root.setLevel(saved_level)

    LoggerManager.settings = saved_settings
    if saved_cached is not None:
        LoggerManager._cached_names = saved_cached


@pytest.fixture(autouse=True)
def clear_log_env(monkeypatch):
    for key in list(os.environ):
        if key.startswith("LOG_"):
            monkeypatch.delenv(key, raising=False)


@pytest.fixture
def logs_dir(tmp_path: Path) -> Path:
    d = tmp_path / "logs"
    d.mkdir()
    return d


@pytest.fixture
def session_dir(tmp_path: Path) -> Path:
    d = tmp_path / "session"
    d.mkdir()
    return d


@pytest.fixture
def init_global(logs_dir):
    from logger import LoggerManager, LoggerFormatType, LogLevel

    def _init(**overrides):
        kwargs = dict(
            format_type=LoggerFormatType.DEBUG,
            level=LogLevel.DEBUG,
            name_size=10,
            session_level=LogLevel.INFO,
            enable_file_handlers=True,
            global_dir=logs_dir,
        )
        kwargs.update(overrides)
        return LoggerManager.init_global_logger(**kwargs)

    return _init
