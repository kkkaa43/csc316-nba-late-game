# Data status

The CSVs in this folder are **real** aggregates built from SportsDataverse / hoopR ESPN NBA play-by-play for the 2024–25 regular season (1,231 games) by `scripts/build_data.py` on 2026-11-20. See `metadata.json` for row counts, definitions, and the source file's SHA-256.

To rebuild: `python scripts/build_data.py --season 2025`. `scripts/make_demo.py` still exists but only generates illustrative placeholder values; do not use its output for findings.
