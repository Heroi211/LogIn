"""Testes unitários — JWT e tokens."""

import pytest

from core.auth import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    create_token_response,
    decode_refresh_token,
    decode_token_payload,
)
from domain.entities.user import UserEntity


def _sample_user() -> UserEntity:
    return UserEntity(
        id=1,
        name="Operador Dev",
        email="operador@example.com",
        phone="11999990001",
        role_id=1,
        active=True,
        cpf="11111111111",
    )


@pytest.mark.unit
def test_create_token_response_contains_jti():
    tokens = create_token_response(_sample_user())
    access_payload = decode_token_payload(tokens.access_token)
    refresh_payload = decode_token_payload(tokens.refresh_token)

    assert access_payload["type"] == ACCESS_TOKEN_TYPE
    assert refresh_payload["type"] == REFRESH_TOKEN_TYPE
    assert access_payload["jti"]
    assert refresh_payload["jti"]
    assert access_payload["sub"] == "1"


@pytest.mark.unit
def test_decode_refresh_token_returns_payload():
    tokens = create_token_response(_sample_user())
    payload = decode_refresh_token(tokens.refresh_token)
    assert payload["sub"] == "1"
    assert payload["type"] == REFRESH_TOKEN_TYPE
