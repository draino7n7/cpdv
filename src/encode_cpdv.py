#!/usr/bin/env python3
"""
Catholic Public Domain Version (CPDV) Bible JSON Encoder.

Downloads the 73 books of the CPDV Bible (2009 Original Edition by Ronald L. Conte Jr.)
from https://www.sacredbible.org/catholic/, decodes from windows-1252 to UTF-8,
and writes:
  - CPDV-JSON/<BookCode>.json (73 individual book JSON files)
  - CPDV-JSON/EntireBible-CPDV.json (complete 73-book Bible in a single JSON file)
  - CPDV-JSON/books.json (canonical metadata index with names, abbreviations, and counts)

Usage:
  python src/encode_cpdv.py
  python src/encode_cpdv.py --clean
  python src/encode_cpdv.py --normalize-whitespace --strip-italics --fix-upstream-typos
  python src/encode_cpdv.py --html-dir path/to/cached_html
"""

import argparse
import concurrent.futures
import json
import re
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE_URL = "https://www.sacredbible.org/catholic/"

# Canonical 73-book Catholic metadata catalog:
# (code, name, full_title, abbreviation, osis, usfm, alt_names)
BOOK_CATALOG: Tuple[Tuple[str, str, str, str, str, str, List[str]], ...] = (
    # Old Testament (46 books)
    ("OT-01_Genesis", "Genesis", "The Book of Genesis", "Gn", "Gen", "GEN", []),
    ("OT-02_Exodus", "Exodus", "The Book of Exodus", "Ex", "Exod", "EXO", []),
    ("OT-03_Leviticus", "Leviticus", "The Book of Leviticus", "Lv", "Lev", "LEV", []),
    ("OT-04_Numbers", "Numbers", "The Book of Numbers", "Nm", "Num", "NUM", []),
    ("OT-05_Deuteronomy", "Deuteronomy", "The Book of Deuteronomy", "Dt", "Deut", "DEU", []),
    ("OT-06_Joshua", "Joshua", "The Book of Joshua", "Jos", "Josh", "JOS", ["Josue"]),
    ("OT-07_Judges", "Judges", "The Book of Judges", "Jgs", "Judg", "JDG", []),
    ("OT-08_Ruth", "Ruth", "The Book of Ruth", "Ru", "Ruth", "RUT", []),
    ("OT-09_1-Samuel", "1 Samuel", "The First Book of Samuel", "1 Sm", "1Sam", "1SA", ["1 Kings (Douay-Rheims)"]),
    ("OT-10_2-Samuel", "2 Samuel", "The Second Book of Samuel", "2 Sm", "2Sam", "2SA", ["2 Kings (Douay-Rheims)"]),
    ("OT-11_1-Kings", "1 Kings", "The First Book of Kings", "1 Kgs", "1Kgs", "1KI", ["3 Kings (Douay-Rheims)"]),
    ("OT-12_2-Kings", "2 Kings", "The Second Book of Kings", "2 Kgs", "2Kgs", "2KI", ["4 Kings (Douay-Rheims)"]),
    ("OT-13_1-Chronicles", "1 Chronicles", "The First Book of Chronicles", "1 Chr", "1Chr", "1CH", ["1 Paralipomenon"]),
    ("OT-14_2-Chronicles", "2 Chronicles", "The Second Book of Chronicles", "2 Chr", "2Chr", "2CH", ["2 Paralipomenon"]),
    ("OT-15_Ezra", "Ezra", "The Book of Ezra", "Ezr", "Ezra", "EZR", ["1 Esdras"]),
    ("OT-16_Nehemiah", "Nehemiah", "The Book of Nehemiah", "Neh", "Neh", "NEH", ["2 Esdras"]),
    ("OT-17_Tobit", "Tobit", "The Book of Tobit", "Tb", "Tob", "TOB", ["Tobias"]),
    ("OT-18_Judith", "Judith", "The Book of Judith", "Jdt", "Jdt", "JDT", []),
    ("OT-19_Esther", "Esther", "The Book of Esther", "Est", "Esth", "EST", []),
    ("OT-20_Job", "Job", "The Book of Job", "Jb", "Job", "JOB", []),
    ("OT-21_Psalms", "Psalms", "The Book of Psalms", "Ps", "Ps", "PSA", ["Psalter"]),
    ("OT-22_Proverbs", "Proverbs", "The Book of Proverbs", "Prv", "Prov", "PRO", []),
    ("OT-23_Ecclesiastes", "Ecclesiastes", "The Words of Ecclesiastes", "Eccl", "Eccl", "ECC", ["Qoheleth"]),
    ("OT-24_Song2", "Song of Songs", "The Song of Solomon", "Sg", "Song", "SNG", ["Canticle of Canticles", "Song of Solomon"]),
    ("OT-25_Wisdom", "Wisdom", "The Wisdom of Solomon", "Wis", "Wis", "WIS", ["Book of Wisdom"]),
    ("OT-26_Sirach", "Sirach", "The Book of Ecclesiasticus", "Sir", "Sir", "SIR", ["Ecclesiasticus", "Wisdom of Ben Sira"]),
    ("OT-27_Isaiah", "Isaiah", "The Prophecy of Isaiah", "Is", "Isa", "ISA", ["Isaias"]),
    ("OT-28_Jeremiah", "Jeremiah", "The Prophecy of Jeremiah", "Jer", "Jer", "JER", ["Jeremias"]),
    ("OT-29_Lamentations", "Lamentations", "The Lamentations of Jeremiah", "Lam", "Lam", "LAM", []),
    ("OT-30_Baruch", "Baruch", "The Book of Baruch", "Bar", "Bar", "BAR", []),
    ("OT-31_Ezekiel", "Ezekiel", "The Prophecy of Ezekiel", "Ez", "Ezek", "EZK", ["Ezechiel"]),
    ("OT-32_Daniel", "Daniel", "The Prophecy of Daniel", "Dn", "Dan", "DAN", []),
    ("OT-33_Hosea", "Hosea", "The Prophecy of Hosea", "Hos", "Hos", "HOS", ["Osee"]),
    ("OT-34_Joel", "Joel", "The Prophecy of Joel", "Jl", "Joel", "JOL", []),
    ("OT-35_Amos", "Amos", "The Prophecy of Amos", "Am", "Amos", "AMO", []),
    ("OT-36_Obadiah", "Obadiah", "The Prophecy of Obadiah", "Ob", "Obad", "OBA", ["Abdias"]),
    ("OT-37_Jonah", "Jonah", "The Prophecy of Jonah", "Jon", "Jonah", "JON", ["Jonas"]),
    ("OT-38_Micah", "Micah", "The Prophecy of Micah", "Mi", "Mic", "MIC", ["Micheas"]),
    ("OT-39_Nahum", "Nahum", "The Prophecy of Nahum", "Na", "Nah", "NAM", []),
    ("OT-40_Habakkuk", "Habakkuk", "The Prophecy of Habakkuk", "Hb", "Hab", "HAB", ["Habacuc"]),
    ("OT-41_Zephaniah", "Zephaniah", "The Prophecy of Zephaniah", "Zep", "Zeph", "ZEP", ["Sophonias"]),
    ("OT-42_Haggai", "Haggai", "The Prophecy of Haggai", "Hg", "Hag", "HAG", ["Aggeus"]),
    ("OT-43_Zechariah", "Zechariah", "The Prophecy of Zechariah", "Zec", "Zech", "ZEC", ["Zacharias"]),
    ("OT-44_Malachi", "Malachi", "The Prophecy of Malachi", "Mal", "Mal", "MAL", ["Malachias"]),
    ("OT-45_1-Maccabees", "1 Maccabees", "The First Book of Maccabees", "1 Mc", "1Macc", "1MA", ["1 Machabees"]),
    ("OT-46_2-Maccabees", "2 Maccabees", "The Second Book of Maccabees", "2 Mc", "2Macc", "2MA", ["2 Machabees"]),
    # New Testament (27 books)
    ("NT-01_Matthew", "Matthew", "The Gospel of Matthew", "Mt", "Matt", "MAT", []),
    ("NT-02_Mark", "Mark", "The Gospel of Mark", "Mk", "Mark", "MRK", []),
    ("NT-03_Luke", "Luke", "The Gospel of Luke", "Lk", "Luke", "LUK", []),
    ("NT-04_John", "John", "The Gospel of John", "Jn", "John", "JHN", []),
    ("NT-05_Acts", "Acts of the Apostles", "The Acts of the Apostles", "Acts", "Acts", "ACT", ["Acts"]),
    ("NT-06_Romans", "Romans", "The Letter to the Romans", "Rom", "Rom", "ROM", []),
    ("NT-07_1-Corinthians", "1 Corinthians", "The First Letter to the Corinthians", "1 Cor", "1Cor", "1CO", []),
    ("NT-08_2-Corinthians", "2 Corinthians", "The Second Letter to the Corinthians", "2 Cor", "2Cor", "2CO", []),
    ("NT-09_Galatians", "Galatians", "The Letter to the Galatians", "Gal", "Gal", "GAL", []),
    ("NT-10_Ephesians", "Ephesians", "The Letter to the Ephesians", "Eph", "Eph", "EPH", []),
    ("NT-11_Philippians", "Philippians", "The Letter to the Philippians", "Phil", "Phil", "PHP", []),
    ("NT-12_Colossians", "Colossians", "The Letter to the Colossians", "Col", "Col", "COL", []),
    ("NT-13_1-Thessalonians", "1 Thessalonians", "The First Letter to the Thessalonians", "1 Thes", "1Thess", "1TH", []),
    ("NT-14_2-Thessalonians", "2 Thessalonians", "The Second Letter to the Thessalonians", "2 Thes", "2Thess", "2TH", []),
    ("NT-15_1-Timothy", "1 Timothy", "The First Letter to Timothy", "1 Tm", "1Tim", "1TI", []),
    ("NT-16_2-Timothy", "2 Timothy", "The Second Letter to Timothy", "2 Tm", "2Tim", "2TI", []),
    ("NT-17_Titus", "Titus", "The Letter to Titus", "Ti", "Titus", "TIT", []),
    ("NT-18_Philemon", "Philemon", "The Letter to Philemon", "Phlm", "Phlm", "PHM", []),
    ("NT-19_Hebrews", "Hebrews", "The Letter to the Hebrews", "Heb", "Heb", "HEB", []),
    ("NT-20_James", "James", "The Letter of James", "Jas", "Jas", "JAS", []),
    ("NT-21_1-Peter", "1 Peter", "The First Letter of Peter", "1 Pt", "1Pet", "1PE", []),
    ("NT-22_2-Peter", "2 Peter", "The Second Letter of Peter", "2 Pt", "2Pet", "2PE", []),
    ("NT-23_1-John", "1 John", "The First Letter of John", "1 Jn", "1John", "1JN", []),
    ("NT-24_2-John", "2 John", "The Second Letter of John", "2 Jn", "2John", "2JN", []),
    ("NT-25_3-John", "3 John", "The Third Letter of John", "3 Jn", "3John", "3JN", []),
    ("NT-26_Jude", "Jude", "The Letter of Jude", "Jude", "Jude", "JUD", []),
    ("NT-27_Revelation", "Revelation", "The Revelation of Jesus Christ", "Rv", "Rev", "REV", ["Apocalypse"]),
)

