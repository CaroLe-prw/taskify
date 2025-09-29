import os
import sys
from datetime import datetime

from loguru import logger


def setup_logger(log_dir: str = "logs", log_level: str = "DEBUG", rotation: str = "1 week", retention: str = "30  days"):
    """配置 Loguru 日誌，輸出到文件與控制台"""

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    current_date = datetime.today().strftime("%Y-%m-%d")

    # 重置默認輸出配置
    logger.remove()

    logger.add(
        os.path.join(log_dir, f"debug_{current_date}.log"),
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation=rotation,
        retention=retention,
        compression="zip",
    )
    logger.add(
        os.path.join(log_dir, f"info_{current_date}.log"),
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation=rotation,
        retention=retention,
        compression="zip",
    )
    logger.add(
        os.path.join(log_dir, f"warning_{current_date}.log"),
        level="WARNING",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation=rotation,
        retention=retention,
        compression="zip",
    )
    logger.add(
        os.path.join(log_dir, f"error_{current_date}.log"),
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation=rotation,
        retention=retention,
        compression="zip",
    )

    logger.add(
        sys.stdout,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        colorize=True,
    )


setup_logger()


def log_debug(message: str):
    logger.debug(message)


def log_info(message: str):
    logger.info(message)


def log_warning(message: str):
    logger.warning(message)


def log_error(message: str):
    logger.error(message)
