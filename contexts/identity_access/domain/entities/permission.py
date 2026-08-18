from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Permission:
    """Permissão nomeada (recurso:ação) — catálogo gerenciável no banco."""

    id: int | None
    code: str
    description: str
    module: str | None = None
    active: bool = True

    @classmethod
    def create(
        cls,
        *,
        code: str,
        description: str,
        module: str | None = None,
        active: bool = True,
    ) -> Permission:
        return cls(
            id=None,
            code=code.strip().lower(),
            description=description.strip(),
            module=module.strip() if module else None,
            active=active,
        )

    def deactivate(self) -> None:
        self.active = False
