# Final-project rubric: status (audit of 20 Nov 2026)

Legend: ✅ met · 🔧 fixed in this audit · 👤 needs a team member (cannot be done in code)

| Rubric item | Status | Evidence / what is left |
|---|---|---|
| **Completeness**: team agreement, proposal | ✅ | Submitted earlier on Quercus (per team). |
| Completeness: all required files, peer assessment from each member | 👤 | ZIP: `docs/SUBMISSION_CHECKLIST.md`; each member fills https://forms.gle/eBptv6YGT5b2j6br5 |
| Completeness: TFs can read the process book and view the video | 👤 | Export Google Doc to PDF; MP4 H.264. |
| **Map & Data**: audience, initial questions | ✅ | Process book M2 (13 questions, bettor audience). |
| Map & Data: data description incl. cleanup | 🔧 | README "Cleaning steps" + `data/DATA_DICTIONARY.md`; M7 text in process book still says illustrative data → updated in the M8/Final draft section. |
| Map & Data: cleanup / EDA code | ✅ | `scripts/build_data.py`, `reference/CSC316_NBA_5_Plots_Colab.ipynb`, `tests/`. |
| Map & Data: complete cleaned data | 🔧 | `static/data/*` + `q4_events.csv` (packaged into ZIP); turnover/foul definitions fixed. |
| **Sketch & Storyboard** | ✅ | Process book M3 (sketches per member) and M6 storyboard. Check Shiyuan's M3 sketches appear in the PDF export. |
| **Decide**: clustering, voting, refined message | ✅ | Process book M4 and M6. |
| **Prototype**: code + data for V1, V2, V3, final | 🔧 / 👤 | Git history: V1 = `86fa01a`; final = this audit's commits. Tag versions (`git tag`) and add a short V2/V3 section with screenshots to the process book. |
| Prototype: screenshots before and after the test | 👤 | Take after the think-aloud test (`docs/THINK_ALOUD_TEST.md`). |
| Prototype: features/issues addressed after the test | 👤 | Fill in the test template's "addressed" column. |
| **Data story**: title, subtitles, captions | 🔧 | Every chart now has an overline, title, one-line subtitle, axis titles with units, and a note. |
| Data story: answers the questions, gives insights | 🔧 | Six insights, each with numbers read live from the CSVs. |
| Data story: hook, main message, takeaways | 🔧 | Hero hook with the 51.7% / 11.8% contrast; closing section with main message + 3 takeaways for bettors. |
| Data story: design (whitespace, C.R.A.P., Gestalt) | ✅ | Consistent cards, alignment and type scale; contrast of small grey text raised. |
| Data story: data sources and authors identified | 🔧 | Byline in the hero, Method & credits section, footer. |
| **Test**: think-aloud notes (name + email of subject) | 👤 | `docs/THINK_ALOUD_TEST.md` (protocol + template). Names/emails go only in the process book. |
| **Process book**: complete | 👤 | Draft "Milestone 8 / Final" section appended to the Google Doc (marked DRAFT); team to review, add test results, screenshots, TF feedback. Milestone 5 heading is missing from the doc. |
| **Video** (length, narration, audience) | 👤 | `docs/VIDEO_SCRIPT.md` (timed script + shot list). |
| **Vis color usage** (2) | 🔧 | Ordinal palettes for time (cool → warm) and deficit (light → dark); sequential comeback scale with legend; diverging accuracy scale centred on the average; accent orange only for "selected". |
| **Vis encoding** (5) | 🔧 | S4, J2, H4 implemented; 95% intervals where samples are small; sample sizes in every tooltip/detail line. |
| **Vis interaction** (5) | 🔧 | Click/keyboard selection, hover details, legend highlight, FG%/3P% toggle, CI toggle, H4 scope / sort / min-attempts controls, team pinning. |
| **Design guidelines** (5) | 🔧 | Titles, axis titles + units, direct labels, annotations, no chart junk, accessible focus states, `aria-label`s, mobile layout. |
| **Linked views** (2) | 🔧 | Shared selection across charts 1–6 + sticky summary bar. |
| **Innovative visualization** (5) | ✅ | J4-R Tactical Fingerprint Map (novel glyph). |
| **Website quality** (1) | 🔧 | `npm run check` 0 errors / 0 warnings, build passes, GitHub Pages deploy via Actions. |
