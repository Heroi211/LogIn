from passlib.context import CryptContext

CRYPT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(password: str, hash_password: str) -> bool:
    return CRYPT.verify(password, hash_password)


def get_password_hash(password: str) -> str:
    return CRYPT.hash(password)
