import uvicorn
from src.core.config import settings
from src.core.logging import configure_logging, get_logger

logger = get_logger(__name__)

def main():
    """本地开发环境启动入口"""
    configure_logging()
    logger.info("Starting %s in %s mode...", settings.PROJECT_NAME, "DEBUG" if settings.DEBUG else "PROD")
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG, # 只有开发模式下热重载
        workers=1 if settings.DEBUG else settings.WORKERS_COUNT,
        log_config=None,
    )

if __name__ == "__main__":
    main()