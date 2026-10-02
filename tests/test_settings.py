from pathlib import Path
import pytest
from pydantic import ValidationError
from logger import LoggerSettings, LogLevel, LoggerFormatType


FIELDS = set(LoggerSettings.model_fields)


def test_settings_defaults():
    s = LoggerSettings()
    assert s.model_dump(include=FIELDS) == {
        "name_size": 30,
        "format_type": LoggerFormatType.DEFAULT,
        "default_format": "%(asctime)s %(levelname)s [%(name)s] - %(message)s",
        "debug_format": "%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(funcName)s - %(message)s",
        "datefmt": None,
        "global_filename": "global.log",
        "global_dir": Path("logs"),
        "session_filename": "session.log",
        "level": LogLevel.INFO,
        "session_level": LogLevel.INFO,
        "max_bytes": 10 * 1024 * 1024,
        "backup_count": 5,
        "enable_file_handlers": False,
        "force": True,
    }


@pytest.mark.parametrize("env_name,value,attr,expected", [
    ("LOG_NAME_SIZE", "20", "name_size", 20),
    ("LOG_FORMAT_TYPE", "debug", "format_type", LoggerFormatType.DEBUG),
    ("LOG_DEFAULT_FORMAT", "X %(message)s", "default_format", "X %(message)s"),
    ("LOG_DATEFMT", "%H:%M", "datefmt", "%H:%M"),
    ("LOG_GLOBAL_FILENAME", "g.log", "global_filename", "g.log"),
    ("LOG_SESSION_FILENAME", "s.log", "session_filename", "s.log"),
    ("LOG_LEVEL", "debug", "level", LogLevel.DEBUG),
    ("LOG_SESSION_LEVEL", "warning", "session_level", LogLevel.WARNING),
    ("LOG_MAX_BYTES", "100", "max_bytes", 100),
    ("LOG_BACKUP_COUNT", "3", "backup_count", 3),
    ("LOG_ENABLE_FILE_HANDLERS", "true", "enable_file_handlers", True),
    ("LOG_FORCE", "false", "force", False),
])
def test_settings_each_env_var(monkeypatch, env_name, value, attr, expected):
    monkeypatch.setenv(env_name, value)
    s = LoggerSettings()
    assert getattr(s, attr) == expected


def test_settings_global_dir_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv("LOG_GLOBAL_DIR", str(tmp_path))
    assert LoggerSettings().global_dir == tmp_path


def test_settings_empty_string_uses_default(monkeypatch):
    monkeypatch.setenv("LOG_DATEFMT", "")
    monkeypatch.setenv("LOG_GLOBAL_DIR", "")
    s = LoggerSettings()
    assert s.datefmt is None
    assert s.global_dir == Path("logs")


def test_settings_reads_env_when_no_arg(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    assert LoggerSettings().level == LogLevel.WARNING


def test_settings_explicit_arg_wins_over_env(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    assert LoggerSettings(level=LogLevel.ERROR).level == LogLevel.ERROR


def test_settings_rejects_invalid_level():
    with pytest.raises(ValidationError):
        LoggerSettings(level="NOT_A_LEVEL")


def test_settings_accepts_string_level():
    assert LoggerSettings(level="DEBUG").level == LogLevel.DEBUG


def test_settings_computed_filename():
    s = LoggerSettings(global_dir=Path("/tmp/x"), global_filename="app.log")
    assert s.filename == Path("/tmp/x/app.log")


@pytest.mark.parametrize("ft,expected_attr", [
    (LoggerFormatType.DEFAULT, "default_format"),
    (LoggerFormatType.DEBUG, "debug_format"),
])
def test_settings_format_matches_format_type(ft, expected_attr):
    s = LoggerSettings(format_type=ft)
    assert s.format == getattr(s, expected_attr)


def test_settings_rejects_invalid_format_type():
    with pytest.raises(ValidationError):
        LoggerSettings(format_type="nope")
