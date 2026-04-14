from __future__ import annotations

from fastapi import FastAPI

import src.main as main_module


class _FakeBroker:
    def __init__(self) -> None:
        self.is_worker_process = False
        self.startup_calls = 0
        self.shutdown_calls = 0

    async def startup(self) -> None:
        self.startup_calls += 1

    async def shutdown(self) -> None:
        self.shutdown_calls += 1


def test_create_app_wires_gateway_router_and_observability(monkeypatch):
    calls: list[tuple[str, object]] = []
    fake_app = FastAPI()

    def fake_configure_logging():
        calls.append(("logging", None))

    def fake_register_gateway_middleware(app):
        calls.append(("gateway", app))

    def fake_configure_observability_runtime(*, app=None, runtime="api"):
        calls.append(("observability", (app, runtime)))

    monkeypatch.setattr(main_module, "configure_logging", fake_configure_logging)
    monkeypatch.setattr(
        main_module, "register_gateway_middleware", fake_register_gateway_middleware
    )
    monkeypatch.setattr(
        main_module, "configure_observability_runtime", fake_configure_observability_runtime
    )
    monkeypatch.setattr(main_module, "FastAPI", lambda **kwargs: fake_app)

    app = main_module.create_app()

    assert app is fake_app
    assert calls[0][0] == "logging"
    assert calls[1][0] == "gateway"
    assert calls[1][1] is fake_app
    assert calls[2][0] == "observability"
    assert calls[2][1] == (fake_app, "api")
    assert "/health" in {route.path for route in app.routes}


def test_lifespan_starts_and_stops_broker_when_not_worker(monkeypatch):
    fake_broker = _FakeBroker()
    calls: list[str] = []

    def fake_configure_logging():
        calls.append("logging")

    monkeypatch.setattr(main_module, "configure_logging", fake_configure_logging)
    monkeypatch.setattr(main_module, "_get_broker", lambda: fake_broker)

    app = FastAPI()
    lifespan_cm = main_module.lifespan(app)

    async def _run():
        async with lifespan_cm:
            calls.append("inside")

    import asyncio

    asyncio.run(_run())

    assert calls == ["logging", "inside"]
    assert fake_broker.startup_calls == 1
    assert fake_broker.shutdown_calls == 1


def test_lifespan_skips_broker_for_worker_process(monkeypatch):
    fake_broker = _FakeBroker()
    fake_broker.is_worker_process = True
    calls: list[str] = []

    def fake_configure_logging():
        calls.append("logging")

    monkeypatch.setattr(main_module, "configure_logging", fake_configure_logging)
    monkeypatch.setattr(main_module, "_get_broker", lambda: fake_broker)

    app = FastAPI()
    lifespan_cm = main_module.lifespan(app)

    async def _run():
        async with lifespan_cm:
            calls.append("inside")

    import asyncio

    asyncio.run(_run())

    assert calls == ["logging", "inside"]
    assert fake_broker.startup_calls == 0
    assert fake_broker.shutdown_calls == 0
