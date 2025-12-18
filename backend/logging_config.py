import logging
import os

import psutil
from colorlog import ColoredFormatter

from .config import settings

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

for handler in root_logger.handlers:
    root_logger.removeHandler(handler)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

formatter = ColoredFormatter(
    "%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)
handler.setFormatter(formatter)
root_logger.addHandler(handler)

logger = logging.getLogger("rails_superhero_cards")
logger.setLevel(settings.log_level)

logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)
logging.getLogger("llama_index_instrumentation").setLevel(logging.WARNING)


def log_memory_usage(label: str = "") -> None:
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    logger.info(
        f"Memory [{label}] - RSS: {mem_info.rss / 1024 / 1024:.2f}MB, "
        f"VMS: {mem_info.vms / 1024 / 1024:.2f}MB, "
        f"Percent: {process.memory_percent():.1f}%"
    )
