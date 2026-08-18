from core.security import get_password_hash, verify_password
from contexts.identity_access.application.ports.password_hasher import PasswordHasher


class BcryptPasswordHasher:
    def hash(self, password: str) -> str:
        return get_password_hash(password)

    def verify(self, plain: str, hashed: str) -> bool:
        return verify_password(plain, hashed)
