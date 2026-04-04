"""Structured result type returned by all helpers."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StepLog:
    step: str
    detail: str


@dataclass
class HelperResult:
    success: bool
    log: list[StepLog] = field(default_factory=list)
    result: Any = None

    def add_step(self, step: str, detail: str) -> "HelperResult":
        self.log.append(StepLog(step=step, detail=detail))
        return self
