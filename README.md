# DESPERATION / METER · CSC316 Prototype V1

A narrative SvelteKit / D3 NBA fourth-quarter visualization prototype based on the group's CSC316 milestones. **Website is implemented; real-season data acquisition is not complete in the bundled preview.** Please read the data-status notice.

## Running the website

```bash
npm install
npm run dev
```

Visit the local URL printed by Vite (normally `http://localhost:5173`). For a deployable production build: `npm run build`.

This is a proper SvelteKit 5 project using D3 v7 and SVG, with responsive page layout and interactions.

## Using REAL NBA play-by-play rather than the ILLUSTRATIVE preview

The bundled `static/data` CSVs exist only to demonstrate that D3 charts render and the website structure is functional. Their values are **synthetic and explicitly tagged illustrative; they must not be cited as basketball findings.** The generation script is included for transparency: `scripts/make_demo.py`.

**To replace the preview with actual data:**

```bash
python -m pip install -r scripts/requirements.txt
python scripts/build_data.py --season 2025
# or if the downloaded file is already on your computer:
python scripts/build_data.py --input /path/to/play_by_play_2025.parquet
npm run dev
```

The pipeline downloads authentic 2024-25 ESPN NBA play-by-play from the SportsDataverse / hoopR release, caches the raw parquet to `data/raw/`, validates and cleans it with pandas, writes audit events to `data/cleaned/q4_events.csv`, generates four CSV aggregations in `static/data/` and writes provenance metadata in `static/data/metadata.json` (including source SHA-256, games, rows). On load, the website reads the fresh CSVs via `d3.csv()` and automatically removes the design-preview warning in favor of a real-data notice.

Internet access is needed once for downloading the season parquet. The source can be large. This build environment had no route to the large source release; therefore the pipeline has been implemented and unit-tested, but not successfully executed over the full season here. **Do not mark the data collection requirement complete until you run the pipeline with the original parquet and inspect its output.**

### Source and license

Source: `https://github.com/sportsdataverse/sportsdataverse-data/releases/download/espn_nba_pbp/play_by_play_2025.parquet` (see https://py.sportsdataverse.org/docs/nba/reference/loaders/other). Derived from ESPN NBA play-by-play, not directly from stats.nba.com. This project is not affiliated with the NBA/ESPN. Ensure permissible research reuse and source attribution when publishing.

## Visualization inventory

- **Implemented in D3:** comeback outcomes matrix (storyboard support), J1 shot-selection multiseries line chart, J4-R novel glyph tactical fingerprint map. Both J1 and J4-R load from generated CSVs. The additional comeback matrix uses the same real-data metrics as J4-R.
- **Design drafts:** S4 shooting-accuracy heatmap, J2 pace-change versus comeback scatterplot, H4 team-specific 3PT bar chart; conceptual placeholders on page and annotated drafts in PDF.

## Measurement details

- Restricts to regular season (`season_type == 2`), completed games, fourth quarter (no OT), with valid score/time/team.
- Uses **pre-event score** for shot-selection / turnover state assignments, so made shots are not classified at their post-shot deficit.
- `three_share = 3PA / (2PA + 3PA)` among trailing field-goal attempts in each bin.
- `shots_per_min` and `turnovers_per_min` denominator is the amount of time a team spent trailing in each post-event score state, accumulated from adjacent play clocks, split at the window boundary.
- `comeback_rate = winning trailing-team game observations / distinct trailing-team game observations` within each cell. Each team/game counted once *per cell*, may appear across cells. It is **descriptive and not a calibrated live-game prediction**.
- Sparse bins should be treated cautiously. Some state-games appear in several adjacent cells, so observations are not statistically independent.
- For J4-R, different spokes use independent maxima as normalization; only exact values in the detail pane are appropriate for cross-indicator numerical comparisons.

## Folder map

```
project/
  src/routes/+page.svelte      # narrative page, D3 CSV loading
  src/lib/components/          # D3 renderers: 3PT lines, glyphs, comeback matrix
  src/app.css                  # responsive editorial styling
  scripts/build_data.py       # source download, validate, clean, aggregate, provenance
  scripts/make_demo.py        # transparently illustrative page preview only
  tests/test_pipeline.py      # deterministic data-cleaning/unit checks
  static/data/                # sample preview CSV, overwritten by real build
  data/cleaned/               # populated by real build
  process_book/               # PDF: original 24 pages + V1 addendum
  reference/                  # previous milestone PDF and older team analysis notebook
```

## Prototype team documentation

Prior process book lists **Jinhao Zhang, Herui Zhang, and Shiyuan Lyu** as the team. The V1 process-book addendum provides a contributor-confirmation box. I cannot verify which group members actively worked on *this particular prototype* from the supplied documents, so do not represent the roster as confirmed V1 contribution until the team checks it.

## Quality checks

```bash
python -m unittest discover -s tests -v
npm run check
npm run build
```

Frontend check/build require `npm install` in a network-enabled environment. This archive does not include `node_modules`.
