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
