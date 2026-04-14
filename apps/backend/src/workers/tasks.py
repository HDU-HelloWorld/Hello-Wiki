from dataclasses import dataclass
from typing import Callable

from application.orchestration import ApplicationOrchestrator


@dataclass(frozen=True)
class CompileTaskPayload:
    source_uri: str


@dataclass(frozen=True)
class QATaskPayload:
    question: str


@dataclass(frozen=True)
class WikiListTaskPayload:
    workspace_id: str


def _parse_compile_payload(payload: dict[str, object]) -> CompileTaskPayload:
    source_uri = payload.get("source_uri", "")
    return CompileTaskPayload(source_uri=str(source_uri))


def _parse_qa_payload(payload: dict[str, object]) -> QATaskPayload:
    question = payload.get("question", "")
    return QATaskPayload(question=str(question))


def _parse_wiki_payload(payload: dict[str, object]) -> WikiListTaskPayload:
    workspace_id = payload.get("workspace_id", "default")
    return WikiListTaskPayload(workspace_id=str(workspace_id))


def register_tasks(
    orchestrator: ApplicationOrchestrator,
) -> dict[str, Callable[[dict[str, object]], object]]:
    """Register worker handlers that only parse payload and orchestrate use-cases."""

    def handle_compile(payload: dict[str, object]) -> object:
        parsed = _parse_compile_payload(payload)
        return orchestrator.compile_document(source_uri=parsed.source_uri)

    def handle_qa(payload: dict[str, object]) -> object:
        parsed = _parse_qa_payload(payload)
        return orchestrator.ask(question=parsed.question)

    def handle_wiki_list(payload: dict[str, object]) -> object:
        parsed = _parse_wiki_payload(payload)
        return orchestrator.list_pages(workspace_id=parsed.workspace_id)

    return {
        "compile.document": handle_compile,
        "qa.ask": handle_qa,
        "wiki.list": handle_wiki_list,
    }
