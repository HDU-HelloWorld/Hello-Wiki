# src/workers/broker.py
import taskiq_redis

from src.core.config import settings
from src.workers.context_middleware import ExecutionContextMiddleware

# 使用 Redis 作为任务队列
broker = taskiq_redis.ListQueueBroker(settings.REDIS_URL).with_result_backend(
    taskiq_redis.RedisAsyncResultBackend(settings.REDIS_URL)
)

broker.add_middlewares(ExecutionContextMiddleware())
