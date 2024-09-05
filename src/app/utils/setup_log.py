import os

from loguru import logger

from src.app.core.config import settings


def init_log():

    # 日志文件
    log_info_file = os.path.join(settings.log_path, "app.log")
    log_error_file = os.path.join(settings.log_path, "app_error.log")

    # 日志参数链接 https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.add
    # loguru 不建议自己实例化 logger，而是使用默认的 logger
    logger.add(
        log_info_file,
        level="INFO",
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        enqueue=settings.log_enqueue,
        backtrace=settings.log_backtrace,
        diagnose=settings.log_diagnose,
    )
    logger.add(
        log_error_file,
        level="ERROR",
        rotation=settings.log_rotation,
        retention=settings.log_retention,
        enqueue=settings.log_enqueue,
        backtrace=settings.log_backtrace,
        diagnose=settings.log_diagnose,
    )
