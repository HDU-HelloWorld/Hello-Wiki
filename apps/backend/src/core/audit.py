# -*- coding: utf-8 -*-
# 编码修复: audit.py - 已替换Unicode符号避免Windows编码问题
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AuditEvent:
    action: str
    actor_id: str
    workspace_id: str
    request_id: str


class AuditRecorder(Protocol):
    def record(self, event: AuditEvent) -> None: ...


class NoopAuditRecorder(AuditRecorder):
    def record(self, event: AuditEvent) -> None:
        _ = event
