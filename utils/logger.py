import logging

INFO = logging.INFO
DEBUG = logging.DEBUG


def setup_logger(
    logger_name: str, log_file: str = "log.log", level: int = logging.INFO
):
    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(file_handler)

    return logger
