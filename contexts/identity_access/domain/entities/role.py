from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Role:
    id: int | None
    description: str
    active: bool
    permission_codes: frozenset[str] = field(default_factory=frozenset)

    @classmethod
    def create(cls, description: str, active: bool = True) -> Role:
        return cls(id=None, description=description, active=active)

    def deactivate(self) -> None:
        self.active = False

    def update(self, *, description: str | None = None, active: bool | None = None) -> None:
        if description is not None:
            self.description = description
        if active is not None:
            self.active = active

    def set_permissions(self, codes: frozenset[str]) -> None:
        self.permission_codes = codes
