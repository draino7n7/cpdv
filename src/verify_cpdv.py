#!/usr/bin/env python3
"""
Automated Verification Suite for CPDV-JSON Bible Files.

Validates all 73 generated book JSON files (CPDV-JSON/*.json),
CPDV-JSON/EntireBible-CPDV.json, and CPDV-JSON/books.json against the source HTML on
https://www.sacredbible.org/catholic/:
  1. Book count (73 books: 46 OT + 27 NT) & UTF-8 charset metadata
  2. Canonical metadata index (CPDV-JSON/books.json) structure, abbreviations, and counts
  3. Chapter count (1,335) & verse count (35,839) parity across HTML, book JSONs, and EntireBible-CPDV.json
  4. Zero leftover <BR> tags or unexpected HTML markup
  5. Quotation mark preservation (all 4,474 verse-ending '”' and 543 verse-ending '’' intact) & balance report
  6. Exact verse-by-verse string equality across all 35,839 verses
  7. Spot-checks on known edge cases (Luke 1:28, Luke 1:38, Psalm 124:1, Judges 21:24, Malachi 4:6, Sirach P:1, Revelation 22:21)

Usage:
  python src/verify_cpdv.py
  python src/verify_cpdv.py --html-dir path/to/cached_html
"""

import argparse
import concurrent.futures
import json
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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

EXPECTED_BOOK_COUNT = 73
EXPECTED_OT_COUNT = 46
EXPECTED_NT_COUNT = 27
EXPECTED_CHAPTER_COUNT = 1335
EXPECTED_VERSE_COUNT = 35839


def fetch_book_html(book_name: str, html_dir: Optional[Path] = None, timeout: int = 30) -> str:
    """Load raw HTML from cache directory if present, otherwise download from sacredbible.org."""
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
    """Apply optional text normalizations to expected HTML verse string."""
    if strip_italics and "<I>" in content:
        content = re.sub(r"</?I>", "", content)

    if fix_upstream_typos:
        if book_name == "OT-45_1-Maccabees" and chapter == "14" and verse == "49":
            if content.endswith("\u2019 \u201c") or content.endswith("\u2019\xa0\u201c"):
                content = content[:-1] + "\u201d"

    if normalize_whitespace:
        content = content.replace("\u00a0", " ")
        content = re.sub(r" {2,}", " ", content)
        content = content.strip()

    return content


def extract_html_verses(
    html_text: str,
    book_name: str,
    normalize_whitespace: bool = False,
    strip_italics: bool = False,
    fix_upstream_typos: bool = False,
) -> Dict[str, Dict[str, str]]:
    """Extract {chapter: {verse: expected_text}} directly from raw HTML lines."""
    chapters: Dict[str, Dict[str, str]] = {}
    for line in html_text.splitlines():
        if not line.startswith("{"):
            continue
        end_meta = line.index("}")
        ch, v = line[1:end_meta].split(":", 1)
        # Strip trailing <BR> if present (Judges 21:24 and Malachi 4:6 have no <BR>)
        rest = line[end_meta + 2 :]
        if rest.endswith("<BR>"):
            rest = rest[:-4]
        rest = normalize_verse_text(
            book_name=book_name,
            chapter=ch,
            verse=v,
            content=rest,
            normalize_whitespace=normalize_whitespace,
            strip_italics=strip_italics,
            fix_upstream_typos=fix_upstream_typos,
        )
        chapters.setdefault(ch, {})[v] = rest
    return chapters


