import logging
import os
import sys
from datetime import datetime

from loguru import logger


class InterceptHandler(logging.Handler):
    """拦截标准库 logging 日志，转发到 loguru"""

    def emit(self, record: logging.LogRecord) -> None:
        # 获取对应的 Loguru 级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 找到调用者的位置
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logger(
    log_dir: str = "logs",
    log_level: str = "DEBUG",
    rotation: str = "1 week",
    retention: str = "30  days",
):
    """配置 Loguru 日志，輸出到文件与控制台

    使用 delay=True 参数实现按需创建日志文件：
    - 日志文件只在实际写入日志时才会被创建
    - 如果没有对应级别的日志产生，对应的日志文件不会被创建
    """

    # 延迟创建日志目录
    os.makedirs(log_dir, exist_ok=True)

    current_date = datetime.today().strftime("%Y-%m-%d")

    # 重置默認輸出配置
    logger.remove()

    # delay=True: 延迟创建文件，只在第一次写入时才创建
    # filter: 过滤器确保每个文件只记录特定级别的日志
    logger.add(
        os.path.join(log_dir, f"debug_{current_date}.log"),
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation=rotation,
        retention=retention,
        compression="zip",
        delay=True,
        filter=lambda record: record["level"].name == "DEBUG",
    )
    logger.add(
        os.path.join(log_dir, f"info_{current_date}.log"),
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation=rotation,
        retention=retention,
        compression="zip",
        delay=True,
        filter=lambda record: record["level"].name == "INFO",
    )
    logger.add(
        os.path.join(log_dir, f"warning_{current_date}.log"),
        level="WARNING",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation=rotation,
        retention=retention,
        compression="zip",
        delay=True,
        filter=lambda record: record["level"].name == "WARNING",
    )
    logger.add(
        os.path.join(log_dir, f"error_{current_date}.log"),
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation=rotation,
        retention=retention,
        compression="zip",
        delay=True,
        filter=lambda record: record["level"].name == "ERROR",
    )
    # 控制台输出，带自定义颜色
    logger.add(
        sys.stdout,
        level=log_level,
        format=custom_format,
        colorize=True,
    )

    # 拦截 uvicorn、fastapi 等使用标准库 logging 的日志
    _setup_intercept(log_level)


def custom_format(record):
    """自定义日志级别颜色"""
    level_colors = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
    }
    level_name = record["level"].name
    color = level_colors.get(level_name, "white")
    return f"<cyan>{{time:YYYY-MM-DD HH:mm:ss}}</cyan> | <{color}>{{level: <8}}</{color}> | <{color}>{{message}}</{color}>\n"


def _setup_intercept(log_level: str = "DEBUG"):
    """设置日志拦截，将标准库 logging 转发到 loguru"""
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(log_level)

    # 拦截所有已存在的 logger（包括 uvicorn）
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # 禁用 watchfiles 的日志，避免监控日志文件导致无限循环
    logging.getLogger("watchfiles").setLevel(logging.WARNING)
    logging.getLogger("watchfiles.main").setLevel(logging.WARNING)


# 初始化日志配置
setup_logger()


def log_debug(message: str):
    logger.debug(message)


def log_info(message: str):
    logger.info(message)


def log_warning(message: str):
    logger.warning(message)


def log_error(message: str):
    logger.error(message)
