from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class SettlementStatus(StrEnum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    EXPIRED = "EXPIRED"


class SettlementAuditAction(StrEnum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    HIT = "HIT"
    EXPIRED = "EXPIRED"


@dataclass
class CaseSimilarity:
    question_pattern: str
    source_message_id: str
    score: float


@dataclass
class SettlementAuditLog:
    log_id: UUID
    settled_id: UUID
    action: SettlementAuditAction
    details: str
    created_at: datetime

    @staticmethod
    def create(
        settled_id: UUID, action: SettlementAuditAction, details: str
    ) -> "SettlementAuditLog":
        return SettlementAuditLog(
            log_id=uuid4(),
            settled_id=settled_id,
            action=action,
            details=details,
            created_at=datetime.now(UTC),
        )


@dataclass
class SettledKnowledge:
    settled_id: UUID
    workspace_id: UUID
    origin_message_id: str
    query_pattern: str
    authority_weight: float
    hit_count: int = 0
    last_hit_at: datetime | None = None
    expires_at: datetime | None = None
    status: SettlementStatus = SettlementStatus.ACTIVE
    similarities: list[CaseSimilarity] = field(default_factory=list)
    audit_logs: list[SettlementAuditLog] = field(default_factory=list)

    @staticmethod
    def create(
        workspace_id: UUID,
        origin_message_id: str,
        query_pattern: str,
        authority_weight: float,
        expires_at: datetime | None = None,
    ) -> "SettledKnowledge":
        return SettledKnowledge(
            settled_id=uuid4(),
            workspace_id=workspace_id,
            origin_message_id=origin_message_id,
            query_pattern=query_pattern,
            authority_weight=authority_weight,
            expires_at=expires_at,
        )

    def record_hit(self) -> None:
        self.hit_count += 1
        self.last_hit_at = datetime.now(UTC)
        self.audit_logs.append(
            SettlementAuditLog.create(
                settled_id=self.settled_id,
                action=SettlementAuditAction.HIT,
                details="settlement hit recorded",
            )
        )

    def add_similarity(self, similarity: CaseSimilarity) -> None:
        self.similarities.append(similarity)

    def archive(self) -> None:
        self.status = SettlementStatus.ARCHIVED
        self.audit_logs.append(
            SettlementAuditLog.create(
                settled_id=self.settled_id,
                action=SettlementAuditAction.UPDATED,
                details="settlement archived",
            )
        )