BOOKS: Tuple[str, ...] = tuple(item[0] for item in BOOK_CATALOG)


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


def normalize_verse_text(
    book_name: str,
    chapter: str,
    verse: str,
    content: str,
    normalize_whitespace: bool = False,
    strip_italics: bool = False,
    fix_upstream_typos: bool = False,
) -> str:
    """Apply optional text normalizations to a parsed verse string."""
    if strip_italics and "<I>" in content:
        content = re.sub(r"</?I>", "", content)

    if fix_upstream_typos:
        # In OT-45_1-Maccabees 14:49, the source HTML ends with an opening double quote (‘ “)
        # instead of a closing double quote (’ ”).
        if book_name == "OT-45_1-Maccabees" and chapter == "14" and verse == "49":
            if content.endswith("\u2019 \u201c") or content.endswith("\u2019\xa0\u201c"):
                content = content[:-1] + "\u201d"

    if normalize_whitespace:
        content = content.replace("\u00a0", " ")
        content = re.sub(r" {2,}", " ", content)
        content = content.strip()

    return content


def parse_book_html(
    html_text: str,
    book_name: str = "",
    normalize_whitespace: bool = False,
    strip_italics: bool = False,
    fix_upstream_typos: bool = False,
) -> Dict[str, Dict[str, str]]:
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

        content = normalize_verse_text(
            book_name=book_name,
            chapter=chapter,
            verse=verse,
            content=content,
            normalize_whitespace=normalize_whitespace,
            strip_italics=strip_italics,
            fix_upstream_typos=fix_upstream_typos,
        )

        if chapter not in book:
            book[chapter] = {}
        book[chapter][verse] = content

    return book


