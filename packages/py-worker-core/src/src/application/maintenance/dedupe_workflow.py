from dataclasses import dataclass, field
from uuid import UUID

from src.core.observability import (
    ObservabilityContext,
    annotate_current_span,
    start_observability_span,
)
from src.domain.maintenance.entities import (
    MaintenanceAction,
    MaintenanceLog,
    MaintenanceTask,
    TaskType,
)
from src.domain.wiki.entities import WikiPage
from src.domain.wiki.repository import WikiQueryRepositoryPort
from src.domain.wiki.services import WikiSearchEngine


@dataclass(frozen=True)
class RunDedupeWorkflowCommand:
    workspace_id: UUID
    min_similarity_score: float = 0.8
    max_candidates: int = 10


@dataclass(frozen=True)
class DedupeCandidate:
    primary_title: str
    duplicate_title: str
    score: float
    reason: str


@dataclass(frozen=True)
class DedupeWorkflowResult:
    task: MaintenanceTask
    candidates: list[DedupeCandidate] = field(default_factory=list)


class DedupeWorkflow:
    """基于标题与内容相似度生成知识库去重任务。"""

    def __init__(
        self,
        repository: WikiQueryRepositoryPort,
        search_engine: WikiSearchEngine,
    ) -> None:
        self._repository = repository
        self._search_engine = search_engine

    async def execute(self, command: RunDedupeWorkflowCommand) -> DedupeWorkflowResult:
        with start_observability_span(
            "llamaindex.workflow",
            "dedupe.execute",
            workspace_id=command.workspace_id,
            workflow_name="dedupe",
            workflow_kind="maintenance",
        ):
            # 去重业务策略留空，先保留任务骨架，供后续团队补齐。
            task = MaintenanceTask.create(command.workspace_id, TaskType.SEMANTIC_DEDUP)
            task.report_summary = {
                "note": "placeholder workflow",
                "min_similarity_score": command.min_similarity_score,
                "task_type": task.task_type.value,
            }
            task.logs.append(
                MaintenanceLog.create(
                    task_id=task.task_id,
                    action=MaintenanceAction.MERGE_PAGES,
                    details="dedupe workflow placeholder; business logic pending",
                )
            )
            annotate_current_span(
                ObservabilityContext(
                    trace_id=None,
                    workspace_id=command.workspace_id,
                    runtime="worker",
                    component="llamaindex.workflow",
                    operation="dedupe.execute",
                    workflow_name="dedupe",
                    workflow_kind="maintenance",
                ),
                {
                    "llamaindex.workflow.candidate_count": 0,
                    "llamaindex.workflow.task_id": str(task.task_id),
                },
            )

            return DedupeWorkflowResult(task=task, candidates=[])

    def _find_candidates(
        self,
        pages: list[WikiPage],
        min_similarity_score: float,
        max_candidates: int,
    ) -> list[DedupeCandidate]:
        return []

    @staticmethod
    def _score_pair(primary: WikiPage, duplicate: WikiPage) -> float:
        return 0.0

    @staticmethod
    def _build_reason(primary: WikiPage, duplicate: WikiPage) -> str:
        return "placeholder reason"
