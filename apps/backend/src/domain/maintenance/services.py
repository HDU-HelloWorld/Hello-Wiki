from typing import Protocol
from uuid import UUID

from src.domain.maintenance.entities import MaintenanceTask, TaskType


class MaintenanceRepository(Protocol):
    def upsert(self, task: MaintenanceTask) -> None: ...

    def get_by_id(self, task_id: UUID) -> MaintenanceTask | None: ...

    def list_by_workspace(self, workspace_id: UUID) -> list[MaintenanceTask]: ...

    def list_by_type(self, task_type: TaskType) -> list[MaintenanceTask]: ...


class MaintenancePlanner(Protocol):
    def plan(self, workspace_id: UUID, task_type: TaskType) -> MaintenanceTask: ...
