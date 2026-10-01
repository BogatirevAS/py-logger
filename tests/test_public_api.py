import logger


def test_public_api_exports():
    expected = {
        "LoggerManager", "LoggerSettings", "LoggerSession",
        "LogLevel", "LoggerFormatType",
        "LoggerMixin", "ClassLoggerMixin",
        "ValidateMixin", "SettingsCreateOrUpdateMixin",
        "Decoratable", "classproperty",
    }
    assert expected == set(logger.__all__)


def test_all_names_exist():
    for name in logger.__all__:
        assert hasattr(logger, name), f"{name} no export in __all__"
