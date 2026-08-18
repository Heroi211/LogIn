from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from contexts.identity_access.domain.entities.permission import Permission
from contexts.identity_access.domain.exceptions import DuplicateUserError, PermissionNotFoundError, RoleNotFoundError
from contexts.identity_access.infrastructure.persistence.models.permissions import (
    Permissions,
    role_permissions_table,
)
from contexts.identity_access.infrastructure.persistence.models.roles import Roles


def _orm_to_permission(entity: Permissions) -> Permission:
    return Permission(
        id=entity.id,
        code=entity.code,
        description=entity.description,
        module=entity.module,
        active=entity.active,
    )


class SqlAlchemyPermissionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_active(self) -> list[Permission]:
        result = await self._session.execute(
            select(Permissions)
            .filter(Permissions.active.is_(True))
            .order_by(Permissions.module.asc(), Permissions.code.asc())
        )
        return [_orm_to_permission(p) for p in result.scalars().all()]

    async def get_by_code(self, code: str) -> Permission | None:
        result = await self._session.execute(
            select(Permissions).filter(Permissions.code == code.strip().lower())
        )
        entity = result.scalars().one_or_none()
        return _orm_to_permission(entity) if entity else None

    async def add(self, permission: Permission) -> Permission:
        existing = await self.get_by_code(permission.code)
        if existing:
            raise DuplicateUserError(f"Permissão {permission.code!r} já cadastrada.")

        entity = Permissions(
            code=permission.code,
            description=permission.description,
            module=permission.module,
            active=permission.active,
        )
        self._session.add(entity)
        await self._session.commit()
        await self._session.refresh(entity)
        return _orm_to_permission(entity)

    async def get_codes_for_role(self, role_id: int) -> frozenset[str]:
        result = await self._session.execute(
            select(Permissions.code)
            .join(role_permissions_table, Permissions.id == role_permissions_table.c.permission_id)
            .filter(
                role_permissions_table.c.role_id == role_id,
                Permissions.active.is_(True),
            )
        )
        return frozenset(result.scalars().all())

    async def list_codes_for_role(self, role_id: int) -> list[str]:
        codes = await self.get_codes_for_role(role_id)
        return sorted(codes)

    async def set_role_permissions(self, role_id: int, permission_codes: list[str]) -> frozenset[str]:
        result = await self._session.execute(
            select(Roles).options(selectinload(Roles.permissions)).filter(Roles.id == role_id)
        )
        role = result.scalars().unique().one_or_none()
        if role is None:
            raise RoleNotFoundError(f"Papel id={role_id} não encontrado.")

        normalized = sorted({code.strip().lower() for code in permission_codes})
        if normalized:
            perm_result = await self._session.execute(
                select(Permissions).filter(
                    Permissions.code.in_(normalized),
                    Permissions.active.is_(True),
                )
            )
            permissions = list(perm_result.scalars().all())
            found = {p.code for p in permissions}
            missing = set(normalized) - found
            if missing:
                raise PermissionNotFoundError(
                    f"Permissões não encontradas: {', '.join(sorted(missing))}"
                )
        else:
            permissions = []

        role.permissions = permissions
        await self._session.commit()
        return frozenset(p.code for p in permissions)
