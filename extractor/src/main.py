import asyncio
import logging
from pathlib import Path

from rich.logging import RichHandler

from html_extractor import Orchestrator as HtmlExtractor
from providers import JapanCustoms

logger = logging.getLogger(__name__)

STAGED_DIR = Path("data/staged")


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, show_path=False)]
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


async def main():
    setup_logging()

    logger.info("=== Tariff extraction pipeline ===")
    try:
        async with HtmlExtractor(JapanCustoms) as orchestrator:
            await orchestrator.download(STAGED_DIR / "japan")

        logger.info("=== Tariff extraction completed. ===")
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Process interrupted by user (Ctrl+C). Exiting...")


if __name__ == "__main__":
    asyncio.run(main())
