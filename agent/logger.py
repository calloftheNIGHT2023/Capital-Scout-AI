import logging
import os


def setup_logger(log_path: str) -> logging.Logger:
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logger = logging.getLogger("capital_scout")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger
