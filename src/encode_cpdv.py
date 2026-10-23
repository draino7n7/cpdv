#!/usr/bin/env python3
"""
Catholic Public Domain Version (CPDV) Bible JSON Encoder.

Downloads the 73 books of the CPDV Bible (2009 Original Edition by Ronald L. Conte Jr.)
from https://www.sacredbible.org/catholic/, decodes from windows-1252 to UTF-8,
and writes:
  - CPDV-JSON/<BookCode>.json (73 individual book JSON files)
  - CPDV-JSON/EntireBible-CPDV.json (complete 73-book Bible in a single JSON file)

Usage:
  python src/encode_cpdv.py
  python src/encode_cpdv.py --html-dir path/to/cached_html
"""

import argparse
import concurrent.futures
import json
import sys
import time
import urllib.request
from pathlib import Path
from typing import Dict, Optional, Tuple

BASE_URL = "https://www.sacredbible.org/catholic/"

BOOKS: Tuple[str, ...] = (
    # Old Testament (46 books)
    "OT-01_Genesis",
    "OT-02_Exodus",
    "OT-03_Leviticus",
    "OT-04_Numbers",
    "OT-05_Deuteronomy",
    "OT-06_Joshua",
    "OT-07_Judges",
    "OT-08_Ruth",
    "OT-09_1-Samuel",
    "OT-10_2-Samuel",
    "OT-11_1-Kings",
    "OT-12_2-Kings",
    "OT-13_1-Chronicles",
    "OT-14_2-Chronicles",
    "OT-15_Ezra",
    "OT-16_Nehemiah",
    "OT-17_Tobit",
    "OT-18_Judith",
    "OT-19_Esther",
    "OT-20_Job",
    "OT-21_Psalms",
    "OT-22_Proverbs",
    "OT-23_Ecclesiastes",
    "OT-24_Song2",
    "OT-25_Wisdom",
    "OT-26_Sirach",
    "OT-27_Isaiah",
    "OT-28_Jeremiah",
    "OT-29_Lamentations",
    "OT-30_Baruch",
    "OT-31_Ezekiel",
    "OT-32_Daniel",
    "OT-33_Hosea",
    "OT-34_Joel",
    "OT-35_Amos",
    "OT-36_Obadiah",
    "OT-37_Jonah",
    "OT-38_Micah",
    "OT-39_Nahum",
    "OT-40_Habakkuk",
    "OT-41_Zephaniah",
    "OT-42_Haggai",
    "OT-43_Zechariah",
    "OT-44_Malachi",
    "OT-45_1-Maccabees",
    "OT-46_2-Maccabees",
    # New Testament (27 books)
    "NT-01_Matthew",
    "NT-02_Mark",
    "NT-03_Luke",
    "NT-04_John",
    "NT-05_Acts",
    "NT-06_Romans",
    "NT-07_1-Corinthians",
    "NT-08_2-Corinthians",
    "NT-09_Galatians",
    "NT-10_Ephesians",
    "NT-11_Philippians",
    "NT-12_Colossians",
    "NT-13_1-Thessalonians",
    "NT-14_2-Thessalonians",
    "NT-15_1-Timothy",
    "NT-16_2-Timothy",
    "NT-17_Titus",
    "NT-18_Philemon",
    "NT-19_Hebrews",
    "NT-20_James",
    "NT-21_1-Peter",
    "NT-22_2-Peter",
    "NT-23_1-John",
    "NT-24_2-John",
    "NT-25_3-John",
    "NT-26_Jude",
    "NT-27_Revelation",
)


def fetch_book_html(book_name: str, html_dir: Optional[Path] = None, timeout: int = 30) -> str:
    """Fetch a book's raw HTML (from local cache if available, otherwise from sacredbible.org)."""
    if html_dir is not None:
        html_file = html_dir / f"{book_name}.htm"
        if html_file.exists():
            return html_file.read_bytes().decode("windows-1252")

    url = f"{BASE_URL}{book_name}.htm"
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        raw_bytes = resp.read()

    if html_dir is not None:
        html_dir.mkdir(parents=True, exist_ok=True)
        (html_dir / f"{book_name}.htm").write_bytes(raw_bytes)

    return raw_bytes.decode("windows-1252")


