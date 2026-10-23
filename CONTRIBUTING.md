# Contributing to CPDV-JSON

Thank you for your interest in contributing to the **Catholic Public Domain Version (CPDV) Bible — JSON Edition**! Because this repository serves as a canonical data source for downstream Catholic applications and publications (such as **PrayTheRosary**) and is maintained by both human developers and autonomous AI agents, our contribution workflow prioritizes strict textual verification and backward compatibility.

## 1. Finding Something to Work On
Check the [Issues](https://github.com/draino7n7/cpdv/issues) tab for tasks labeled `help wanted` or `good first issue`, or open an issue if you notice an upstream errata update on [SacredBible.org](https://www.sacredbible.org/errata.htm) that should be synced.

## 2. Setting Up the Environment
This project uses zero third-party dependencies so it can be run anywhere with a standard Python 3 installation:
1. Ensure **Python 3.8+** is installed (`python --version`).
2. Clone the repository:
   ```bash
   git clone https://github.com/draino7n7/cpdv.git
   cd cpdv
   ```
3. Run the verification suite to confirm your environment is working:
   ```bash
   python src/verify_cpdv.py
   ```

## 3. Regenerating & Verifying the JSON Corpus
Never hand-edit the generated JSON files in `CPDV-JSON/` directly. Instead, update [`src/encode_cpdv.py`](src/encode_cpdv.py) (and [`src/CPDVJSONEncoder.groovy`](src/CPDVJSONEncoder.groovy) if applicable), regenerate the corpus, and run the automated verifier:

```bash
python src/encode_cpdv.py
python src/verify_cpdv.py
```

## 4. Pull Request Guidelines
When submitting a Pull Request, please ensure:
*   **Verification Passes:** `python src/verify_cpdv.py` completes with `ALL VERIFICATION CHECKS PASSED!` (73 books, 1,335 chapters, 35,839 verses verified).
*   **Backward Compatibility:** Do not rename existing file paths (`CPDV-JSON/OT-01_Genesis.json`, `CPDV-JSON/EntireBible-CPDV.json`) or top-level book keys in `EntireBible-CPDV.json` (such as `"Song2"` or `"1-Samuel"`), as downstream applications depend on them. Add new metadata fields to [`CPDV-JSON/books.json`](CPDV-JSON/books.json) instead.
*   **Public Domain Dedication:** By contributing to this repository, you agree that all contributions are dedicated to the public domain under [The Unlicense](LICENSE) and [SacredBible.org's public domain terms](https://www.sacredbible.org/catholic/version.htm).
*   **Atomic Commits:** Keep commits focused on a single logical change.
