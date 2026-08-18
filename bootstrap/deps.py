"""Injeção de dependências (composition root)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from bootstrap.session import get_session
from contexts.identity_access.application.use_cases.roles.create_role import CreateRole
from contexts.identity_access.application.use_cases.roles.deactivate_role import DeactivateRole
from contexts.identity_access.application.use_cases.roles.get_role import GetRoleById
from contexts.identity_access.application.use_cases.roles.list_roles import ListRoles
from contexts.identity_access.application.use_cases.roles.update_role import UpdateRole
from contexts.identity_access.application.use_cases.users.authenticate_user import AuthenticateUser
from contexts.identity_access.application.use_cases.users.block_user import BlockUser
from contexts.identity_access.application.use_cases.users.deactivate_user import DeactivateUser
from contexts.identity_access.application.use_cases.users.get_user import GetUserById
from contexts.identity_access.application.use_cases.users.list_users import ListUsers
from contexts.identity_access.application.use_cases.users.register_user import RegisterUser
from contexts.identity_access.application.use_cases.users.request_password_reset import RequestPasswordReset
from contexts.identity_access.application.use_cases.users.reset_password import ResetPassword
from contexts.identity_access.application.use_cases.users.unblock_user import UnblockUser
from contexts.identity_access.application.use_cases.users.update_user import UpdateUser
from contexts.identity_access.infrastructure.audit.sqlalchemy_audit_logger import SqlAlchemyAuditLogger
from contexts.identity_access.infrastructure.email.smtp_sender import SmtpEmailSender
from contexts.identity_access.infrastructure.persistence.repositories.permission_repository import (
    SqlAlchemyPermissionRepository,
)
from contexts.identity_access.infrastructure.persistence.repositories.role_repository import (
    SqlAlchemyRoleRepository,
)
from contexts.identity_access.infrastructure.persistence.repositories.user_repository import (
    SqlAlchemyUserRepository,
)
from contexts.identity_access.infrastructure.security.db_authorization_service import DbAuthorizationService
from contexts.identity_access.infrastructure.security.jwt_token_service import JwtTokenService
from contexts.identity_access.infrastructure.security.password_hasher import BcryptPasswordHasher
from contexts.identity_access.infrastructure.security.permission_cache import get_permission_cache
from contexts.identity_access.application.use_cases.permissions.manage_permissions import (
    CreatePermission,
    ListPermissions,
)
from contexts.identity_access.application.use_cases.permissions.set_role_permissions import (
    GetMyPermissions,
    SetRolePermissions,
)
from contexts.identity_access.application.ports.authorization_service import AuthorizationService
from core.configs import settings

_hasher = BcryptPasswordHasher()
_email_sender = SmtpEmailSender()
_token_service = JwtTokenService()


def get_audit_logger(session: Annotated[AsyncSession, Depends(get_session)]) -> SqlAlchemyAuditLogger:
    return SqlAlchemyAuditLogger(session)


def get_token_service() -> JwtTokenService:
    return _token_service


def get_user_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session)


def get_role_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> SqlAlchemyRoleRepository:
    return SqlAlchemyRoleRepository(session)


def get_permission_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SqlAlchemyPermissionRepository:
    return SqlAlchemyPermissionRepository(session)


def get_authorization_service(
    permissions: Annotated[SqlAlchemyPermissionRepository, Depends(get_permission_repository)],
) -> DbAuthorizationService:
    return DbAuthorizationService(permissions, get_permission_cache())


def get_register_user(
    users: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
    audit: Annotated[SqlAlchemyAuditLogger, Depends(get_audit_logger)],
) -> RegisterUser:
    return RegisterUser(users, _hasher, audit, password_min_length=settings.PASSWORD_MIN_LENGTH)


def get_authenticate_user(
    users: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
    audit: Annotated[SqlAlchemyAuditLogger, Depends(get_audit_logger)],
) -> AuthenticateUser:
    return AuthenticateUser(
        users,
        _hasher,
        audit,
        max_failed_attempts=settings.LOGIN_MAX_FAILED_ATTEMPTS,
    )


def get_list_users(
    users: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
    roles: Annotated[SqlAlchemyRoleRepository, Depends(get_role_repository)],
) -> ListUsers:
    return ListUsers(users, roles)


def get_user_by_id(
    users: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
) -> GetUserById:
    return GetUserById(users)


def get_update_user(
    users: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
    audit: Annotated[SqlAlchemyAuditLogger, Depends(get_audit_logger)],
) -> UpdateUser:
    return UpdateUser(users, audit)


def get_deactivate_user(
    users: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
    audit: Annotated[SqlAlchemyAuditLogger, Depends(get_audit_logger)],
) -> DeactivateUser:
    return DeactivateUser(users, audit)


def get_request_password_reset(
    users: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
    audit: Annotated[SqlAlchemyAuditLogger, Depends(get_audit_logger)],
) -> RequestPasswordReset:
    return RequestPasswordReset(
        users,
        _email_sender,
        audit,
        max_requests=settings.PASSWORD_RESET_MAX_REQUESTS,
        window_days=settings.PASSWORD_RESET_WINDOW_DAYS,
    )


def get_reset_password(
    users: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
    audit: Annotated[SqlAlchemyAuditLogger, Depends(get_audit_logger)],
) -> ResetPassword:
    return ResetPassword(users, _hasher, audit, password_min_length=settings.PASSWORD_MIN_LENGTH)


def get_create_role(
    roles: Annotated[SqlAlchemyRoleRepository, Depends(get_role_repository)],
    audit: Annotated[SqlAlchemyAuditLogger, Depends(get_audit_logger)],
) -> CreateRole:
    return CreateRole(roles, audit)


def get_list_roles(
    roles: Annotated[SqlAlchemyRoleRepository, Depends(get_role_repository)],
) -> ListRoles:
    return ListRoles(roles)


def get_role_by_id(
    roles: Annotated[SqlAlchemyRoleRepository, Depends(get_role_repository)],
) -> GetRoleById:
    return GetRoleById(roles)


def get_update_role(
    roles: Annotated[SqlAlchemyRoleRepository, Depends(get_role_repository)],
    audit: Annotated[SqlAlchemyAuditLogger, Depends(get_audit_logger)],
) -> UpdateRole:
    return UpdateRole(roles, audit)


def get_deactivate_role(
    roles: Annotated[SqlAlchemyRoleRepository, Depends(get_role_repository)],
    audit: Annotated[SqlAlchemyAuditLogger, Depends(get_audit_logger)],
) -> DeactivateRole:
    return DeactivateRole(roles, audit)


def get_block_user(
    users: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
    audit: Annotated[SqlAlchemyAuditLogger, Depends(get_audit_logger)],
) -> BlockUser:
    return BlockUser(users, audit)


def get_unblock_user(
    users: Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)],
    audit: Annotated[SqlAlchemyAuditLogger, Depends(get_audit_logger)],
) -> UnblockUser:
    return UnblockUser(users, audit)


def get_list_permissions(
    permissions: Annotated[SqlAlchemyPermissionRepository, Depends(get_permission_repository)],
) -> ListPermissions:
    return ListPermissions(permissions)


def get_create_permission(
    permissions: Annotated[SqlAlchemyPermissionRepository, Depends(get_permission_repository)],
    audit: Annotated[SqlAlchemyAuditLogger, Depends(get_audit_logger)],
) -> CreatePermission:
    return CreatePermission(permissions, audit)


def get_set_role_permissions(
    roles: Annotated[SqlAlchemyRoleRepository, Depends(get_role_repository)],
    permissions: Annotated[SqlAlchemyPermissionRepository, Depends(get_permission_repository)],
    authz: Annotated[DbAuthorizationService, Depends(get_authorization_service)],
    audit: Annotated[SqlAlchemyAuditLogger, Depends(get_audit_logger)],
) -> SetRolePermissions:
    return SetRolePermissions(roles, permissions, authz, audit)


def get_my_permissions(
    authz: Annotated[DbAuthorizationService, Depends(get_authorization_service)],
) -> GetMyPermissions:
    return GetMyPermissions(authz)
