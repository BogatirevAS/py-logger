import pytest

from logger import LoggerManager, LoggerSession


def test_global_logger_writes_to_file(init_global):
    init_global()
    log = LoggerManager.get_logger("test1.test2")
    log.warning("test warning")
    log.info("test info")
    log.debug("test debug")

    content = LoggerManager.global_filepath.read_text()
    assert "test warning" in content
    assert "test info" in content
    assert "test debug" in content


def test_global_logger_respects_level(init_global):
    init_global(level="WARNING")
    log = LoggerManager.get_logger("test")
    log.debug("should not appear")
    log.warning("should appear")

    content = LoggerManager.global_filepath.read_text()
    assert "should not appear" not in content
    assert "should appear" in content


def test_no_file_handlers_means_no_file(init_global):
    init_global(enable_file_handlers=False)
    log = LoggerManager.get_logger("test")
    log.info("hello")
    assert not LoggerManager.global_filepath.exists()


def test_session_writes_to_separate_file(init_global, session_dir):
    init_global()
    session = LoggerSession(id="123", path=session_dir)
    with LoggerManager.session_scope(session):
        log = LoggerManager.get_logger("test")
        log.warning("session warning")
        log.info("session info")

    session_file = LoggerManager.session_filepath(session)
    assert session_file.exists()
    content = session_file.read_text()
    assert "session warning" in content
    assert "session info" in content


def test_session_file_contains_session_id(init_global, session_dir):
    init_global()
    session = LoggerSession(id="abc-123", path=session_dir)
    with LoggerManager.session_scope(session):
        log = LoggerManager.get_logger("test")
        log.info("inside")

    content = LoggerManager.session_filepath(session).read_text()
    assert "abc-123" in content


def test_session_level_filters_debug(init_global, session_dir):
    init_global(level="DEBUG", session_level="INFO")
    session = LoggerSession(id="1", path=session_dir)
    with LoggerManager.session_scope(session):
        log = LoggerManager.get_logger("test")
        log.debug("debug msg")
        log.info("info msg")

    content = LoggerManager.session_filepath(session).read_text()
    assert "debug msg" not in content
    assert "info msg" in content


def test_global_logger_also_receives_session_messages(init_global, session_dir):
    init_global()
    session = LoggerSession(id="1", path=session_dir)
    with LoggerManager.session_scope(session):
        log = LoggerManager.get_logger("test")
        log.info("both files")

    global_content = LoggerManager.global_filepath.read_text()
    session_content = LoggerManager.session_filepath(session).read_text()
    assert "both files" in global_content
    assert "both files" in session_content


def test_session_removes_handler_after_exit(init_global, session_dir):
    init_global()
    log = LoggerManager.get_logger("test")
    session = LoggerSession(id="1", path=session_dir)
    with LoggerManager.session_scope(session):
        log.info("inside")

    log.info("outside")

    session_content = LoggerManager.session_filepath(session).read_text()
    assert "inside" in session_content
    assert "outside" not in session_content


def test_session_cleanup_on_exception(init_global, session_dir):
    init_global()
    log = LoggerManager.get_logger("test")
    session = LoggerSession(id="1", path=session_dir)
    with pytest.raises(RuntimeError):
        with LoggerManager.session_scope(session):
            log.info("before crash")
            raise RuntimeError("boom")

    log.info("after crash")
    session_content = LoggerManager.session_filepath(session).read_text()
    assert "after crash" not in session_content
