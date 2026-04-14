#!/usr/bin/env python3
from __future__ import annotations

import argparse
from uuid import UUID

import uvicorn
from src.core.config import settings
from src.core.logging import configure_logging, get_logger
from src.main import app as backend_app

logger = get_logger(__name__)
DEFAULT_WORKSPACE_ID = UUID("00000000-0000-0000-0000-000000000001")


class DefaultWorkspaceHeaderMiddleware:
    def __init__(self, app, workspace_id: UUID) -> None:
        self.app = app
        self.workspace_id = workspace_id

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = list(scope.get("headers", []))
            header_name = b"x-workspace-id"
            has_header = any(name.lower() == header_name for name, _ in headers)
            if not has_header:
                headers.append((header_name, str(self.workspace_id).encode("utf-8")))
                scope = dict(scope)
                scope["headers"] = headers
        await self.app(scope, receive, send)


def _parse_workspace_id(value: str) -> UUID:
    try:
        return UUID(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"invalid workspace id: {value}") from error


def build_app(workspace_id: UUID) -> DefaultWorkspaceHeaderMiddleware:
    return DefaultWorkspaceHeaderMiddleware(backend_app, workspace_id)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="MVP 本地开发启动器：为缺省请求自动注入统一默认租户。"
    )
    parser.add_argument(
        "--workspace-id",
        type=_parse_workspace_id,
        default=DEFAULT_WORKSPACE_ID,
        help=f"默认租户 ID，默认值为 {DEFAULT_WORKSPACE_ID}",
    )
    parser.add_argument("--host", default=settings.HOST, help="监听地址")
    parser.add_argument("--port", type=int, default=settings.PORT, help="监听端口")
    args = parser.parse_args()

    configure_logging()
    logger.info("Starting MVP wrapper with default workspace id: %s", args.workspace_id)
    uvicorn.run(
        build_app(args.workspace_id),
        host=args.host,
        port=args.port,
        log_config=None,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
