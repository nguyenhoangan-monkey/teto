from pathlib import Path
from typing import Protocol

import pandas as pd


class Browser(Protocol):
    def fetch(self, url: str) -> bytes | None:
        ...

class Storage(Protocol):
    def save(self, table: pd.DataFrame, path: Path) -> None:
        ...
    def exists(self, path: Path) -> None:
        ...

class Orchestrator(Protocol):
    def chapter(self, url: str, chapter: int, output: Path) -> None:
        ...
    def schedule(self, url: str, date: str) -> None:
        ...
    def all(self, schedules: dict[str, str]) -> None:
        ...