def parse_book_html(html_text: str) -> Dict[str, Dict[str, str]]:
    """
    Parse CPDV HTML text into a nested dict of {chapter: {verse: text}}.

    Handles both CRLF (\\r\\n) and LF (\\n) line endings (e.g., NT-27_Revelation.htm),
    non-numeric prologue chapters ("P" in Sirach and Lamentations), and verses with
    or without a trailing <BR> tag (e.g., Judges 21:24 and Malachi 4:6).
    """
    book: Dict[str, Dict[str, str]] = {}

    for line in html_text.splitlines():
        if not line.startswith("{"):
            continue

        end_meta = line.index("}")
        meta = line[1:end_meta]
        chapter, verse = meta.split(":", 1)

        # Strip "<BR>" and extract everything after "{chapter:verse} " without truncating
        cleaned_line = line.replace("<BR>", "")
        content = cleaned_line[end_meta + 2 :]

        if chapter not in book:
            book[chapter] = {}
        book[chapter][verse] = content

    return book


def encode_all(
    output_dir: Path,
    html_dir: Optional[Path] = None,
    workers: int = 6,
) -> Tuple[int, int, int]:
    """Download/parse all 73 books and write individual + combined JSON files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    def _load(book_name: str) -> Tuple[str, Dict[str, Dict[str, str]]]:
        html_text = fetch_book_html(book_name, html_dir=html_dir)
        return book_name, parse_book_html(html_text)

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        loaded_books = dict(executor.map(_load, BOOKS))

    bible_map: Dict[str, object] = {"charset": "UTF-8"}
    total_chapters = 0
    total_verses = 0

    for book_name in BOOKS:
        book_chapters = loaded_books[book_name]
        total_chapters += len(book_chapters)
        total_verses += sum(len(v_map) for v_map in book_chapters.values())

        # In EntireBible-CPDV.json, the key is the suffix after "_" (e.g. "Genesis")
        short_name = book_name.split("_", 1)[1]
        bible_map[short_name] = {ch: dict(v_map) for ch, v_map in book_chapters.items()}

        # Individual book JSON includes trailing "charset": "UTF-8"
        book_json_obj: Dict[str, object] = {ch: dict(v_map) for ch, v_map in book_chapters.items()}
        book_json_obj["charset"] = "UTF-8"

        book_file = output_dir / f"{book_name}.json"
        book_file.write_text(
            json.dumps(book_json_obj, indent=4, ensure_ascii=False),
            encoding="utf-8",
        )

    entire_bible_file = output_dir / "EntireBible-CPDV.json"
    entire_bible_file.write_text(
        json.dumps(bible_map, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    return len(BOOKS), total_chapters, total_verses


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        description="Download and encode the 73 books of the CPDV Bible into UTF-8 JSON."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=repo_root / "CPDV-JSON",
        help="Directory to write JSON files (default: <repo>/CPDV-JSON)",
    )
    parser.add_argument(
        "--html-dir",
        type=Path,
        default=None,
        help="Optional directory to read/cache raw .htm files",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=6,
        help="Max concurrent HTTP downloads (default: 6)",
    )
    args = parser.parse_args()

    print("Encoding Bible-CPDV to JSON...")
    start_time = time.perf_counter()
    num_books, num_chapters, num_verses = encode_all(
        output_dir=args.output_dir,
        html_dir=args.html_dir,
        workers=args.workers,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    print(
        f"Finished encoding CPDV Bible to JSON ({num_books} books, "
        f"{num_chapters} chapters, {num_verses} verses) - {elapsed_ms}ms"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
