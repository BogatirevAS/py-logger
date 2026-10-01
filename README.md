# Logger

A wrapper around the standard `logging` module featuring Pydantic-based configuration, class mixins,
and support for session-specific logs. It enables centralized logging configuration via environment
variables or code, allows adding a logger to a class through simple inheritance, and supports writing
specific log entries to a separate file within a given context.
-----

## Table of Contents

- [Installation](#installation)
- [Environment](#environment)
- [Examples](#examples)

## Installation

- console
```console
pip install git+https://github.com/BogatirevAS/py-logger.git@master
```
```console
pip install git+https://github.com/BogatirevAS/py-logger.git@0.1.0
```

- requirements.txt
```requirements
logger @ git+https://github.com/BogatirevAS/py-logger.git@master
```
```requirements
logger @ git+https://github.com/BogatirevAS/py-logger.git@0.1.0
```

## Environment
.env
```properties
LOG_NAME_SIZE=30
LOG_FORMAT_TYPE="default"
LOG_DEFAULT_FORMAT="%(asctime)s %(levelname)s [%(name)s] - %(message)s"
LOG_DEBUG_FORMAT="%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(funcName)s - %(message)s"
LOG_DATEFMT=
LOG_GLOBAL_FILENAME="global.log"
LOG_GLOBAL_DIR="logs"
LOG_SESSION_FILENAME="session.log"
LOG_LEVEL="INFO"
LOG_SESSION_LEVEL="INFO"
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
LOG_ENABLE_FILE_HANDLERS="False"
LOG_FORCE="True"
```

## Examples
1. Init loggers by settings object, env and kwargs
    ```python
    from dotenv import load_dotenv
    from logger import LoggerManager, LogLevel
    
    load_dotenv()
    # valid levels is LogLevel or case-insensitive string
    LoggerManager.init_global_logger(level=LogLevel.INFO, session_level="debug", enable_file_handlers=True)
    print(LoggerManager.settings.model_dump())
    ```
2. Simple loggers
    ```python
    from logger import LoggerManager
    
    LoggerManager.init_global_logger()
    
    logger_by_str = LoggerManager.get_named_logger("test")
    logger_by_str.info("1")
    logger_by_module_name = LoggerManager.get_named_logger(__name__)
    logger_by_module_name.info("2")
    
    class TestClass:
        pass
    
    logger_by_class = LoggerManager.get_named_logger(TestClass)
    logger_by_class.info("3")
    logger_by_obj = LoggerManager.get_named_logger(TestClass())
    logger_by_obj.info("4")
    ```
3. Class loggers by mixins
    ```python
    from logger import LoggerManager, LoggerMixin, ClassLoggerMixin, ValidateMixin
    
    LoggerManager.init_global_logger()
    
    class TestClass(LoggerMixin):
        pass
    
    TestClass().logger.info("1")
    
    class TestClass2(ClassLoggerMixin):
        pass
    
    TestClass2.logger.info("2")
    
    class TestClass3(ValidateMixin):
        def __init__(self):
            super().__init__(validate=False)
    
    TestClass3().validate_msg("3")  # For validate errors in another packages
    ```
4. Session scope
    ```python
    from pathlib import Path
    from logger import LoggerManager, LoggerSession, LogLevel
    
    LoggerManager.init_global_logger(enable_file_handlers=True, session_level=LogLevel.DEBUG, level=LogLevel.INFO)
    
    session = LoggerSession(id="123", path=Path("logs", "123"))
    with LoggerManager.session_scope(session):  # async with LoggerManager.async_session_scope(session)
        # Scope intercepts logs, add session id to logger name and write session log file (if path is not None)
        logger = LoggerManager.get_named_logger("Test")
        logger.debug("Write text only in file \"logs/123/session.log\"")
        logger.info("Write text in both files \"logs/global.log\" and \"logs/123/session.log\"")
    ```
