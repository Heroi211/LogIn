class AuditAction:
    """Vocabulário de eventos de auditoria do contexto Identity & Access."""

    AUTH_LOGIN_SUCCESS = "auth.login.success"
    AUTH_LOGIN_FAILED = "auth.login.failed"
    AUTH_PASSWORD_RESET_REQUESTED = "auth.password.reset.requested"
    AUTH_PASSWORD_RESET_COMPLETED = "auth.password.reset.completed"

    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DEACTIVATED = "user.deactivated"
    USER_BLOCKED = "user.blocked"
    USER_UNBLOCKED = "user.unblocked"
    USER_AUTO_BLOCKED = "user.auto_blocked"

    ROLE_CREATED = "role.created"
    ROLE_UPDATED = "role.updated"
    ROLE_DEACTIVATED = "role.deactivated"
    ROLE_PERMISSIONS_UPDATED = "role.permissions.updated"

    PERMISSION_CREATED = "permission.created"

    AUTHZ_DENIED = "authz.denied"
