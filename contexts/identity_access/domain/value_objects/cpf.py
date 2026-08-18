from __future__ import annotations

import re
from dataclasses import dataclass

_DIGITS_RE = re.compile(r"\D")


@dataclass(frozen=True, slots=True)
class CPF:
    value: str

    def __post_init__(self) -> None:
        digits = _DIGITS_RE.sub("", self.value)
        if len(digits) not in (11, 12):
            raise ValueError(f"CPF inválido: {self.value}")
        object.__setattr__(self, "value", digits)

    def __str__(self) -> str:
        return self.value
