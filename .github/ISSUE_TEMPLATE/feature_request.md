---
name: Feature request
about: Propose a metadata enhancement, normalization option, or tooling improvement
title: ''
labels: 'enhancement'
assignees: ''
---

### 1. Problem & Context
A concise explanation of the use case and why this enhancement improves the CPDV-JSON repository for downstream projects.

### 2. Technical Scope & Affected Files
- `src/encode_cpdv.py`
- `src/verify_cpdv.py`
- `CPDV-JSON/books.json`
- `README.md`

### 3. Acceptance Criteria
- [ ] Implement enhancement while preserving backward compatibility for existing `CPDV-JSON/*.json` consumers.
- [ ] Add verification coverage in `src/verify_cpdv.py`.
- [ ] Update `README.md` and `AGENTS.md` documentation.
