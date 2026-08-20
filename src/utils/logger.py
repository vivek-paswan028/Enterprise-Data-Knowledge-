import sys
from pathlib import Path
from loguru import logger
from src.config.settings import settings

def setup_logger() -> None:
    """
    Configures Loguru enterprise logging framework.
    Provides structured console logs for development and JSON logs for production aggregators (Splunk/ELK).
    """
    logger.remove()  # Remove default handler

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # Console logging
    logger.add(
        sys.stdout,
        format=log_format,
        level="DEBUG" if settings.DEBUG else "INFO",
        colorize=True,
    )

    # File logging (rotating & retention)
    log_dir = Path("./logs")
    log_dir.mkdir(exist_ok=True)

    logger.add(
        log_dir / "datapulse.log",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} - {message}",
    )

    logger.info(f"Logger initialized for project: {settings.PROJECT_NAME} [{settings.ENVIRONMENT}]")

# Execute logger setup on module import
setup_logger()
export_logger = logger
