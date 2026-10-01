import pytest
from pydantic import ValidationError
from logger import LoggerSettings, LogLevel, LoggerFormatType


def test_settings_defaults():
    s = LoggerSettings()
    assert s.level == LogLevel.INFO
    assert s.format_type == LoggerFormatType.DEFAULT
    assert s.name_size > 0


def test_settings_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("LOG_NAME_SIZE", "20")
    monkeypatch.setenv("LOG_GLOBAL_DIR", str(tmp_path))

    s = LoggerSettings()
    assert s.level == LogLevel.DEBUG
    assert s.name_size == 20
    assert s.global_dir == tmp_path


def test_settings_env_overrides_defaults(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    s = LoggerSettings(level=LogLevel.ERROR)
    assert LoggerSettings().level == LogLevel.WARNING
    assert s.level == LogLevel.ERROR


def test_settings_rejects_invalid_level():
    with pytest.raises(ValidationError):
        LoggerSettings(level="NOT_A_LEVEL")


def test_settings_accepts_string_level():
    assert LoggerSettings(level="DEBUG").level == LogLevel.DEBUG
