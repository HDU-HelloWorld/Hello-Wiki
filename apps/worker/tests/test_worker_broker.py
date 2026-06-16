from __future__ import annotations

from hello_wiki_worker.broker import broker
from hello_wiki_worker.context_middleware import ExecutionContextMiddleware


def test_worker_broker_uses_redis_backends():
    assert broker is not None
    assert broker.result_backend is not None


def test_worker_broker_registers_execution_context_middleware():
    middleware_types = [type(middleware) for middleware in broker.middlewares]

    assert ExecutionContextMiddleware in middleware_types
