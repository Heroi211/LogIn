"""Testes unitários — security."""

import pytest

from core.security import get_password_hash, verify_password


@pytest.mark.unit
def test_password_hash_and_verify():
    hashed = get_password_hash("senha-segura-123")
    assert hashed != "senha-segura-123"
    assert verify_password("senha-segura-123", hashed)
    assert not verify_password("outra-senha", hashed)