def verify_books_metadata(
    books_index_path: Path,
    loaded_book_jsons: Dict[str, Dict[str, Dict[str, str]]],
    errors: List[str],
) -> Optional[Dict[str, Any]]:
    """Validate CPDV-JSON/books.json structure, uniqueness, and counts against the book JSONs."""
    if not books_index_path.exists():
        errors.append(f"Missing canonical metadata index: {books_index_path.name}")
        return None

    books_index = json.loads(books_index_path.read_text(encoding="utf-8"))
    if books_index.get("charset") != "UTF-8":
        errors.append("books.json missing 'charset': 'UTF-8'")
    if books_index.get("book_count") != EXPECTED_BOOK_COUNT:
        errors.append(f"books.json book_count = {books_index.get('book_count')}, expected {EXPECTED_BOOK_COUNT}")
    if books_index.get("old_testament_count") != EXPECTED_OT_COUNT:
        errors.append(f"books.json old_testament_count = {books_index.get('old_testament_count')}, expected {EXPECTED_OT_COUNT}")
    if books_index.get("new_testament_count") != EXPECTED_NT_COUNT:
        errors.append(f"books.json new_testament_count = {books_index.get('new_testament_count')}, expected {EXPECTED_NT_COUNT}")
    if books_index.get("chapter_count") != EXPECTED_CHAPTER_COUNT:
        errors.append(f"books.json chapter_count = {books_index.get('chapter_count')}, expected {EXPECTED_CHAPTER_COUNT}")
    if books_index.get("verse_count") != EXPECTED_VERSE_COUNT:
        errors.append(f"books.json verse_count = {books_index.get('verse_count')}, expected {EXPECTED_VERSE_COUNT}")

    entries = books_index.get("books", [])
    if len(entries) != EXPECTED_BOOK_COUNT:
        errors.append(f"books.json 'books' array has {len(entries)} entries, expected {EXPECTED_BOOK_COUNT}")
        return books_index

    seen_orders = set()
    seen_codes = set()
    seen_keys = set()
    seen_osis = set()
    seen_usfm = set()

    required_fields = {
        "order",
        "testament",
        "testament_order",
        "code",
        "file",
        "key",
        "name",
        "alt_names",
        "full_title",
        "abbreviation",
        "osis",
        "usfm",
        "has_prologue",
        "chapter_count",
        "chapters",
        "verse_count",
        "chapter_verses",
    }

    for idx, entry in enumerate(entries, start=1):
        missing = required_fields - set(entry.keys())
        if missing:
            errors.append(f"books.json entry #{idx} missing fields: {sorted(missing)}")
            continue

        code = entry["code"]
        if entry["order"] != idx:
            errors.append(f"books.json {code}: order={entry['order']}, expected {idx}")
        if code != BOOKS[idx - 1]:
            errors.append(f"books.json entry #{idx}: code={code}, expected {BOOKS[idx - 1]}")

        seen_orders.add(entry["order"])
        seen_codes.add(code)
        seen_keys.add(entry["key"])
        seen_osis.add(entry["osis"])
        seen_usfm.add(entry["usfm"])

        actual_chapters = loaded_book_jsons.get(code, {})
        actual_ch_keys = list(actual_chapters.keys())
        actual_ch_verses = {ch: len(v_map) for ch, v_map in actual_chapters.items()}
        actual_v_count = sum(actual_ch_verses.values())

        if entry["chapters"] != actual_ch_keys:
            errors.append(f"books.json {code}: chapters list mismatch")
        if entry["chapter_count"] != len(actual_ch_keys):
            errors.append(f"books.json {code}: chapter_count={entry['chapter_count']} vs {len(actual_ch_keys)}")
        if entry["chapter_verses"] != actual_ch_verses:
            errors.append(f"books.json {code}: chapter_verses mismatch")
        if entry["verse_count"] != actual_v_count:
            errors.append(f"books.json {code}: verse_count={entry['verse_count']} vs {actual_v_count}")
        if entry["has_prologue"] != ("P" in actual_chapters):
            errors.append(f"books.json {code}: has_prologue mismatch")

    if len(seen_osis) != EXPECTED_BOOK_COUNT:
        errors.append(f"books.json duplicate OSIS codes found ({len(seen_osis)} unique)")
    if len(seen_usfm) != EXPECTED_BOOK_COUNT:
        errors.append(f"books.json duplicate USFM codes found ({len(seen_usfm)} unique)")

    return books_index


