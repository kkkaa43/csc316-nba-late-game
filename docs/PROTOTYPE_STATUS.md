# Prototype V1 requirement tracking

This file separates **implemented code** from requirements that require a genuine input dataset or team confirmation. Do not remove caveats without completing them.

| Rubric requirement | Current evidence | State |
|---|---|---|
| Team member documentation | Names preserved from original process book; V1 checklist in updated PDF | Listed; V1 participation confirmation needed |
| Complete data pipeline with real source | `scripts/build_data.py` downloader, cleaning, validation, summaries, CSV metadata; unit tested | Implemented, real-season run pending |
| Two functional D3 visualizations | `ThreePointChart.svelte`, `FingerprintMap.svelte` | Implemented, use illustrative data until source run |
| Additional drafts (2–3) | S4 accuracy, J2 pace/comeback, H4 team comparison, process-book addendum page 8 | Complete design drafts |
| Webpage structure | Page, chapter navigation, charts, future view placeholders, method notes | Complete prototype |
| Story | Question -> probability -> 3PT selection -> tactical view -> takeaway | Complete prototype |
| Novel view | J4-R 3-spoke glyph + outcome arc; click details | Implemented D3 renderer and PDF rationale |
| Updated process book | 24 original pages plus 9 new addendum pages | Complete; team-credit confirmation pending |
| One ZIP | Entire project and PDF | Complete |

## Blocking tasks before a fully compliant graded submission

1. Run `python scripts/build_data.py --season 2025` on an internet-enabled system or use a locally obtained authentic source parquet. Inspect metadata and record row counts in the process book.
2. Run `npm install`, `npm run check`, and `npm run build`; verify visual charts in browser (JavaScript dependencies cannot be installed in this sandbox).
3. Verify which of the three students actively contributed to Prototype V1 and complete the process-book contribution checklist.
4. Reread any interpretation text after real data are loaded. Do not present demo results as evidence.

## Disclosure

All delivered `static/data/*.csv` values are **illustrative** unless `static/data/metadata.json` says `"status": "real"`. Source download could not be executed here because outbound internet was blocked. Pipeline tests use a constructed trace to exercise calculations; they do not establish empirical basketball findings.
