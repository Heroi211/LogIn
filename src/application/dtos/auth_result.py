from __future__ import annotations

from dataclasses import dataclass

from schemas.auth_schemas import TokenResponse


@dataclass
class AuthResult:
    token_response: TokenResponse
    session_token: str
