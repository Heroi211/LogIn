from typing import Any, Protocol

from contexts.identity_access.application.dto.audit import AuditRecord


class AuditLogger(Protocol):
    async def record(self, event: AuditRecord) -> None: ...
