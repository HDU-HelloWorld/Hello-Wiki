# -*- coding: utf-8 -*-
# 编码修复: auth.py - 已替换Unicode符号避免Windows编码问题
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AuthPrincipal:
    principal_id: str
    roles: tuple[str, ...]


class Authenticator(Protocol):
    def authenticate(self, token: str | None) -> AuthPrincipal: ...


class ScaffoldAuthenticator(Authenticator):
    def authenticate(self, token: str | None) -> AuthPrincipal:
        _ = token
        return AuthPrincipal(principal_id="anonymous", roles=("reader",))
