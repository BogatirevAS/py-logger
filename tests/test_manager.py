import logging
from logger import LoggerManager


def test_init_global_logger_clears_existing_handlers(init_global):
    root = logging.getLogger()
    old_handler = logging.NullHandler()
    root.addHandler(old_handler)
    assert old_handler in root.handlers

    init_global()

    assert old_handler not in root.handlers


def test_init_global_logger_is_idempotent(init_global):
    init_global()
    n1 = len(logging.getLogger().handlers)
    init_global()
    n2 = len(logging.getLogger().handlers)
    assert n1 == n2


def test_get_logger_returns_same_instance(init_global):
    init_global()
    a = LoggerManager.get_logger("shared")
    b = LoggerManager.get_logger("shared")
    assert a is b


def test_get_logger_name_is_cached(init_global):
    init_global(enable_file_handlers=False)

    class Foo:
        pass

    n1 = LoggerManager.get_logger_name(Foo())
    n2 = LoggerManager.get_logger_name(Foo())
    assert n1 == n2
