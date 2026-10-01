import pytest
from logger import (
    LoggerManager, LoggerSession,
    LoggerMixin, ClassLoggerMixin, ValidateMixin,
)


def test_logger_mixin_instance_has_logger(init_global):
    init_global()

    class MyClass(LoggerMixin):
        pass

    obj = MyClass()
    assert obj.logger is not None
    obj.logger.info("from instance")
    assert "from instance" in LoggerManager.global_filepath.read_text()


def test_logger_mixin_two_instances_share_logger_by_class(init_global):
    init_global()

    class MyClass(LoggerMixin):
        pass

    a, b = MyClass(), MyClass()
    assert a.logger is b.logger


def test_class_logger_mixin_on_class(init_global):
    init_global()

    class MyClass(ClassLoggerMixin):
        pass

    MyClass.logger.info("from class")
    assert "from class" in LoggerManager.global_filepath.read_text()


def test_class_logger_mixin_name_contains_class_name(init_global):
    init_global()

    class MyClass(ClassLoggerMixin):
        pass

    assert "MyClass" in MyClass.logger.name


def test_validate_mixin_disabled_does_not_raise(init_global):
    init_global()

    class MyClass(ValidateMixin):
        pass

    obj = MyClass(validate=False)
    obj.validate_msg("")


def test_validate_mixin_raises_on_invalid(init_global):
    init_global()

    class MyClass(ValidateMixin):
        pass

    obj = MyClass(validate=True)
    with pytest.raises(AttributeError):
        obj.validate_msg("")


def test_mixin_logger_picks_up_session_file(init_global, session_dir):
    init_global()
    session = LoggerSession(id="1", path=session_dir)
    with LoggerManager.session_scope(session):
        class MyClass(LoggerMixin):
            pass

        MyClass().logger.info("inside session")

    content = LoggerManager.session_filepath(session).read_text()
    assert "inside session" in content
