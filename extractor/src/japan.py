import io
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

from interface import Browser, Orchestrator, Storage


class Html(Browser):
    def __init__(self):
        self.timeout = 10
        self.header = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
    def fetch(self, url):
        try:
            response = requests.get(url, headers=self.header, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.exceptions.Timeout:
            print("Request timed out after 10 seconds.")
            return None
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "Unknown"
            print(f"HTTP error ({status}) - {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Network error - {e}")
            return None


def get_biggest_table(html):
    """In Japan Custom's website, the biggest table is the tariff schedule itself"""
    try:
        soup = BeautifulSoup(html, "html.parser")
        tables = pd.read_html(io.StringIO(str(soup)))
    except ValueError:
        print("No HTML <table> tags found on page")
        return None

    if not tables:
        print("Skipped: Empty table list returned")
        return None

    # the logic
    df = max(tables, key=len)

    if df.empty or len(df) <= 1:
        reason = "empty table" if df.empty else f"insufficient rows ({len(df)})"
        print(f"Skipped ({reason})")
        return None

    # some pages in japan customs have multiple layers for headers
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ["_".join(str(c) for c in col).strip() for col in df.columns.values]

    return df


class LocalDisk(Storage):
    def save(self, table, path):
        try:
            table.to_csv(path, index=False, encoding="utf-8-sig")
            return True
        except OSError as e:
            print(f"Failed to write table to {path} - {e}")
            return False

    def exists(self, path):
        return path.is_file()


def merge_chapters(file_chapter_map: list[tuple[int, Path]], save):
    dfs = []

    for chap, path in file_chapter_map:
        if path.exists():
            df = pd.read_csv(path)
            df.insert(0, "Chapter", chap)
            dfs.append(df)

    if not dfs:
        print(f"No chapter files found to merge for {save.name}.")
        return pd.DataFrame()

    master_df = pd.concat(dfs, ignore_index=True)

    try:
        master_df.to_csv(save, index=False, encoding="utf-8-sig")
        print(
            f"Combined {len(dfs)} files into master schedule: "
            f"{save} ({len(master_df)} rows)."
        )
    except OSError as e:
        print(f"Failed to write master schedule to {save} - {e}")

    return master_df



class Extractor(Orchestrator):
    def __init__(self, browser: Browser, storage: Storage, folder: Path) -> None:
        self.browser = browser
        self.storage = storage
        self.folder = folder
        self.export = self.folder / "schedules"

        # make folder for both self.folder and self.export
        self.export.mkdir(parents=True, exist_ok=True)


    def chapter(self, url, chapter, output):
        # has potential to check for idempotency
        if self.storage.exists(output):
            return True

        content = self.browser.fetch(url)
        if content is None:
            return False

        table = get_biggest_table(content)
        if table is None:
            return False

        return self.storage.save(table, output)


    def schedule(self, url, date):
        def hs_chapters():
            for chapter in range(1, 98):
                if chapter == 77:
                    continue
                yield chapter

        date_dir = self.folder / date
        date_dir.mkdir(parents=True, exist_ok=True)
        file_chapter_map = []

        return_value = True
        for chapter in hs_chapters():
            formatted_url = url.format(chap=chapter)
            csv_path = date_dir / f"chapter_{chapter:02d}.csv"

            match self.chapter(formatted_url, chapter, csv_path):
                case False:
                    return_value = False
                case True:
                    file_chapter_map.append((chapter, csv_path))

        merge_chapters(sorted(file_chapter_map), date)
        return return_value


    def all(self, schedules):
        for date, web in schedules:
            if (self.schedule(web, date) == False):
                return False

        return True


def JapanCustoms():
    BASE_URL = "https://www.customs.go.jp/english/tariff/"
    SCHEDULE_MAP = {
        "2026_08_08": "2026_08_08/data/print_e_{chap:02d}.htm",
        "2026_08_01": "2026_08_01/data/print_e_{chap:02d}.htm",
        "2026_07_09": "2026_07_09/data/print_e_{chap:02d}.htm",
        "2026_04_01": "2026_04_01/data/print_e_{chap:02d}.htm",
        "2026_01_01": "2026_01_01/data/print_e_{chap:02d}.htm",
        "2025_04_01": "2025_04_01/data/print_e_{chap:02d}.htm",
        "2025_01_01": "2025_01_01/data/print_e_{chap:02d}.htm",
        "2024_04_01": "2024_04_01/data/print_e_{chap:02d}.htm",
        "2024_02_01": "2024_02_01/data/print_e_{chap:02d}.htm",
        "2024_01_01": "2024_01_01/data/print_e_{chap:02d}.htm",
        "2023_04_01": "2023_04_01/data/print_e_{chap:02d}.htm",
        "2023_02_21": "2023_02_21/data/print_e_{chap:02d}.htm",
        "2023_01_01": "2023_01_01/data/print_e_{chap:02d}.htm",
        "2022_12_08": "2022_12_08/data/print_e_{chap:02d}.htm",
        "2022_12_01": "2022_12_01/data/print_e_{chap:02d}.htm",
        "2022_11_29": "2022_11_29/data/print_e_{chap:02d}.htm",
        "2022_04_01": "2022_04_01/data/print_e_{chap:02d}.htm",
        "2022_01_01": "2022_1_1/data/print_e_{chap:02d}.htm",
        "2021_10_22": "2021_10_22/data/print_e_{chap:02d}.htm",
        "2021_09_19": "2021_9/data/print_e_{chap:02d}.htm",
        "2021_04_01": "2021_4/data/print_e_{chap:02d}.htm",
        "2021_01_01": "2021_1/data/print_e_{chap:02d}.htm",
        "2020_10_01": "2020_10/data/print_e_{chap:02d}.htm",
        "2020_06_27": "2020_6/data/print_e_{chap:02d}.htm",
        "2020_04_01": "2020_4/data/print_e_{chap:02d}.htm",
        "2020_01_01": "2020_1/data/print_e_{chap:02d}.htm",
        "2019_04_01": "2019_4/data/print_e_{chap:02d}.htm",
        "2019_02_01": "2019_2/data/print_e_{chap:02d}.htm",
        "2019_01_14": "2019_1/data/print_e_{chap:02d}.htm",
        "2018_12_30": "2018_12/data/print_e_{chap:02d}.htm",
        "2018_04_01": "2018_4/data/print_e_{chap:02d}.htm",
        "2018_01_01": "2018_1/data/print_e_{chap:02d}.htm",
        "2017_05_16": "2017_5/data/print_e_{chap:02d}.htm",
        "2017_04_01": "2017_4/data/print_e_{chap:02d}.htm",
        "2017_01_01": "2017_1/data/print_e_{chap:02d}.htm",
        "2016_06_07": "2016_6/data/print_e_{chap:02d}.htm",
        "2016_04_01": "2016_4/data/print_e_{chap:02d}.htm",
        "2016_01_01": "2016_1/data/print_e_{chap:02d}.htm",
        "2015_04_01": "2015_4/data/print_e_{chap:02d}.htm",
        "2015_01_15": "2015_115/data/print_e_{chap:02d}.htm",
        "2015_01_01": "2015_1/data/print_e_{chap:02d}.htm",
        "2014_04_01": "2014_4/data/print_e_{chap:02d}.htm",
        "2014_01_01": "2014_1/data/print_i201401e_{chap:02d}.htm",
        "2013_04_01": "2013_4/data/print_i201304e_{chap:02d}.htm",
        "2013_01_01": "2013_1/data/print_i201301e_{chap:02d}.htm",
        "2012_04_01": "2012_4/data/print_i201204e_{chap:02d}.htm",
        "2012_03_01": "2012_3/data/print_i201203e_{chap:02d}.htm",
        "2012_01_01": "2012_1/data/print_i201201e_{chap:02d}.htm",
        "2011_08_01": "2011_8/data/print_i201108e_{chap:02d}.htm",
        "2011_04_01": "2011_4/data/print_i201104e_{chap:02d}.htm",
        "2011_01_01": "2011/data/print_i201101e_{chap:02d}.htm",
        "2010_04_01": "2010_4/data/print_i201004e_{chap:02d}.htm",
        "2010_01_01": "2010/data/print_i201001e_{chap:02d}.htm",
        "2009_06_01": "2009_6/data/print_200910e_{chap:02d}.htm",
        "2009_04_01": "2009_4/data/print_{chap:02d}.htm",
        "2009_01_01": "2009/data/print_{chap:02d}.htm",
        "2008_04_01": "2008_4/data/print_{chap:02d}.htm",
        "2008_01_01": "2008/data/print_{chap:02d}.htm",
        "2007_04_01": "2007_4/data/print_{chap:02d}.htm",
    }

    for date, path in SCHEDULE_MAP.items():
        yield date, BASE_URL + path
