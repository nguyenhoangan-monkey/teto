import asyncio
import io
import logging
from pathlib import Path

import httpx
import pandas as pd
from tqdm.asyncio import tqdm

from providers import TariffProvider

logger = logging.getLogger(__name__)

HTML_HEADER = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
async def fetch_html(client: httpx.AsyncClient, url: str) -> bytes | None:
    response = await client.get(url, headers=HTML_HEADER, timeout=10.0)
    response.raise_for_status()
    return response.content


def html_to_df(html: bytes) -> pd.DataFrame | None:
    try:
        html_str = html.decode("utf-8-sig", errors="ignore")
        tables = pd.read_html(io.StringIO(html_str), flavor="lxml")
    except ValueError:
        return None

    tariff_table = max(tables, key=len) # heuristics
    if tariff_table.empty or len(tariff_table) <= 1:
        return None

    # flatten table
    if isinstance(tariff_table.columns, pd.MultiIndex):
        tariff_table.columns = ["_".join(str(c) for c in col).strip() for col in tariff_table.columns.values]

    return tariff_table


def merge_chapters(downloaded_df: dict[int, pd.DataFrame]) -> pd.DataFrame:
    list_of_dfs = [downloaded_df[ch] for ch in sorted(downloaded_df.keys())]
    return pd.concat(list_of_dfs, ignore_index=True)


def atomic_save(df: pd.DataFrame, file_path: Path) -> bool:
    tmp_file_path = file_path.with_suffix(".csv.tmp")
    try:
        df.to_csv(tmp_file_path, index=False, encoding="utf-8-sig")
        tmp_file_path.replace(file_path)
        return True
    except OSError as e:
        logger.error("Failed to write file to %s - %s", display_path(file_path), e)
        if tmp_file_path.exists():
            tmp_file_path.unlink()
        return False


def display_path(file_path: Path):
    try:
        return file_path.relative_to(Path.cwd())
    except ValueError:
        return file_path.name

class Orchestrator:
    def __init__(self, provider: type[TariffProvider], clients: int = 10):
        self.provider = provider
        self.semaphore = asyncio.Semaphore(clients)
        self.client: httpx.AsyncClient | None = None # initialization is async

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()


    async def chapter(self, url: str) -> pd.DataFrame | None:
        assert self.client is not None, "Orchestrator must be used as an async context manager."

        try:
            async with self.semaphore:
                html = await fetch_html(self.client, url)

            if html is not None:
                return await asyncio.to_thread(html_to_df, html)

        except httpx.TimeoutException:
            logger.debug("Timeout (10s): %s", url)
        except httpx.HTTPStatusError as e:
            status = e.response.status_code if e.response is not None else "unknown"
            logger.debug("HTTP %s: %s", status, url)
        except httpx.RequestError as e:
            logger.debug("Network failed for %s: %s", url, type(e).__name__)
        except (RuntimeError, asyncio.CancelledError):
            pass

        return None


    async def schedule(self, date:str, template: str, retries: int = 3) -> pd.DataFrame | None:
        assert self.client is not None, "Orchestrator must be used as an async context manager."

        urls_to_download = self.provider.get_chapters(template)
        downloaded_df: dict[int, pd.DataFrame] = {}

        for attempt in range(1, retries + 1):
            chapters, urls = zip(*urls_to_download.items())

            # progress bar!
            results = await tqdm.gather(
                *(self.chapter(url) for url in urls),
                desc=f"Download {date} ({attempt}/{retries})",
                leave=False,
                ncols=70,
                bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}",  # Hides speed/time
            )

            urls_to_download = {}
            for chapter, df in zip(chapters, results):
                if df is not None: downloaded_df[chapter] = df
                else: urls_to_download[chapter] = template.format(chap=chapter)

            # no more urls, no more tasks!
            if not urls_to_download:
                break

            logger.info("Schedule %s: attempt %d/%d, failed %d chapters, retrying...",
                date, attempt, retries, len(urls_to_download))
            await asyncio.sleep(2.0 * attempt)

        if urls_to_download:
            failed_chapters = " ".join(str(key) for key in urls_to_download)
            logger.error("Chapter(s) %s failed after %d attempts", failed_chapters, retries)
            return None

        return merge_chapters(downloaded_df)


    async def download(self, output: Path | str, force = False) -> None:
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        logger.info("Downloading %s at %s ---", self.provider.name(), self.provider.source())

        for date, template in self.provider.schedules():
            file_path = output_path / f"{date}.csv"
            if file_path.exists() and file_path.stat().st_size > 0 and not force:
                logger.info("Skipped schedule %s (cached)", date)
                continue

            df = await self.schedule(date, template)

            if df is None:
                logger.error("Cannot merge chapters for %s", date)
                continue

            if await asyncio.to_thread(atomic_save, df, file_path):
                logger.info("Downloaded and saved %s (%d rows)", date, len(df))

        logger.info("Download of %s completed.", self.provider.name())
