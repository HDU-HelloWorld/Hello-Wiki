from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class TaskType(StrEnum):
    SEMANTIC_DEDUP = "SEMANTIC_DEDUP"
    STALENESS_AUDIT = "STALENESS_AUDIT"
    LINK_VALIDATION = "LINK_VALIDATION"
    FACT_CONSOLIDATION = "FACT_CONSOLIDATION"


class TaskStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING_REVIEW = "WAITING_REVIEW"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class MaintenanceAction(StrEnum):
    MERGE_PAGES = "MERGE_PAGES"
    FLAG_OBSOLETE = "FLAG_OBSOLETE"
    REPAIR_LINK = "REPAIR_LINK"
    CONSOLIDATE_FACTS = "CONSOLIDATE_FACTS"


@dataclass
class MaintenanceLog:
    log_id: UUID
    task_id: UUID
    action: MaintenanceAction
    details: str
    created_at: datetime

    @staticmethod
    def create(task_id: UUID, action: MaintenanceAction, details: str) -> "MaintenanceLog":
        return MaintenanceLog(
            log_id=uuid4(),
            task_id=task_id,
            action=action,
            details=details,
            created_at=datetime.now(UTC),
        )


@dataclass
class MaintenanceTask:
    task_id: UUID
    workspace_id: UUID
    task_type: TaskType
    scheduled_at: datetime
    report_summary: dict[str, object] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    logs: list[MaintenanceLog] = field(default_factory=list)

    @staticmethod
    def create(
        workspace_id: UUID,
        task_type: TaskType,
        scheduled_at: datetime | None = None,
    ) -> "MaintenanceTask":
        return MaintenanceTask(
            task_id=uuid4(),
            workspace_id=workspace_id,
            task_type=task_type,
            scheduled_at=scheduled_at or datetime.now(UTC),
        )

    def start(self) -> None:
        self.status = TaskStatus.RUNNING

    def mark_waiting_review(self) -> None:
        self.status = TaskStatus.WAITING_REVIEW

    def complete(self, report_summary: dict[str, object] | None = None) -> None:
        self.status = TaskStatus.COMPLETED
        if report_summary is not None:
            self.report_summary = report_summary

    def fail(self, details: str) -> None:
        self.status = TaskStatus.FAILED
        self.logs.append(
            MaintenanceLog.create(
                task_id=self.task_id,
                action=MaintenanceAction.FLAG_OBSOLETE,
                details=details,
            )
        )
