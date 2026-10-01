from logger import LoggerManager


def test_get_logger_name_for_instance(init_global):
    init_global(enable_file_handlers=False)

    class TestInstance:
        pass

    name = LoggerManager.get_logger_name(TestInstance())
    assert "TestInstance" in name


def test_get_logger_name_for_class(init_global):
    init_global(enable_file_handlers=False)

    class TestClass:
        pass

    name = LoggerManager.get_logger_name(TestClass)
    assert "TestClass" in name


def test_get_logger_name_for_string(init_global):
    init_global(enable_file_handlers=False)
    assert LoggerManager.get_logger_name("foo.bar") == "foo.bar"


def test_get_logger_name_respects_name_size(init_global):
    name_size = 30
    init_global(name_size=name_size, enable_file_handlers=False)
    short_module = "a123.b123.c123.d123.e123.f123.SomeClassName"
    long_module = "a123.b123.c123.d123.e123.f123.SomeVeryLongClassName"
    name = LoggerManager.get_logger_name(short_module)
    print(name)
    assert len(name) <= name_size and name.endswith("SomeClassName")
    name = LoggerManager.get_logger_name(long_module)
    print(name)
    assert len(name.split("SomeVeryLongClassName")[0]) == 12 and name.endswith("SomeVeryLongClassName")
