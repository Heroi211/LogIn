from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserId:
    """Identificador de usuário na fronteira entre bounded contexts."""

    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise ValueError(f"UserId inválido: {self.value}")

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        return str(self.value)
