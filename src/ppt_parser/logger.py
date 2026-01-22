import logging
from logging.handlers import RotatingFileHandler

def setup_logger(
    name: str = "ppt_parser",
    log_file: str = "app.log",
    level=logging.INFO,
):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s"
    )

    # 콘솔 로그
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 파일 로그 (5MB x 5개)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
