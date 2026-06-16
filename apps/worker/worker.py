from taskiq.cli.worker.args import WorkerArgs
from taskiq.cli.worker.run import run_worker

from src.core.logging import configure_logging, get_logger
from src.infrastructure.observability.otel_runtime import configure_observability_runtime

logger = get_logger(__name__)


def main() -> int | None:
    configure_logging()
    configure_observability_runtime(runtime="worker")
    logger.info("Hello Wiki Worker is initializing...")
    args = WorkerArgs(
        broker="hello_wiki_worker.broker:broker",
        modules=["hello_wiki_worker.tasks"],
    )
    logger.info("Worker is ready. Listening for tasks...")
    try:
        return run_worker(args)
    except KeyboardInterrupt:
        logger.info("Worker stopped by user.")
        return 0
    except Exception as exc:
        logger.exception("Worker crashed: %s", exc)
        return 1


if __name__ == "__main__":
    status = main()
    if isinstance(status, int):
        raise SystemExit(status)
