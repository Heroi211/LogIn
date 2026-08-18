"""
API pública do bounded context Identity & Access.

Outros contextos (ex.: Ticket Management) devem importar **somente** deste módulo
— nunca de infrastructure.persistence ou entities internas completas.
"""

from contexts.identity_access.domain.audit.actions import AuditAction
from contexts.identity_access.domain.permission import Permission
from contexts.identity_access.domain.role_type import RoleType
from contexts.identity_access.domain.value_objects.user_id import UserId

__all__ = [
    "AuditAction",
    "Permission",
    "RoleType",
    "UserId",
]
