"""Dependencies reutilizáveis de controle de acesso (RBAC + API key scopes)."""

from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status

from core.deps import get_current_user
from models.roles import Roles
from models.users import Users

_FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Você não possui permissão para acessar este recurso.",
)

_SCOPE_FORBIDDEN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Escopo da API Key insuficiente para esta operação.",
)


def _normalize_scopes(raw: str | None) -> set[str]:
    if not raw:
        return {"read"}
    return {part.strip().lower() for part in raw.split(",") if part.strip()}


def _check_api_key_scope(request: Request) -> None:
    if getattr(request.state, "auth_method", None) != "api_key":
        return

    scopes = _normalize_scopes(getattr(request.state, "api_key_scopes", "read"))
    if "admin" in scopes:
        return

    method = request.method.upper()
    if method in {"GET", "HEAD", "OPTIONS"}:
        if "read" in scopes or "write" in scopes:
            return
        raise _SCOPE_FORBIDDEN

    if "write" not in scopes:
        raise _SCOPE_FORBIDDEN


def require_role(*allowed_roles: int) -> Callable:
    """Exige role_id + escopo de API key quando aplicável."""

    async def _checker(
        request: Request,
        user: Users = Depends(get_current_user),
    ) -> Users:
        _check_api_key_scope(request)
        if user.role_id not in allowed_roles:
            raise _FORBIDDEN
        return user

    return _checker


require_operator = require_role(Roles.OPERATOR, Roles.ADMINISTRATOR)
require_admin = require_role(Roles.ADMINISTRATOR)
