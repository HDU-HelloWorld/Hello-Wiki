import sys

from taskiq.cli.worker.args import WorkerArgs
from taskiq.cli.worker.run import run_worker

from src.core.logging import configure_logging, get_logger
from src.infrastructure.observability.otel_runtime import configure_observability_runtime

logger = get_logger(__name__)

def main() -> int | None:
    """启动 TaskIQ Worker 进程"""
    configure_logging()
    configure_observability_runtime(runtime="worker")
    logger.info("ZhiYuan Worker is initializing...")

    args = WorkerArgs(
        broker="src.workers.broker:broker",
        modules=["src.workers.tasks"],
    )
    logger.info("Worker is ready. Listening for tasks...")

    try:
        return run_worker(args)
    except KeyboardInterrupt:
        logger.info("Worker stopped by user.")
        return 0
    except Exception as e:
        logger.exception("Worker crashed: %s", e)
        return 1

if __name__ == "__main__":
    # # 解决 Windows 下可能出现的事件循环问题
    # if sys.platform == 'win32':
    #     # 仅保留兼容提示，实际事件循环由 taskiq worker 管理。
    #     pass

    try:
        status = main()
        if isinstance(status, int):
            raise SystemExit(status)
    except KeyboardInterrupt:
        pass