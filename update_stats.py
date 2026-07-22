from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup


NPB_URL = "https://npb.jp/bis/players/31135133.html"
TARGET_SEASON = 2026

# 2025年終了時点の日米通算安打数
PREVIOUS_SEASON_HITS = 1832

OUTPUT_FILE = Path(__file__).resolve().parent / "data.js"


class StatsParseError(RuntimeError):
    """NPBページの構造または値が想定と異なる場合のエラー。"""


def fetch_npb_html() -> bytes:
    response = requests.get(
        NPB_URL,
        timeout=30,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (compatible; "
                "AkiyamaHitsGitHubPages/1.0; +https://github.com/)"
            )
        },
    )
    response.raise_for_status()
    return response.content


def parse_current_hits(soup: BeautifulSoup) -> int:
    table = soup.select_one("#tablefix_b")

    if table is None:
        raise StatsParseError("打撃成績テーブル #tablefix_b が見つかりません。")

    season_row = None

    for row in table.select("tbody tr.registerStats"):
        year_cell = row.select_one("td.year")

        if year_cell and year_cell.get_text(strip=True) == str(TARGET_SEASON):
            season_row = row
            break

    if season_row is None:
        raise StatsParseError(
            f"{TARGET_SEASON}年の成績行が見つかりません。"
        )

    cells = season_row.find_all("td", recursive=False)

    # 見出し上で「安打」は7列目。Pythonの添字では6。
    if len(cells) < 7:
        raise StatsParseError(
            f"成績行の列数が不足しています: {len(cells)}列"
        )

    hit_text = cells[6].get_text(strip=True)

    if not re.fullmatch(r"\d+", hit_text):
        raise StatsParseError(
            f"今季安打数が整数ではありません: {hit_text!r}"
        )

    return int(hit_text)


def parse_as_of_date(soup: BeautifulSoup) -> tuple[str, str, str]:
    time_element = soup.select_one("#p_common_smenu time")

    if time_element is None:
        raise StatsParseError(
            "情報日付の要素 #p_common_smenu time が見つかりません。"
        )

    source_text = " ".join(time_element.stripped_strings)

    match = re.search(
        r"(\d{4})年\s*(\d{1,2})月\s*(\d{1,2})日",
        source_text,
    )

    if match is None:
        raise StatsParseError(
            f"情報日付を解析できません: {source_text!r}"
        )

    year, month, day = map(int, match.groups())

    display_date = f"{year}.{month}.{day}"
    iso_date = f"{year:04d}-{month:02d}-{day:02d}"

    return display_date, iso_date, source_text


def build_stats(html: bytes) -> dict[str, object]:
    soup = BeautifulSoup(html, "html.parser")

    current_hits = parse_current_hits(soup)
    display_date, iso_date, source_date_text = parse_as_of_date(soup)
    total_hits = PREVIOUS_SEASON_HITS + current_hits

    return {
        "season": TARGET_SEASON,
        "previousHits": PREVIOUS_SEASON_HITS,
        "currentHits": current_hits,
        "totalHits": total_hits,
        "asOfDate": display_date,
        "asOfDateIso": iso_date,
        "sourceDateText": source_date_text,
        "sourceUrl": NPB_URL,
        "generatedAtUtc": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat(),
    }


def write_data_js(stats: dict[str, object]) -> None:
    json_text = json.dumps(
        stats,
        ensure_ascii=False,
        indent=2,
    )

    output = (
        "// このファイルは update_stats.py により自動生成されます。\n"
        f"window.AKIYAMA_STATS = {json_text};\n"
    )

    OUTPUT_FILE.write_text(output, encoding="utf-8")


def main() -> None:
    html = fetch_npb_html()
    stats = build_stats(html)
    write_data_js(stats)

    print(
        "Updated:",
        f"{stats['previousHits']}+{stats['currentHits']}"
        f"={stats['totalHits']}",
        stats["asOfDate"],
    )


if __name__ == "__main__":
    main()
