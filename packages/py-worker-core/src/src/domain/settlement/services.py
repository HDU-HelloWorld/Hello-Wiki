from typing import Protocol
from uuid import UUID

from src.domain.settlement.entities import SettledKnowledge


class SettlementRepository(Protocol):
    def upsert(self, item: SettledKnowledge) -> None: ...

    def get_by_id(self, settled_id: UUID) -> SettledKnowledge | None: ...

    def list_by_workspace(self, workspace_id: UUID) -> list[SettledKnowledge]: ...


class SettlementPolicy(Protocol):
    def should_settle(self, question_pattern: str, authority_weight: float) -> bool: ...
