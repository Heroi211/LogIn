from __future__ import annotations

from domain.entities.user import ApiKeyEntity, SessionEntity, UserEntity
from models.api_keys import ApiKeys
from models.sessions import Sessions
from models.users import Users


def user_to_entity(user: Users) -> UserEntity:
    return UserEntity(
        id=user.id,
        name=user.name,
        email=user.email,
        phone=user.phone,
        role_id=user.role_id,
        active=user.active,
        auth_provider=getattr(user, "auth_provider", "local") or "local",
        cpf=user.cpf,
        password_hash=user.password,
        google_id=getattr(user, "google_id", None),
        failed_login_attempts=getattr(user, "failed_login_attempts", 0) or 0,
        reset_password_token=user.reset_password_token,
        reset_password_expires=user.reset_password_expires,
        created_at=user.created_at,
    )


def user_from_entity(entity: UserEntity) -> Users:
    user = Users(
        name=entity.name,
        email=entity.email,
        phone=entity.phone,
        cpf=entity.cpf or f"oauth_{entity.google_id or entity.id}",
        role_id=entity.role_id,
    )
    user.id = entity.id
    user.password = entity.password_hash
    user.active = entity.active
    user.auth_provider = entity.auth_provider
    user.google_id = entity.google_id
    user.created_at = entity.created_at
    user.reset_password_token = None
    user.reset_password_expires = None
    return user


def entity_to_orm(entity: UserEntity) -> Users:
    return user_from_entity(entity)


def session_to_entity(record: Sessions) -> SessionEntity:
    return SessionEntity(
        id=record.id,
        user_id=record.user_id,
        token_hash=record.token_hash,
        expires_at=record.expires_at,
        active=record.active,
        ip_address=record.ip_address,
        user_agent=record.user_agent,
        created_at=record.created_at,
    )


def api_key_to_entity(record: ApiKeys) -> ApiKeyEntity:
    return ApiKeyEntity(
        id=record.id,
        key_prefix=record.key_prefix,
        key_hash=record.key_hash,
        name=record.name,
        user_id=record.user_id,
        scopes=record.scopes,
        active=record.active,
        expires_at=record.expires_at,
        created_at=record.created_at,
    )


def role_display(role_id: int) -> str:
    """Alias de session_service.role_label — único ponto para label de role."""
    from services.session_service import role_label

    return role_label(role_id)
