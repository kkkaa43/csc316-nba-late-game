# Final submission checklist (due Sun 6 Dec 2026, 23:59; one ZIP, submitted once by the team's submitter)

## ZIP contents

| Item | Required by | Where it comes from | Done |
|---|---|---|---|
| Process book PDF (complete, clean, **with the website link**) | "Complete and clean process book" | Export the Google Doc to PDF | ☐ |
| 2-minute video (MP4, H.264, ≤ 2:00) | "2-minute video" | Record with `docs/VIDEO_SCRIPT.md` | ☐ |
| README (how to run, libraries) | "README on how to run the code, used libraries" | `README.md` | ✅ |
| Data + field description file | "Data (submitted and with a file describing data fields)" | `static/data/*`, `data/cleaned/q4_events.csv`, `data/DATA_DICTIONARY.md` | ✅ (regenerate q4_events first) |
| Code (clean and documented) | "Code" | `src/`, `scripts/`, `tests/`, configs | ✅ |
| Link to project website | "Link to project website" | `WEBSITE.txt` (created by the script) + README + process book | ✅ |
| Peer evaluation form, **each member individually** | Completeness | https://forms.gle/eBptv6YGT5b2j6br5 | ☐ ☐ ☐ |

## Build the ZIP

```bash
cd ~/code/csc316-nba
.venv/bin/python scripts/build_data.py --input data/raw/play_by_play_2025.parquet   # regenerates q4_events.csv
scripts/package_submission.sh path/to/ProcessBook.pdf path/to/video.mp4
```

The script copies the tracked files of the repo (no `node_modules`, no raw parquet), the cleaned event
table, the process book and the video into `dist/CSC316_NBA_Desperation_Meter.zip`.

## Before submitting

- [ ] Website loads at https://kkkaa43.github.io/csc316-nba-late-game/ in a private window, all 6 charts render.
- [ ] Process book has: think-aloud notes (subject name + email), findings, improvement list, what was
      changed, before/after screenshots, a Prototype V2/V3/final section, the website link, and the TF's
      M8 feedback with how you responded.
- [ ] Video ≤ 2:00, plays in VLC, narration audible.
- [ ] Unzip the ZIP into a fresh folder and run `npm install && npm run dev` once.
- [ ] Every member has filled in the peer evaluation form.
