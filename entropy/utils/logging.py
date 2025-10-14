import os
from datetime import datetime
from pathlib import Path
from loguru import logger

def set_run_dir():
    run_id = os.getenv("RUN_ID", datetime.now().strftime("%Y%m%d_%H%M%S"))
    run_dir = Path(os.getenv("LOGS_PATH")) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_id, run_dir

def configure_logging(script_name: str, console_level = "INFO") -> Path:
    """Configure loguru for scripts (both console and file)."""
    _, run_dir = set_run_dir()

    log_path = run_dir / f"{script_name}.log"
    logger.remove()

    if console_level is not None:
        logger.add(os.sys.stderr, level=console_level, format="<level>{level: <8}</level> | <level>{message}</level>")
    logger.add(log_path, level="DEBUG", rotation="10 MB")

    return log_path


def configure_cli_logging(script_name: str = "cli_session") -> Path:
    """Configure loguru for CLI (file only, no console spam)."""
    return configure_logging(script_name, console_level=None)