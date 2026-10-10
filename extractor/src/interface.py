from pathlib import Path
from typing import Protocol

import pandas as pd


class Browser(Protocol):
    def fetch(self, url: str) -> bytes | None:
        ...

class Storage(Protocol):
    def save(self, table: pd.DataFrame, path: Path) -> bool:
        ...
    def exists(self, path: Path) -> bool:
        ...

class Orchestrator(Protocol):
    def chapter(self, url: str, chapter: int, output: Path) -> bool:
        ...
    def schedule(self, url: str, date: str) -> bool:
        ...
    def all(self, schedules: dict[str, str]) -> bool:
        ...
