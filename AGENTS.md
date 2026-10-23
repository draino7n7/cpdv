# AI Agent Guide (`AGENTS.md`)

This document serves as the authoritative guide for autonomous AI coding agents working in the `cpdv` repository. Any agent modifying scripts, regenerating JSON data, or updating documentation MUST follow these directives.

---

## 1. Repository Purpose & Invariants

This repository maintains the canonical UTF-8 JSON encoding of the **Catholic Public Domain Version (CPDV)** of the Holy Bible (2009 Original Edition by Ronald L. Conte Jr.), fetched from `https://www.sacredbible.org/catholic/`.

### Strict Invariants (DO NOT BREAK)
1. **73 Canonical Books:** 46 Old Testament (`OT-01_Genesis` through `OT-46_2-Maccabees`) + 27 New Testament (`NT-01_Matthew` through `NT-27_Revelation`).
2. **1,335 Chapters & 35,839 Verses:**
   - Old Testament: 1,075 chapters (including chapter `"P"` Prologues in `OT-26_Sirach` and `OT-29_Lamentations`), 27,887 verses.
   - New Testament: 260 chapters, 7,952 verses.
3. **Backward-Compatible File Paths & Keys:**
   - Individual book files MUST remain at `CPDV-JSON/<BookCode>.json` with `"charset": "UTF-8"` as the final key.
   - [`CPDV-JSON/EntireBible-CPDV.json`](CPDV-JSON/EntireBible-CPDV.json) MUST keep `"charset": "UTF-8"` as the first key and use the legacy suffix after `_` as each book's key (e.g., `"Genesis"`, `"1-Samuel"`, `"Song2"`, `"Revelation"`).
   - [`CPDV-JSON/books.json`](CPDV-JSON/books.json) provides the canonical metadata index mapping legacy keys (`"Song2"`) to standard titles (`"Song of Songs"`), OSIS/USFM codes, and chapter/verse counts.
4. **Formatting Consistency:**
   - All JSON files MUST be serialized with `json.dumps(obj, indent=4, ensure_ascii=False)` in UTF-8 so diffs contain only actual text changes.
5. **Public Domain Mandate:**
   - Everything in this repository is 100% Public Domain ([`LICENSE`](LICENSE)). Never introduce third-party libraries or assets with restrictive licenses.

---

## 2. Upstream HTML Quirks on `sacredbible.org/catholic/`

When modifying [`src/encode_cpdv.py`](src/encode_cpdv.py), [`src/verify_cpdv.py`](src/verify_cpdv.py), or [`src/CPDVJSONEncoder.groovy`](src/CPDVJSONEncoder.groovy), agents MUST account for the following quirks in the upstream `.htm` files:

1. **Character Encoding (`windows-1252`):**
   - All 73 `.htm` files are encoded in `windows-1252` (`cp1252`), NOT UTF-8. Bytes `0x91`–`0x94` encode curly single/double quotation marks (`‘`, `’`, `“`, `”`) and `0xA0` encodes a non-breaking space (`\u00a0`). Always decode raw bytes with `.decode("windows-1252")` before writing UTF-8 JSON.
2. **Mixed Line Endings (`CRLF` vs. `LF`):**
   - 72 of the 73 `.htm` files use Windows `\r\n` (CRLF) line endings, but `NT-27_Revelation.htm` uses Unix `\n` (LF) line endings. Always split lines using `.splitlines()` (Python) or `split(/\r?\n/)` (Groovy) — NEVER `split("\r\n")`.
3. **Missing Trailing `<BR>` on 2 Verses:**
   - Most verse lines follow `{chapter:verse} verse text<BR>`, with no trailing space before `<BR>`.
   - However, `OT-07_Judges` `{21:24}` and `OT-44_Malachi` `{4:6}` omit the trailing `<BR>`. Never slice a fixed number of characters from the end of a line (`line[:-1]` or `it.length() - 1`); always strip `"<BR>"` explicitly and keep the full remaining substring after `{chapter:verse} `.
4. **Prologue Chapters (`"P"`):**
   - `OT-26_Sirach.htm` has `{P:1}`–`{P:9}` and `OT-29_Lamentations.htm` has `{P:1}`. Chapter keys are strings and must not be coerced to integers.
5. **Inline `<I>...</I>` Speaker Labels in `OT-24_Song2.htm`:**
   - 55 verses in `OT-24_Song2.htm` contain `<I>...</I>` tags around speaker labels (e.g., `<I>Bride:</I>`). In default mode, these are preserved for exact HTML parity; in `--strip-italics` or `--clean` mode, they are removed.
6. **HTTP ModSecurity `406 Not Acceptable` Quirk:**
   - `https://www.sacredbible.org/` rejects HTTP requests that send a bare `User-Agent: Mozilla/5.0` header with `HTTP 406 Not Acceptable`. Standard `urllib.request.urlopen(url)` (or a full browser User-Agent with standard `Accept` headers) succeeds.

---

## 3. Standard Agent Workflow for Updating the Corpus

Whenever you are asked to sync upstream errata from SacredBible.org or update the encoder/normalizer:

1. **Regenerate the JSON Corpus:**
   ```bash
   python src/encode_cpdv.py
   ```
   *(If testing normalization flags, run `python src/encode_cpdv.py --clean` or the specific flag requested.)*
2. **Run Automated Verification (Mandatory):**
   ```bash
   python src/verify_cpdv.py
   ```
   Do not consider any task complete until `python src/verify_cpdv.py` exits with code `0` (`ALL VERIFICATION CHECKS PASSED!`).
3. **Inspect `git diff`:**
   Verify that only expected lines changed and that JSON indentation (`indent=4`) and UTF-8 encoding remain intact.
