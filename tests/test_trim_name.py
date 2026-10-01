import pytest
from logger import LoggerManager


@pytest.fixture
def init_no_files(init_global):
    return init_global(enable_file_handlers=False)


def test_trim_name_short_name_unchanged(init_no_files):
    assert LoggerManager.trim_name("foo", 10) == "foo"


def test_trim_name_long_name_is_trimmed(init_no_files):
    result = LoggerManager.trim_name("test1.test2.test3.test4.test5", 10)
    assert result == "t.t.t.t.test5"


def test_trim_name_keeps_full_class_name(init_no_files):
    result = LoggerManager.trim_name("test1.test2.test3.MyClass", 10)
    assert result.endswith("MyClass")


def test_trim_name_keeps_session_id(init_no_files):
    result = LoggerManager.trim_name("test1.test2:1234567890", 10)
    assert result.endswith(":1234567890")


def test_trim_name_class_and_session_together(init_no_files):
    result = LoggerManager.trim_name(
        "test1.test2.test3.test4.test5.test6:12345667890", 10
    )
    assert "test6" in result
    assert "12345667890" in result
