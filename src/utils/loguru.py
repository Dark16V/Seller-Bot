from loguru import logger
import sys
import logging
from pathlib import Path


class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())



def setup_logger(level: str = "INFO"):
    logger.remove()

    logger.add(
        sink=sys.stdout,
        level=level,
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level}</level> | <magenta>{message}</magenta>"
    )

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Общий лог-файл
    logger.add(
        sink=str(log_dir / "log.log"),
        level="DEBUG",
        enqueue=True,
        backtrace=True,
        diagnose=True,
        format="{time:MM-DD HH:mm} | {level} | {message}"
    )

    logger.add(
        sink=str(log_dir / "error.log"),
        level="ERROR", 
        enqueue=True,
        backtrace=True,
        diagnose=True,
        format="{time:MM-DD HH:mm} | {level} | {message}"
    )

    # Интеграция с обычным логгером Python
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.getLevelName(level))
    logger.success("Logger succ started!")
