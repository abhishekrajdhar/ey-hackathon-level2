import logging
from .config import get_settings

_settings = get_settings()


def setup_logging() -> None:
    level = logging.INFO if _settings.environment == "prod" else logging.DEBUG
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
