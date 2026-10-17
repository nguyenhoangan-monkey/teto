import asyncio
import io
from pathlib import Path

import httpx
import pandas as pd

HTML_HEADER = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
async def fetch_html(client: httpx.AsyncClient, url: str) -> bytes | None:
    try:
        response = await client.get(url, headers=HTML_HEADER, timeout=10.0)
        response.raise_for_status()
        return response.content
    except httpx.TimeoutException:
        print(f"Request timed out after 10 seconds: {url}")
        return None
    except httpx.HTTPStatusError as e:
        status = e.response.status_code if e.response is not None else "Unknown"
        print(f"HTTP error ({status}) - {e}")
        return None
    except httpx.RequestError as e:
        print(f"Network error - {e}")
        return None



def html_to_df(html: bytes) -> pd.DataFrame | None:
    try:
        html_str = html.decode("utf-8-sig", errors="ignore")
        tables = pd.read_html(io.StringIO(html_str), flavor="lxml")
    except ValueError:
        print("No HTML <table> tags found on page.")
        return None

    # the biggest table in the website is probably the tariff table
    tariff_table = max(tables, key=len)
    if tariff_table.empty or len(tariff_table) <= 1:
        print("Table does not have body.")
        return

    # flatten table
    if isinstance(tariff_table.columns, pd.MultiIndex):
        tariff_table.columns = ["_".join(str(c) for c in col).strip() for col in tariff_table.columns.values]

    return tariff_table



class Orchestrator:
    def __init__(self, output: Path, clients: int = 10):
        self.semaphore = asyncio.Semaphore(clients)
        self.client: httpx.AsyncClient | None = None # initialization is async
        self.output = output
        self.output.mkdir(parents=True, exist_ok=True)

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()


    # one direct network request
    async def chapter(self, url: str) -> pd.DataFrame | None:
        assert self.client is not None, "Orchestrator must be used as an async context manager."

        async with self.semaphore:
            html = await fetch_html(self.client, url)

        if html is not None:
            return await asyncio.to_thread(html_to_df, html)

        return None


    # lazy, create tasks to the async scheduler
    async def schedule(self, template: str, retries: int = 3) -> pd.DataFrame | None:
        assert self.client is not None, "Orchestrator must be used as an async context manager."

        def hs_chapter():
            for ch in range(1, 98):
                if ch == 77:  # Reserved by WCO for future use
                    continue
                yield ch

        # initial state
        urls_to_download = {ch: template.format(chap=ch) for ch in hs_chapter()}
        downloaded_df: dict[int, pd.DataFrame] = {}

        for attempt in range(1, retries + 1):
            pending_chapters = list(urls_to_download.keys())

            tasks = [self.chapter(urls_to_download[ch]) for ch in pending_chapters]
            results = await asyncio.gather(*tasks)

            for chapter, df in zip(pending_chapters, results):
                if df is not None:
                    downloaded_df[chapter] = df
                    del urls_to_download[chapter]

            # we finished early!!!
            if not urls_to_download:
                break

            await asyncio.sleep(2.0 * attempt)

        if urls_to_download:
            print(f"Error: Chapters {list(urls_to_download.keys())} failed after {retries} attempts.")
            return None

        list_of_dfs = [downloaded_df[ch] for ch in sorted(downloaded_df.keys())]
        return pd.concat(list_of_dfs, ignore_index=True)


    # manage folders, I/O and status
    async def download(self, force = False) -> None:
        from config import JapanCustoms

        for date, template in JapanCustoms.english_schedules():
            file_path = self.output / f"{date}.csv"
            if file_path.exists() and file_path.stat().st_size > 0 and not force:
                print(f"Skipping schedule {date}: Already exists ({file_path})")
                continue

            print(f"\nProcessing schedule {date} --- ", end="")
            df = await self.schedule(template)

            if df is None:
                print(f"No chapter files found to merge for {date}.")
                continue

            # write to temp ensures we write one complete file at a time
            tmp_file_path = self.output / f"{date}.csv.tmp"
            try:
                await asyncio.to_thread(df.to_csv, tmp_file_path, index=False, encoding="utf-8-sig")
                tmp_file_path.replace(file_path)
                print(f"Saved {date} ({len(df)} rows)")
            except OSError as e:
                print(f"Failed to write file to {file_path} - {e}")
                if tmp_file_path.exists():
                    tmp_file_path.unlink()
