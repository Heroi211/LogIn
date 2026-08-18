from contexts.identity_access.domain.exceptions import WeakPasswordError


def validate_password(password: str, *, min_length: int) -> None:
    if len(password) < min_length:
        raise WeakPasswordError(f"A senha deve ter no mínimo {min_length} caracteres.")
