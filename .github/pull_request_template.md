## Summary & Context

Resolves #<issue_number>

<!-- Briefly describe the problem solved, upstream errata synced, or feature implemented. -->

## Key Changes & Technical Scope

<!-- Detail modifications by file or component with technical context -->
- `src/encode_cpdv.py`: <description of change>
- `src/verify_cpdv.py`: <description of change>
- `CPDV-JSON/`: <description of regenerated files>

## Automated Testing & Verification

- [ ] Regenerated JSON corpus via `python src/encode_cpdv.py`.
- [ ] Ran automated verification suite via `python src/verify_cpdv.py`.
- **Results:** `ALL VERIFICATION CHECKS PASSED! (73 books, 1335 chapters, 35839 verses)`

```text
<!-- Paste output from `python src/verify_cpdv.py` -->
```

## Documentation Coordination

- [ ] Updated `README.md` if CLI flags, schema, or book metadata changed.
- [ ] Updated `AGENTS.md` if new source HTML quirks or verification rules were added.
