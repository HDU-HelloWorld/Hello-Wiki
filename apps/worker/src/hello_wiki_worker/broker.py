from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from src.core.config import settings

from hello_wiki_worker.context_middleware import ExecutionContextMiddleware

broker = ListQueueBroker(settings.REDIS_URL).with_result_backend(
    RedisAsyncResultBackend(settings.REDIS_URL)
)

broker.add_middlewares(ExecutionContextMiddleware())
