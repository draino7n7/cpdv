---
name: Bug report
about: Report a text encoding defect, missing upstream errata, or script bug
title: ''
labels: 'bug'
assignees: ''
---

### 1. Problem & Context
A concise explanation of the issue (e.g., specific book/chapter/verse discrepancy against SacredBible.org, or script error).

**Affected Book / Chapter / Verse (if applicable):**
- Book: 
- Chapter & Verse: 

**Observed Text / Behavior:**
<!-- What is currently in CPDV-JSON or happening when running the script -->

**Expected Text / Behavior:**
<!-- What appears on https://www.sacredbible.org/catholic/ or expected script behavior -->

### 2. Technical Scope & Affected Files
- `src/encode_cpdv.py`
- `src/verify_cpdv.py`
- `CPDV-JSON/<book>.json`

### 3. Acceptance Criteria
- [ ] Fix encoder/verifier logic in `src/`.
- [ ] Regenerate `CPDV-JSON/*.json`, `CPDV-JSON/EntireBible-CPDV.json`, and `CPDV-JSON/books.json`.
- [ ] `python src/verify_cpdv.py` passes with 0 errors.
