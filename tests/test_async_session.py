import asyncio
import pytest

from logger import LoggerManager, LoggerSession, LoggerMixin


async def test_async_scope_yields(init_global, session_dir):
    init_global()
    session = LoggerSession(id="a1", path=session_dir)

    entered = False
    async with LoggerManager.async_session_scope(session):
        entered = True

    assert entered


async def test_async_scope_writes_to_session_file(init_global, session_dir):
    init_global()
    session = LoggerSession(id="a2", path=session_dir)

    async with LoggerManager.async_session_scope(session):
        LoggerManager.get_logger("test").info("from async")

    content = LoggerManager.session_filepath(session).read_text()
    assert "from async" in content


async def test_async_scope_cleanup_after_exit(init_global, session_dir):
    init_global()
    log = LoggerManager.get_logger("test")
    session = LoggerSession(id="a3", path=session_dir)

    async with LoggerManager.async_session_scope(session):
        log.info("inside")

    log.info("outside")

    content = LoggerManager.session_filepath(session).read_text()
    assert "inside" in content
    assert "outside" not in content


async def test_async_scope_cleanup_on_exception(init_global, session_dir):
    init_global()
    log = LoggerManager.get_logger("test")
    session = LoggerSession(id="a4", path=session_dir)

    with pytest.raises(RuntimeError):
        async with LoggerManager.async_session_scope(session):
            log.info("before crash")
            raise RuntimeError("boom")

    log.info("after crash")

    content = LoggerManager.session_filepath(session).read_text()
    assert "after crash" not in content


async def test_async_scope_cleanup_on_cancellation(init_global, session_dir):
    init_global()
    log = LoggerManager.get_logger("test")
    session = LoggerSession(id="a5", path=session_dir)

    async def worker():
        async with LoggerManager.async_session_scope(session):
            log.info("inside worker")
            await asyncio.sleep(10)

    task = asyncio.create_task(worker())
    await asyncio.sleep(0.05)
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    log.info("after cancel")

    content = LoggerManager.session_filepath(session).read_text()
    assert "inside worker" in content
    assert "after cancel" not in content


async def test_concurrent_sessions_do_not_interfere(init_global, tmp_path):
    init_global()

    dir_a = tmp_path / "a"
    dir_b = tmp_path / "b"
    dir_a.mkdir()
    dir_b.mkdir()

    session_a = LoggerSession(id="A", path=dir_a)
    session_b = LoggerSession(id="B", path=dir_b)

    log = LoggerManager.get_logger("shared")

    async def worker(session, tag, delay):
        async with LoggerManager.async_session_scope(session):
            for i in range(5):
                log.info(f"{tag}-{i}")
                await asyncio.sleep(delay)

    await asyncio.gather(
        worker(session_a, "A", 0.01),
        worker(session_b, "B", 0.01),
    )

    content_a = LoggerManager.session_filepath(session_a).read_text()
    content_b = LoggerManager.session_filepath(session_b).read_text()

    assert "A-0" in content_a
    assert "A-4" in content_a
    assert "B-0" not in content_a
    assert "B-4" not in content_a

    assert "B-0" in content_b
    assert "B-4" in content_b
    assert "A-0" not in content_b
    assert "A-4" not in content_b


async def test_logger_mixin_in_async_method(init_global):
    init_global()

    class MyService(LoggerMixin):
        async def do_work(self):
            self.logger.info("from async method")
            await asyncio.sleep(0)

    await MyService().do_work()

    content = LoggerManager.global_filepath.read_text()
    assert "from async method" in content


async def test_nested_async_scopes(init_global, tmp_path):
    init_global()
    outer_dir = tmp_path / "outer"
    inner_dir = tmp_path / "inner"
    outer_dir.mkdir()
    inner_dir.mkdir()

    outer = LoggerSession(id="outer", path=outer_dir)
    inner = LoggerSession(id="inner", path=inner_dir)

    log = LoggerManager.get_logger("t")

    async with LoggerManager.async_session_scope(outer):
        log.info("in outer")
        async with LoggerManager.async_session_scope(inner):
            log.info("in inner")
        log.info("back to outer")

    outer_content = LoggerManager.session_filepath(outer).read_text()
    inner_content = LoggerManager.session_filepath(inner).read_text()

    assert "in outer" in outer_content
    assert "back to outer" in outer_content
    assert "in inner" in inner_content


async def test_async_matches_sync_behavior(init_global, session_dir, tmp_path):
    init_global()

    sync_dir = tmp_path / "sync"
    sync_dir.mkdir()

    sync_session = LoggerSession(id="S", path=sync_dir)
    async_session = LoggerSession(id="A", path=session_dir)

    log = LoggerManager.get_logger("t")

    with LoggerManager.session_scope(sync_session):
        log.info("hello")

    async with LoggerManager.async_session_scope(async_session):
        log.info("hello")

    sync_content = LoggerManager.session_filepath(sync_session).read_text()
    async_content = LoggerManager.session_filepath(async_session).read_text()

    assert "hello" in sync_content
    assert "hello" in async_content