def encode_all(
    output_dir: Path,
    html_dir: Optional[Path] = None,
    workers: int = 6,
    normalize_whitespace: bool = False,
    strip_italics: bool = False,
    fix_upstream_typos: bool = False,
) -> Tuple[int, int, int]:
    """Download/parse all 73 books and write individual, combined, and metadata JSON files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    def _load(book_name: str) -> Tuple[str, Dict[str, Dict[str, str]]]:
        html_text = fetch_book_html(book_name, html_dir=html_dir)
        parsed = parse_book_html(
            html_text,
            book_name=book_name,
            normalize_whitespace=normalize_whitespace,
            strip_italics=strip_italics,
            fix_upstream_typos=fix_upstream_typos,
        )
        return book_name, parsed

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        loaded_books = dict(executor.map(_load, BOOKS))

    bible_map: Dict[str, Any] = {"charset": "UTF-8"}
    books_metadata_list: List[Dict[str, Any]] = []
    total_chapters = 0
    total_verses = 0
    ot_count = 0
    nt_count = 0

    for idx, (code, name, full_title, abbr, osis, usfm, alt_names) in enumerate(BOOK_CATALOG, start=1):
        book_chapters = loaded_books[code]
        chapter_keys = list(book_chapters.keys())
        chapter_verses = {ch: len(v_map) for ch, v_map in book_chapters.items()}
        book_verse_count = sum(chapter_verses.values())

        total_chapters += len(chapter_keys)
        total_verses += book_verse_count

        testament, num_part = code.split("_", 1)[0].split("-", 1)
        testament_order = int(num_part)
        if testament == "OT":
            ot_count += 1
        else:
            nt_count += 1

        # In EntireBible-CPDV.json, the key is the suffix after "_" (e.g. "Genesis", "Song2")
        short_name = code.split("_", 1)[1]
        bible_map[short_name] = {ch: dict(v_map) for ch, v_map in book_chapters.items()}

        # Individual book JSON includes trailing "charset": "UTF-8"
        book_json_obj: Dict[str, Any] = {ch: dict(v_map) for ch, v_map in book_chapters.items()}
        book_json_obj["charset"] = "UTF-8"

        book_file = output_dir / f"{code}.json"
        book_file.write_text(
            json.dumps(book_json_obj, indent=4, ensure_ascii=False),
            encoding="utf-8",
        )

        books_metadata_list.append(
            {
                "order": idx,
                "testament": testament,
                "testament_order": testament_order,
                "code": code,
                "file": f"{code}.json",
                "key": short_name,
                "name": name,
                "alt_names": alt_names,
                "full_title": full_title,
                "abbreviation": abbr,
                "osis": osis,
                "usfm": usfm,
                "has_prologue": "P" in book_chapters,
                "chapter_count": len(chapter_keys),
                "chapters": chapter_keys,
                "verse_count": book_verse_count,
                "chapter_verses": chapter_verses,
            }
        )

    entire_bible_file = output_dir / "EntireBible-CPDV.json"
    entire_bible_file.write_text(
        json.dumps(bible_map, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    books_index_obj: Dict[str, Any] = {
        "charset": "UTF-8",
        "translation": "Catholic Public Domain Version (CPDV)",
        "edition": "2009 Original Edition",
        "translator": "Ronald L. Conte Jr.",
        "source_url": BASE_URL,
        "license": "Public Domain",
        "book_count": len(BOOK_CATALOG),
        "old_testament_count": ot_count,
        "new_testament_count": nt_count,
        "chapter_count": total_chapters,
        "verse_count": total_verses,
        "normalization": {
            "normalize_whitespace": normalize_whitespace,
            "strip_italics": strip_italics,
            "fix_upstream_typos": fix_upstream_typos,
        },
        "books": books_metadata_list,
    }
    books_index_file = output_dir / "books.json"
    books_index_file.write_text(
        json.dumps(books_index_obj, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    return len(BOOK_CATALOG), total_chapters, total_verses


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
    parser.add_argument(
        "--normalize-whitespace",
        action="store_true",
        help="Replace NBSP (U+00A0) with regular space, collapse double spaces, and strip trailing spaces",
    )
    parser.add_argument(
        "--strip-italics",
        action="store_true",
        help="Strip <I>...</I> speaker label tags in OT-24_Song2",
    )
    parser.add_argument(
        "--fix-upstream-typos",
        action="store_true",
        help="Fix known upstream HTML punctuation typos (e.g., 1 Maccabees 14:49 trailing quote)",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Enable all optional text normalizations (--normalize-whitespace --strip-italics --fix-upstream-typos)",
    )
    args = parser.parse_args()

    norm_ws = args.normalize_whitespace or args.clean
    strip_it = args.strip_italics or args.clean
    fix_typos = args.fix_upstream_typos or args.clean

    mode_str = "raw HTML parity"
    if norm_ws or strip_it or fix_typos:
        flags = []
        if norm_ws:
            flags.append("normalize-whitespace")
        if strip_it:
            flags.append("strip-italics")
        if fix_typos:
            flags.append("fix-upstream-typos")
        mode_str = ", ".join(flags)

    print(f"Encoding Bible-CPDV to JSON (mode: {mode_str})...")
    start_time = time.perf_counter()
    num_books, num_chapters, num_verses = encode_all(
        output_dir=args.output_dir,
        html_dir=args.html_dir,
        workers=args.workers,
        normalize_whitespace=norm_ws,
        strip_italics=strip_it,
        fix_upstream_typos=fix_typos,
    )
    elapsed_ms = int((time.perf_counter() - start_time) * 1000)
    print(
        f"Finished encoding CPDV Bible to JSON ({num_books} books, "
        f"{num_chapters} chapters, {num_verses} verses) - {elapsed_ms}ms"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
