from enum import IntEnum

_ROLE_LABELS: dict[int, str] = {
    1: "Usuario",
    2: "Operador",
    3: "Administrador",
    4: "Usuario_cliente",
}


class RoleType(IntEnum):
    """Papéis de usuário no domínio Identity & Access."""

    USER = 1
    OPERATOR = 2
    ADMINISTRATOR = 3
    USER_CLIENT = 4

    def label(self) -> str:
        return _ROLE_LABELS.get(self.value, "Role inválida")

    @classmethod
    def label_for(cls, role_id: int | None) -> str:
        if role_id is None:
            return "Role inválida"
        try:
            return cls(role_id).label()
        except ValueError:
            return "Role inválida"
