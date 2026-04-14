# -*- coding: utf-8 -*-
# 编码修复: __init__.py - 已替换Unicode符号避免Windows编码问题
"""Core module for shared runtime concerns."""

from core.audit import AuditEvent, AuditRecorder, NoopAuditRecorder
from core.auth import AuthPrincipal, Authenticator, ScaffoldAuthenticator
from core.context import RequestContext, get_request_context, set_request_context

__all__ = [
    "AuditEvent",
    "AuditRecorder",
    "NoopAuditRecorder",
    "AuthPrincipal",
    "Authenticator",
    "ScaffoldAuthenticator",
    "RequestContext",
    "get_request_context",
    "set_request_context",
]
