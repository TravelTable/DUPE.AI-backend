from loguru import logger
import sys
import os

def setup_logging(level: str = "INFO"):
    logger.remove()
    logger.add(sys.stdout, level=level, backtrace=False, diagnose=False,
               format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
                      "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    # Reduce noisy libs
    for noisy in ["uvicorn", "uvicorn.access", "httpx", "asyncio"]:
        logger.disable(noisy)
