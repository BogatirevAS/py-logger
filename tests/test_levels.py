import pytest

from logger import LogLevel, LoggerSettings, LoggerManager


def test_log_level_accepts_lowercase():
    assert LogLevel("debug") == LogLevel.DEBUG
    assert LogLevel("info") == LogLevel.INFO


def test_log_level_accepts_mixed_case():
    assert LogLevel("DeBuG") == LogLevel.DEBUG


def test_log_level_rejects_unknown():
    with pytest.raises(ValueError):
        LogLevel("nope")


def test_settings_level_from_env_lowercase(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "debug")
    assert LoggerSettings().level == LogLevel.DEBUG


def test_init_global_logger_accepts_lowercase(init_global):
    init_global(level="debug")
    assert LoggerManager.settings.level == LogLevel.DEBUG
