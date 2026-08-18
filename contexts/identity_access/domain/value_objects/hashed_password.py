from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HashedPassword:
    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("Hash de senha não pode ser vazio")
