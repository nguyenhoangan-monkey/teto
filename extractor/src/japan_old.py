import io
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup


def download_tariff_chapter(base_url: str, output_dir: Path, chap: int) -> None:
    file_path = output_dir / f"chapter_{chap:02d}.csv"

    if file_path.is_file():
        print(f"Skipping download: Chapter {chap:02d} already exists at {file_path}")
        return

    url = base_url.format(chap=chap)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print(f"Chapter {chap:02d}: Request timed out after 10 seconds.")
        return
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "Unknown"
        print(f"Chapter {chap:02d}: HTTP error ({status}) - {e}")
        return
    except requests.exceptions.RequestException as e:
        print(f"Chapter {chap:02d}: Network error - {e}")
        return

    try:
        tables = pd.read_html(
            io.StringIO(str(BeautifulSoup(response.content, "html.parser")))
        )
    except ValueError:
        print(f"Chapter {chap:02d}: No HTML <table> tags found on page.")
        return

    if not tables:
        print(f"Chapter {chap:02d}: Skipped (empty list).")
        return

    df = max(tables, key=len)

    if df.empty or len(df) <= 1:
        reason = "empty table" if df.empty else f"insufficient rows ({len(df)})"
        print(f"Chapter {chap:02d}: Skipped ({reason}).")
        return

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ["_".join(str(c) for c in col).strip() for col in df.columns.values]

    df.insert(0, "Chapter", f"Chapter {chap:02d}")

    try:
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        print(f"Saved Chapter {chap:02d} ({len(df)} rows)")
    except OSError as e:
        print(f"Chapter {chap:02d}: Failed to write file to {file_path} - {e}")


BASE_URL = "https://www.customs.go.jp/english/tariff/"
SCHEDULES_URLS = {
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

def hs_chapters():
    for ch in range(1, 98):
        if ch == 77:  # Reserved by WCO for future use
            continue
        yield ch


OUTPUT_DIR = Path("japan")
SCHEDULES_DIR = OUTPUT_DIR / "schedules"
SCHEDULES_DIR.mkdir(parents=True, exist_ok=True)

for date, page in SCHEDULES_URLS.items():
    print(f"\nProcessing schedule {date} ---")

    DATE_DIR = OUTPUT_DIR / date
    DATE_DIR.mkdir(parents=True, exist_ok=True)

    for chapter in hs_chapters():
        csv_file_path = DATE_DIR / f"chapter_{chapter}.csv"

        if csv_file_path.exists():
            print(f"Skipping download: Chapter {chapter} already exists at {csv_file_path}")
            continue

        download_tariff_chapter(BASE_URL + page, DATE_DIR, chapter)

    csv_files = sorted(DATE_DIR.glob("chapter_*.csv"))

    if csv_files:
        master_df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)
        master_path = SCHEDULES_DIR / f"japan-{date}.csv"

        master_df.to_csv(master_path, index=False, encoding="utf-8-sig")
        print(f"Combined {len(csv_files)} files into master schedule: {master_path} ({len(master_df)} rows).")

    else:
        print(f"No chapter files found to merge for {date}.")
