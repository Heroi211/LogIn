from domain.entities.user import UserEntity
from models.roles import Roles
from models.users import Users
from schemas.auth_schemas import UserSession


def role_label(role_id: int) -> str:
    for code, label in Roles.ROLES:
        if code == role_id:
            return label
    return "Desconhecido"


def build_user_session(user: Users | UserEntity) -> UserSession:
    return UserSession(
        id=user.id,
        name=user.name,
        email=user.email,
        cpf=user.cpf or "",
        phone=user.phone,
        role_id=user.role_id,
        role=role_label(user.role_id),
        active=user.active,
        auth_provider=getattr(user, "auth_provider", "local") or "local",
    )
