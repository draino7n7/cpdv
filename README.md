# Catholic Public Domain Version (CPDV) Bible — JSON Edition

[![Verify CPDV JSON Corpus](https://github.com/draino7n7/cpdv/actions/workflows/verify.yml/badge.svg)](https://github.com/draino7n7/cpdv/actions/workflows/verify.yml)
[![License: Public Domain](https://img.shields.io/badge/License-Public_Domain-brightgreen.svg)](LICENSE)

Complete, verified **UTF-8 JSON** encoding of all **73 books** of the **Catholic Public Domain Version (CPDV)** of the Holy Bible (*2009 Original Edition*, translated and edited by **Ronald L. Conte Jr.** from the Sixtus V and Clement VIII Latin Vulgate, using the Challoner Douay-Rheims as a guide).

- **Source Text:** [https://www.sacredbible.org/catholic/](https://www.sacredbible.org/catholic/)
- **Canon:** 73 Books (46 Old Testament + 27 New Testament, following the Council of Trent / Vulgate order)
- **Scope:** 1,335 Chapters (including Prologues in Sirach and Lamentations) · 35,839 Verses
- **Copyright Status:** **100% Public Domain** (both the biblical text and all JSON encodings, metadata, and scripts in this repository)

---

## Why This Repository Exists (2026 Restoration & Bug Fix)

This repository was originally cloned from the 2012 Bitbucket repository ([`sbruno/cpdv-json-encoder`](https://bitbucket.org/sbruno/cpdv-json-encoder/src/master/)) linked on the front page of SacredBible.org.

During an audit of the 2012 JSON files, a critical off-by-one bug was discovered in [`src/CPDVJSONEncoder.groovy`](src/CPDVJSONEncoder.groovy):

```groovy
it = it.replaceAll("<BR>", "")
def endIdx = it.length()-1;
def content = it.substring(strtIdx, endIdx)
```

Because `it.length() - 1` was calculated *after* stripping `"<BR>"`, **every single verse across all 73 books (all 35,839 verses) in the 2012 repository had its final character chopped off**:
- **29,800+ verses** were missing their final punctuation mark (`.`, `,`, `?`, `:`, `;`, `!`, `)`), e.g., Luke 1:38 ended with `"And the Angel departed from her"` without a period.
- **5,017 verses** were missing their closing quotation mark (`”` or `’`), leaving thousands of unclosed quotes across the Bible (e.g., Luke 1:28).
- **93 enjambed verses** (sentences wrapping into the next verse without punctuation) had the **last letter of their final word cut off** (e.g., Psalm 124:1 ended with `"who dwell"` instead of `"who dwells"`, Genesis 24:21 ended with `"or no"` instead of `"or not"`, and Numbers 15:11 ended with `"So shall you d"` instead of `"So shall you do"`).

### What Has Been Fixed & Modernized
1. **100% Intact Verses:** Fixed the off-by-one bug and regenerated all 73 individual book JSON files and [`CPDV-JSON/EntireBible-CPDV.json`](CPDV-JSON/EntireBible-CPDV.json) directly from [SacredBible.org](https://www.sacredbible.org/catholic/).
2. **Synced with Latest Upstream Errata:** Regenerating from the live site incorporates **156 verse errata/typo fixes** made by Ronald L. Conte Jr. on SacredBible.org between 2012 and 2025.
3. **Modern Zero-Dependency Python 3 Encoder ([`src/encode_cpdv.py`](src/encode_cpdv.py)):** Replaces the need for a legacy 2012 Groovy environment, handles mixed CRLF/LF line endings (such as `NT-27_Revelation.htm`), and supports optional text-normalization flags.
4. **Canonical Book Metadata Index ([`CPDV-JSON/books.json`](CPDV-JSON/books.json)):** Provides standard book titles, Catholic/OSIS/USFM abbreviations, alternate names (e.g., *Sirach* / *Ecclesiasticus*, *Song of Songs* / *Canticle of Canticles*), and per-chapter verse counts.
5. **Automated Verification Suite ([`src/verify_cpdv.py`](src/verify_cpdv.py)):** Validates all 73 books, 1,335 chapters, and 35,839 verses character-for-character against the source HTML.

---

## Repository Structure

```text
cpdv/
├── CPDV-JSON/
│   ├── OT-01_Genesis.json          # 46 Old Testament book JSON files (OT-01 through OT-46)
│   ├── ...
│   ├── NT-01_Matthew.json          # 27 New Testament book JSON files (NT-01 through NT-27)
│   ├── ...
│   ├── EntireBible-CPDV.json       # Complete 73-book CPDV Bible in a single JSON file
│   ├── books.json                  # Canonical metadata index (names, abbreviations, counts)
│   └── README                      # Attribution notice for the JSON directory
├── src/
│   ├── encode_cpdv.py              # Modern Python 3 encoder (zero third-party dependencies)
│   ├── verify_cpdv.py              # Automated verification suite against SacredBible.org
│   └── CPDVJSONEncoder.groovy      # Original Groovy encoder (fixed for UTF-8 and LF/CRLF)
├── .github/                        # GitHub Actions CI workflows & Issue/PR templates
├── AGENTS.md                       # Instructions and architectural guide for AI coding agents
├── CONTRIBUTING.md                 # Contribution guidelines
├── CODE_OF_CONDUCT.md              # Contributor Covenant Code of Conduct
├── SECURITY.md                     # Security reporting policy
├── SUPPORT.md                      # Support and usage help
└── LICENSE                         # Public Domain dedication (The Unlicense)
```

---

## JSON Schema & Usage

### 1. Individual Book Files (`CPDV-JSON/<BookCode>.json`)
Each of the 73 book files maps chapter strings (`"1"`, `"2"`, etc.) to an object of verse strings (`"1"`, `"2"`, etc.), with a trailing `"charset": "UTF-8"` property:

```json
{
    "1": {
        "1": "In the beginning, God created heaven and earth.",
        "2": "But the earth was empty and unoccupied, and darknesses were over the face of the abyss; and so the Spirit of God was brought over the waters.",
        "3": "And God said, “Let there be light.” And light became."
    },
    "charset": "UTF-8"
}
```

> [!NOTE]
> **Prologue Chapters (`"P"`):** Two books include a Prologue before Chapter 1, keyed as `"P"`:
> - **Sirach** ([`CPDV-JSON/OT-26_Sirach.json`](CPDV-JSON/OT-26_Sirach.json)): Chapter `"P"` has verses `"1"` through `"9"`, followed by Chapters `"1"` through `"51"`.
> - **Lamentations** ([`CPDV-JSON/OT-29_Lamentations.json`](CPDV-JSON/OT-29_Lamentations.json)): Chapter `"P"` has verse `"1"`, followed by Chapters `"1"` through `"5"`.

### 2. Complete Bible File ([`CPDV-JSON/EntireBible-CPDV.json`](CPDV-JSON/EntireBible-CPDV.json))
Contains a top-level `"charset": "UTF-8"` key followed by all 73 books keyed by their filename suffix after `_` (e.g., `"Genesis"`, `"1-Samuel"`, `"Song2"`, `"Luke"`, `"Revelation"`):

```json
{
    "charset": "UTF-8",
    "Genesis": {
        "1": {
            "1": "In the beginning, God created heaven and earth."
        }
    }
}
```

### 3. Canonical Metadata Index ([`CPDV-JSON/books.json`](CPDV-JSON/books.json))
Because [`EntireBible-CPDV.json`](CPDV-JSON/EntireBible-CPDV.json) retains the legacy 2012 keys for backward compatibility (such as `"Song2"` for Song of Songs and hyphenated keys like `"1-Samuel"`), [`CPDV-JSON/books.json`](CPDV-JSON/books.json) provides a rich lookup manifest for applications:

```json
{
    "order": 24,
    "testament": "OT",
    "testament_order": 24,
    "code": "OT-24_Song2",
    "file": "OT-24_Song2.json",
    "key": "Song2",
    "name": "Song of Songs",
    "alt_names": ["Canticle of Canticles", "Song of Solomon"],
    "full_title": "The Song of Solomon",
    "abbreviation": "Sg",
    "osis": "Song",
    "usfm": "SNG",
    "has_prologue": false,
    "chapter_count": 8,
    "chapters": ["1", "2", "3", "4", "5", "6", "7", "8"],
    "verse_count": 116,
    "chapter_verses": {
        "1": 21, "2": 19, "3": 11, "4": 17, "5": 17, "6": 12, "7": 13, "8": 14
    }
}
```

---

## Regenerating & Verifying the JSON Corpus

Requires **Python 3.8+** (uses only the Python standard library; zero `pip` dependencies).

### Regenerate All JSON Files from SacredBible.org
```bash
python src/encode_cpdv.py
```

#### Optional Text Normalization Flags
By default, [`src/encode_cpdv.py`](src/encode_cpdv.py) preserves strict character-for-character equality with the raw HTML on SacredBible.org. For downstream applications (such as mobile apps or print/eBook typesetting) that prefer normalized text, optional flags are supported:

```bash
# Apply all text cleanups (whitespace normalization + strip <I> tags in Song2 + fix 1 Mac 14:49 quote typo)
python src/encode_cpdv.py --clean

# Or apply individual normalizations:
python src/encode_cpdv.py --normalize-whitespace   # Replace NBSP (\u00a0) with space, strip trailing spaces, collapse "  " -> " "
python src/encode_cpdv.py --strip-italics          # Strip the 55 <I>...</I> speaker tags in OT-24_Song2
python src/encode_cpdv.py --fix-upstream-typos     # Fix 1 Maccabees 14:49 trailing opening quote (’ “ -> ’ ”)

# Cache raw .htm files locally to avoid re-downloading on subsequent runs:
python src/encode_cpdv.py --html-dir .cache/html
```

### Run the Automated Verification Suite
```bash
python src/verify_cpdv.py
```
If you regenerated the corpus using normalization flags (`--clean`, etc.), pass the matching flags to `verify_cpdv.py` (or `verify_cpdv.py` will automatically detect normalization settings from `CPDV-JSON/books.json`).

---

## Complete 73-Book Reference

### Old Testament (46 Books)

| # | File Code | `EntireBible` Key | Book Name | Abbr | OSIS | USFM | Chapters | Verses |
|---:|:---|:---|:---|:---|:---|:---|---:|---:|
| 1 | `OT-01_Genesis` | `Genesis` | Genesis | Gn | Gen | GEN | 50 | 1,533 |
| 2 | `OT-02_Exodus` | `Exodus` | Exodus | Ex | Exod | EXO | 40 | 1,213 |
| 3 | `OT-03_Leviticus` | `Leviticus` | Leviticus | Lv | Lev | LEV | 27 | 859 |
| 4 | `OT-04_Numbers` | `Numbers` | Numbers | Nm | Num | NUM | 36 | 1,288 |
| 5 | `OT-05_Deuteronomy` | `Deuteronomy` | Deuteronomy | Dt | Deut | DEU | 34 | 959 |
| 6 | `OT-06_Joshua` | `Joshua` | Joshua | Jos | Josh | JOS | 24 | 658 |
| 7 | `OT-07_Judges` | `Judges` | Judges | Jgs | Judg | JDG | 21 | 618 |
| 8 | `OT-08_Ruth` | `Ruth` | Ruth | Ru | Ruth | RUT | 4 | 85 |
| 9 | `OT-09_1-Samuel` | `1-Samuel` | 1 Samuel | 1 Sm | 1Sam | 1SA | 31 | 811 |
| 10 | `OT-10_2-Samuel` | `2-Samuel` | 2 Samuel | 2 Sm | 2Sam | 2SA | 24 | 695 |
| 11 | `OT-11_1-Kings` | `1-Kings` | 1 Kings | 1 Kgs | 1Kgs | 1KI | 22 | 817 |
| 12 | `OT-12_2-Kings` | `2-Kings` | 2 Kings | 2 Kgs | 2Kgs | 2KI | 25 | 719 |
| 13 | `OT-13_1-Chronicles` | `1-Chronicles` | 1 Chronicles | 1 Chr | 1Chr | 1CH | 29 | 942 |
| 14 | `OT-14_2-Chronicles` | `2-Chronicles` | 2 Chronicles | 2 Chr | 2Chr | 2CH | 36 | 822 |
| 15 | `OT-15_Ezra` | `Ezra` | Ezra | Ezr | Ezra | EZR | 10 | 280 |
| 16 | `OT-16_Nehemiah` | `Nehemiah` | Nehemiah | Neh | Neh | NEH | 13 | 406 |
| 17 | `OT-17_Tobit` | `Tobit` | Tobit | Tb | Tob | TOB | 14 | 295 |
| 18 | `OT-18_Judith` | `Judith` | Judith | Jdt | Jdt | JDT | 16 | 375 |
| 19 | `OT-19_Esther` | `Esther` | Esther | Est | Esth | EST | 16 | 272 |
| 20 | `OT-20_Job` | `Job` | Job | Jb | Job | JOB | 42 | 1,070 |
| 21 | `OT-21_Psalms` | `Psalms` | Psalms | Ps | Ps | PSA | 150 | 2,526 |
| 22 | `OT-22_Proverbs` | `Proverbs` | Proverbs | Prv | Prov | PRO | 31 | 915 |
| 23 | `OT-23_Ecclesiastes` | `Ecclesiastes` | Ecclesiastes | Eccl | Eccl | ECC | 12 | 222 |
| 24 | `OT-24_Song2` | `Song2` | Song of Songs | Sg | Song | SNG | 8 | 116 |
| 25 | `OT-25_Wisdom` | `Wisdom` | Wisdom | Wis | Wis | WIS | 19 | 436 |
| 26 | `OT-26_Sirach` | `Sirach` | Sirach (Ecclesiasticus) | Sir | Sir | SIR | 52 (`P` + 51) | 1,613 |
| 27 | `OT-27_Isaiah` | `Isaiah` | Isaiah | Is | Isa | ISA | 66 | 1,292 |
| 28 | `OT-28_Jeremiah` | `Jeremiah` | Jeremiah | Jer | Jer | JER | 52 | 1,364 |
| 29 | `OT-29_Lamentations` | `Lamentations` | Lamentations | Lam | Lam | LAM | 6 (`P` + 5) | 155 |
| 30 | `OT-30_Baruch` | `Baruch` | Baruch | Bar | Bar | BAR | 6 | 213 |
| 31 | `OT-31_Ezekiel` | `Ezekiel` | Ezekiel | Ez | Ezek | EZK | 48 | 1,273 |
| 32 | `OT-32_Daniel` | `Daniel` | Daniel | Dn | Dan | DAN | 14 | 531 |
| 33 | `OT-33_Hosea` | `Hosea` | Hosea | Hos | Hos | HOS | 14 | 197 |
| 34 | `OT-34_Joel` | `Joel` | Joel | Jl | Joel | JOL | 3 | 73 |
| 35 | `OT-35_Amos` | `Amos` | Amos | Am | Amos | AMO | 9 | 146 |
| 36 | `OT-36_Obadiah` | `Obadiah` | Obadiah | Ob | Obad | OBA | 1 | 21 |
| 37 | `OT-37_Jonah` | `Jonah` | Jonah | Jon | Jonah | JON | 4 | 48 |
| 38 | `OT-38_Micah` | `Micah` | Micah | Mi | Mic | MIC | 7 | 105 |
| 39 | `OT-39_Nahum` | `Nahum` | Nahum | Na | Nah | NAM | 3 | 47 |
| 40 | `OT-40_Habakkuk` | `Habakkuk` | Habakkuk | Hb | Hab | HAB | 3 | 56 |
| 41 | `OT-41_Zephaniah` | `Zephaniah` | Zephaniah | Zep | Zeph | ZEP | 3 | 53 |
| 42 | `OT-42_Haggai` | `Haggai` | Haggai | Hg | Hag | HAG | 2 | 38 |
| 43 | `OT-43_Zechariah` | `Zechariah` | Zechariah | Zec | Zech | ZEC | 14 | 211 |
| 44 | `OT-44_Malachi` | `Malachi` | Malachi | Mal | Mal | MAL | 4 | 55 |
| 45 | `OT-45_1-Maccabees` | `1-Maccabees` | 1 Maccabees | 1 Mc | 1Macc | 1MA | 16 | 924 |
| 46 | `OT-46_2-Maccabees` | `2-Maccabees` | 2 Maccabees | 2 Mc | 2Macc | 2MA | 15 | 557 |

### New Testament (27 Books)

| # | File Code | `EntireBible` Key | Book Name | Abbr | OSIS | USFM | Chapters | Verses |
|---:|:---|:---|:---|:---|:---|:---|---:|---:|
| 47 | `NT-01_Matthew` | `Matthew` | Matthew | Mt | Matt | MAT | 28 | 1,071 |
| 48 | `NT-02_Mark` | `Mark` | Mark | Mk | Mark | MRK | 16 | 678 |
| 49 | `NT-03_Luke` | `Luke` | Luke | Lk | Luke | LUK | 24 | 1,151 |
| 50 | `NT-04_John` | `John` | John | Jn | John | JHN | 21 | 879 |
| 51 | `NT-05_Acts` | `Acts` | Acts of the Apostles | Acts | Acts | ACT | 28 | 1,006 |
| 52 | `NT-06_Romans` | `Romans` | Romans | Rom | Rom | ROM | 16 | 433 |
| 53 | `NT-07_1-Corinthians` | `1-Corinthians` | 1 Corinthians | 1 Cor | 1Cor | 1CO | 16 | 437 |
| 54 | `NT-08_2-Corinthians` | `2-Corinthians` | 2 Corinthians | 2 Cor | 2Cor | 2CO | 13 | 256 |
| 55 | `NT-09_Galatians` | `Galatians` | Galatians | Gal | Gal | GAL | 6 | 149 |
| 56 | `NT-10_Ephesians` | `Ephesians` | Ephesians | Eph | Eph | EPH | 6 | 155 |
| 57 | `NT-11_Philippians` | `Philippians` | Philippians | Phil | Phil | PHP | 4 | 104 |
| 58 | `NT-12_Colossians` | `Colossians` | Colossians | Col | Col | COL | 4 | 95 |
| 59 | `NT-13_1-Thessalonians` | `1-Thessalonians` | 1 Thessalonians | 1 Thes | 1Thess | 1TH | 5 | 89 |
| 60 | `NT-14_2-Thessalonians` | `2-Thessalonians` | 2 Thessalonians | 2 Thes | 2Thess | 2TH | 3 | 46 |
| 61 | `NT-15_1-Timothy` | `1-Timothy` | 1 Timothy | 1 Tm | 1Tim | 1TI | 6 | 113 |
| 62 | `NT-16_2-Timothy` | `2-Timothy` | 2 Timothy | 2 Tm | 2Tim | 2TI | 4 | 83 |
| 63 | `NT-17_Titus` | `Titus` | Titus | Ti | Titus | TIT | 3 | 46 |
| 64 | `NT-18_Philemon` | `Philemon` | Philemon | Phlm | Phlm | PHM | 1 | 25 |
| 65 | `NT-19_Hebrews` | `Hebrews` | Hebrews | Heb | Heb | HEB | 13 | 303 |
| 66 | `NT-20_James` | `James` | James | Jas | Jas | JAS | 5 | 108 |
| 67 | `NT-21_1-Peter` | `1-Peter` | 1 Peter | 1 Pt | 1Pet | 1PE | 5 | 105 |
| 68 | `NT-22_2-Peter` | `2-Peter` | 2 Peter | 2 Pt | 2Pet | 2PE | 3 | 61 |
| 69 | `NT-23_1-John` | `1-John` | 1 John | 1 Jn | 1John | 1JN | 5 | 105 |
| 70 | `NT-24_2-John` | `2-John` | 2 John | 2 Jn | 2John | 2JN | 1 | 13 |
| 71 | `NT-25_3-John` | `3-John` | 3 John | 3 Jn | 3John | 3JN | 1 | 14 |
| 72 | `NT-26_Jude` | `Jude` | Jude | Jude | Jude | JUD | 1 | 25 |
| 73 | `NT-27_Revelation` | `Revelation` | Revelation | Rv | Rev | REV | 22 | 403 |

---

## License & Public Domain Dedication

In accordance with the public domain terms of [SacredBible.org](https://www.sacredbible.org/catholic/version.htm):
- **The Catholic Public Domain Version (CPDV)** of the Sacred Bible (translated and edited by Ronald L. Conte Jr.) is in the **Public Domain** and must remain free of any copyright restriction.
- All JSON files, metadata indices, and encoding/verification scripts in this repository are likewise dedicated to the **Public Domain** under [The Unlicense](LICENSE).
