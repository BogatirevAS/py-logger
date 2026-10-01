from pathlib import Path
from pydantic import BaseModel


class LoggerSession(BaseModel):
    id: str
    path: Path | None
