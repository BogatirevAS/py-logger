from pathlib import Path
from typing import Any, Optional, TypedDict
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from logger import base
from logger.enums import LoggerFormatType, LogLevel
from logger.mixins.settings import SettingsCreateOrUpdateMixin


class LoggerSettingsKwargs(TypedDict, total=False):
    name_size: int
    format_type: LoggerFormatType
    default_format: str
    debug_format: str
    datefmt: str | None
    global_filename: str
    global_dir: Optional[Path]
    session_filename: str
    level: LogLevel
    session_level: LogLevel
    max_bytes: int
    backup_count: int
    enable_file_handlers: bool


class LoggerSettings(BaseSettings, SettingsCreateOrUpdateMixin):
    model_config = SettingsConfigDict(env_prefix="LOG_", extra="ignore", env_ignore_empty=True)

    name_size: int = 30
    format_type: LoggerFormatType = LoggerFormatType.DEFAULT
    default_format: str = "%(asctime)s %(levelname)s [%(name)s] - %(message)s"
    debug_format: str = "%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(funcName)s - %(message)s"
    datefmt: str | None = None
    global_filename: str = "global.log"
    global_dir: Optional[Path] = "logs"
    session_filename: str = "session.log"
    level: LogLevel = LogLevel.INFO
    session_level: LogLevel = LogLevel.INFO
    max_bytes: int = 1024 * 1024 * 10
    backup_count: int = 5
    enable_file_handlers: bool = False
    force: bool = True

    @computed_field
    @property
    def filename(self) -> Path:
        return Path(*[self.global_dir, self.global_filename] if self.global_dir else [self.global_filename])

    @computed_field
    @property
    def format(self) -> str:
        return getattr(self, f"{self.format_type.value}_format")

    @computed_field
    @property
    def formatter(self) -> base.Formatter:
        return base.Formatter(
            fmt=self.format,
            datefmt=self.datefmt
        )

    @computed_field
    @property
    def handlers(self) -> list[base.Handler]:
        stream = base.StreamHandler()
        stream.setLevel(self.level.numeric)
        stream.setFormatter(self.formatter)

        handlers = [stream]
        if self.enable_file_handlers:
            self.filename.parent.mkdir(parents=True, exist_ok=True)
            file = base.RotatingFileHandler(
                filename=self.filename,
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
            )
            file.setLevel(self.level.numeric)
            file.setFormatter(self.formatter)
            handlers.append(file)

        return handlers

    @computed_field
    @property
    def root_level(self) -> int:
        levels = [self.level.numeric, self.session_level.numeric]
        return min(levels)

    @computed_field
    @property
    def config(self) -> dict[str, Any]:
        return {
            "level": self.root_level,
            "handlers": self.handlers,
            "force": self.force,
        }