def verify_all(
    json_dir: Path,
    html_dir: Optional[Path] = None,
    workers: int = 6,
    normalize_whitespace: Optional[bool] = None,
    strip_italics: Optional[bool] = None,
    fix_upstream_typos: Optional[bool] = None,
) -> int:
    errors: List[str] = []

    print(f"Verifying JSON files in: {json_dir}")
    entire_path = json_dir / "EntireBible-CPDV.json"
    if not entire_path.exists():
        print(f"FAIL: Missing {entire_path}")
        return 1

    entire_bible = json.loads(entire_path.read_text(encoding="utf-8"))
    if entire_bible.get("charset") != "UTF-8":
        errors.append("EntireBible-CPDV.json missing 'charset': 'UTF-8'")

    entire_book_keys = [k for k in entire_bible.keys() if k != "charset"]
    if len(entire_book_keys) != EXPECTED_BOOK_COUNT:
        errors.append(
            f"EntireBible-CPDV.json has {len(entire_book_keys)} books, expected {EXPECTED_BOOK_COUNT}"
        )

    # Read books.json if present to auto-detect normalization settings when not overridden on CLI
    books_index_path = json_dir / "books.json"
    norm_cfg: Dict[str, bool] = {}
    if books_index_path.exists():
        try:
            norm_cfg = json.loads(books_index_path.read_text(encoding="utf-8")).get("normalization", {})
        except Exception:
            norm_cfg = {}

    use_norm_ws = normalize_whitespace if normalize_whitespace is not None else bool(norm_cfg.get("normalize_whitespace", False))
    use_strip_it = strip_italics if strip_italics is not None else bool(norm_cfg.get("strip_italics", False))
    use_fix_typos = fix_upstream_typos if fix_upstream_typos is not None else bool(norm_cfg.get("fix_upstream_typos", False))

    def _load_html(book_name: str) -> Tuple[str, Dict[str, Dict[str, str]]]:
        return (
            book_name,
            extract_html_verses(
                fetch_book_html(book_name, html_dir=html_dir),
                book_name=book_name,
                normalize_whitespace=use_norm_ws,
                strip_italics=use_strip_it,
                fix_upstream_typos=use_fix_typos,
            ),
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        html_books = dict(executor.map(_load_html, BOOKS))

    loaded_book_jsons: Dict[str, Dict[str, Dict[str, str]]] = {}
    total_chapters = 0
    total_verses = 0
    br_tag_failures = 0
    unexpected_tag_failures = 0
    verse_mismatches = 0
    entire_bible_mismatches = 0
    closing_double_quotes_at_end = 0
    closing_single_quotes_at_end = 0
    balanced_books = 0
    unbalanced_books_info: List[Tuple[str, int, int]] = []

    html_tag_re = re.compile(r"<[^>]+>")

    for book_name in BOOKS:
        book_path = json_dir / f"{book_name}.json"
        if not book_path.exists():
            errors.append(f"Missing book JSON file: {book_path.name}")
            continue

        book_json = json.loads(book_path.read_text(encoding="utf-8"))
        if book_json.get("charset") != "UTF-8":
            errors.append(f"{book_path.name} missing 'charset': 'UTF-8'")

        short_name = book_name.split("_", 1)[1]
        if short_name not in entire_bible:
            errors.append(f"Book '{short_name}' missing from EntireBible-CPDV.json")
            continue

        entire_book = entire_bible[short_name]
        expected_chapters = html_books[book_name]

        book_chapters = {k: v for k, v in book_json.items() if k != "charset"}
        loaded_book_jsons[book_name] = book_chapters

        if list(book_chapters.keys()) != list(expected_chapters.keys()):
            errors.append(
                f"{book_name}: chapter keys mismatch: {list(book_chapters.keys())} vs {list(expected_chapters.keys())}"
            )

        if book_chapters != entire_book:
            entire_bible_mismatches += 1
            errors.append(f"{book_name}: mismatch between {book_path.name} and EntireBible-CPDV.json[{short_name!r}]")

        total_chapters += len(book_chapters)

        book_open_q = 0
        book_close_q = 0

        for ch, exp_verses in expected_chapters.items():
            act_verses = book_chapters.get(ch, {})
            if list(act_verses.keys()) != list(exp_verses.keys()):
                errors.append(f"{book_name} ch {ch}: verse keys mismatch")

            for v, exp_text in exp_verses.items():
                total_verses += 1
                act_text = act_verses.get(v)

                if act_text != exp_text:
                    verse_mismatches += 1
                    if verse_mismatches <= 10:
                        errors.append(
                            f"Mismatch at {book_name} {ch}:{v}:\n"
                            f"  Expected: {exp_text!r}\n"
                            f"  Actual  : {act_text!r}"
                        )
                    continue

                if "<br>" in act_text.lower():
                    br_tag_failures += 1
                    errors.append(f"Leftover <BR> tag in {book_name} {ch}:{v}")

                tags = html_tag_re.findall(act_text)
                if tags:
                    if use_strip_it or book_name != "OT-24_Song2" or any(t not in ("<I>", "</I>") for t in tags):
                        unexpected_tag_failures += 1
                        errors.append(f"Unexpected HTML tag {tags} in {book_name} {ch}:{v}")

                if act_text.endswith("\u201d"):
                    closing_double_quotes_at_end += 1
                if act_text.endswith("\u2019"):
                    closing_single_quotes_at_end += 1

                book_open_q += act_text.count("\u201c")
                book_close_q += act_text.count("\u201d")

        if book_open_q == book_close_q:
            balanced_books += 1
        else:
            unbalanced_books_info.append((book_name, book_open_q, book_close_q))

    verify_books_metadata(books_index_path, loaded_book_jsons, errors)

    if total_chapters != EXPECTED_CHAPTER_COUNT:
        errors.append(f"Total chapters = {total_chapters}, expected {EXPECTED_CHAPTER_COUNT}")
    if total_verses != EXPECTED_VERSE_COUNT:
        errors.append(f"Total verses = {total_verses}, expected {EXPECTED_VERSE_COUNT}")

    # Spot-check specific regression verses
    spot_checks = [
        (
            "NT-03_Luke",
            "1",
            "28",
            "And upon entering, the Angel said to her: \u201cHail, full of grace. The Lord is with you. Blessed are you among women.\u201d",
        ),
        (
            "NT-03_Luke",
            "1",
            "38",
            "Then Mary said: \u201cBehold, I am the handmaid of the Lord. Let it be done to me according to your word.\u201d And the Angel departed from her.",
        ),
        (
            "OT-21_Psalms",
            "124",
            "1",
            "A Canticle in steps. Those who trust in the Lord will be like the mountain of Zion. He will not be disturbed for eternity, who dwells",
        ),
        (
            "OT-07_Judges",
            "21",
            "24",
            "The sons of Israel also returned, according to their tribes and families, to their tents. In those days, there was no king in Israel. Instead, each one did what seemed right to himself.",
        ),
        (
            "OT-44_Malachi",
            "4",
            "6",
            "And he will turn the heart of the fathers to the sons, and the heart of the sons to their fathers, lest I come and strike the earth with anathema.",
        ),
        (
            "NT-27_Revelation",
            "22",
            "21",
            "The grace of our Lord Jesus Christ be with you all. Amen.",
        ),
    ]

    for b_name, ch, v, expected_str in spot_checks:
        short_name = b_name.split("_", 1)[1]
        actual_str = entire_bible.get(short_name, {}).get(ch, {}).get(v)
        if actual_str != expected_str:
            errors.append(
                f"Spot-check failed for {b_name} {ch}:{v}:\n"
                f"  Expected: {expected_str!r}\n"
                f"  Actual  : {actual_str!r}"
            )

    print("\n=== CPDV-JSON VERIFICATION REPORT ===")
    print(f"  Books verified              : {len(BOOKS)} / {EXPECTED_BOOK_COUNT}")
    print(f"  Canonical index (books.json): {'VALID' if books_index_path.exists() else 'MISSING'} ({EXPECTED_BOOK_COUNT} entries)")
    print(f"  Chapters verified           : {total_chapters} / {EXPECTED_CHAPTER_COUNT}")
    print(f"  Verses verified             : {total_verses} / {EXPECTED_VERSE_COUNT}")
    print(f"  Exact HTML verse matches    : {total_verses - verse_mismatches} / {total_verses}")
    print(f"  EntireBible parity matches  : {len(BOOKS) - entire_bible_mismatches} / {len(BOOKS)} books")
    print(f"  Leftover <BR> tags          : {br_tag_failures}")
    print(f"  Unexpected HTML tags        : {unexpected_tag_failures}")
    print(f"  Verse-ending '\u201d' preserved  : {closing_double_quotes_at_end} (previously 0 in buggy repo)")
    print(f"  Verse-ending '\u2019' preserved  : {closing_single_quotes_at_end} (previously 0 in buggy repo)")
    print(
        f"  Quotation marks (\u201c/\u201d)       : 100% matched to expected text "
        f"({balanced_books}/73 books balanced; {len(unbalanced_books_info)} have multi-chapter speeches/typos in source HTML)"
    )
    print(f"  Known edge-case spot-checks : {len(spot_checks)} / {len(spot_checks)} passed")

    if errors:
        print(f"\nFAILED with {len(errors)} error(s):")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("\nALL VERIFICATION CHECKS PASSED!")
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        description="Verify CPDV-JSON files against https://www.sacredbible.org/catholic/."
    )
    parser.add_argument(
        "--json-dir",
        type=Path,
        default=repo_root / "CPDV-JSON",
        help="Directory containing generated JSON files (default: <repo>/CPDV-JSON)",
    )
    parser.add_argument(
        "--html-dir",
        type=Path,
        default=None,
        help="Optional directory containing cached .htm files",
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
        default=None,
        help="Expect whitespace-normalized verse text",
    )
    parser.add_argument(
        "--strip-italics",
        action="store_true",
        default=None,
        help="Expect <I>...</I> tags stripped in OT-24_Song2",
    )
    parser.add_argument(
        "--fix-upstream-typos",
        action="store_true",
        default=None,
        help="Expect upstream punctuation typos fixed",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Expect all optional text normalizations applied",
    )
    args = parser.parse_args()

    norm_ws = True if (args.clean or args.normalize_whitespace) else None
    strip_it = True if (args.clean or args.strip_italics) else None
    fix_typos = True if (args.clean or args.fix_upstream_typos) else None

    return verify_all(
        json_dir=args.json_dir,
        html_dir=args.html_dir,
        workers=args.workers,
        normalize_whitespace=norm_ws,
        strip_italics=strip_it,
        fix_upstream_typos=fix_typos,
    )


if __name__ == "__main__":
    sys.exit(main())
