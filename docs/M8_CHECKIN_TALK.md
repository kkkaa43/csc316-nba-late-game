# Milestone 8 check-in (Tue 24 Nov 2026, before 12:00): 3-minute walkthrough

All three members attend. Have open: the live site, the process book (Google Doc), this repo.
The TF will direct questions to individuals, so **everyone should be able to explain any chart and the
data pipeline** (see the Q&A prep below).

## Script (~3:00, ~420 words)

**1. Topic and audience (0:00–0:30).** "Our project asks how NBA teams change their offence when they
trail in the fourth quarter. Our audience is sports bettors who know basic stats like FG% and pace. They
watch live games and need to judge whether a late surge actually changes the odds."

**2. Data (0:30–0:55).** "We use ESPN play-by-play for the 2024–25 regular season from SportsDataverse:
1,230 games, about 27,000 fourth-quarter shots by trailing teams. Our Python script rebuilds the score
before every event, so a made three counts at the deficit the shooter faced, and bins every event by
deficit (1–3, 4–6, 7–10, 11+) and time left (four three-minute windows)."

**3. Story walkthrough (0:55–2:30).** Scroll and click while talking.
- *Chart 1, comeback heatmap (hook).* "The same deficit is a different game late: down 7–10, 17.7% come back at 12:00, 3.0% in the last three minutes. Clicking a cell selects that state everywhere."
- *Chart 2, J1.* "Teams respond with threes: around 40% of shots early, peaking at 51.7% when down 4–6 in the final three minutes."
- *Chart 3, J4-R, our novel view.* "Each glyph combines three-point share, shots per minute and turnovers, plus an arc for comeback rate. Down 4–6 late has the biggest triangle, 2.31 shots a minute, but only an 11.8% arc. Down 11+, teams don't actually speed up."
- *Chart 4, S4.* "Accuracy holds except in one-possession games at the end: 42.2% FG versus about 46% elsewhere."
- *Chart 5, J2.* "Teams that took more shots in the final five minutes than in the five before did not come back more often, within each deficit."
- *Chart 6, H4.* "It's linked to the selection, so you can compare teams in exactly this situation, with 95% intervals so we don't over-read small samples."

**4. Main message (2:30–2:45).** "When teams trail late they shoot faster and take more threes, but that
urgency doesn't turn into comebacks. For a bettor, a late flurry of threes is a symptom of desperation, not momentum."

**5. Plan and questions (2:45–3:00).** "Next: think-aloud tests, then the video and final polish.
Our questions for you: (1) is the fingerprint glyph readable enough, or should we add an animated
'how to read it' step? (2) Is one season enough, or should we add 2023–24 for stability?"

## Q&A prep (anyone may be asked)

| Likely question | Short answer |
|---|---|
| Why pre-event score? | ESPN rows hold the score after the event; using it would put a made shot in the wrong (smaller) deficit. |
| How is comeback rate counted? | Distinct trailing team-games per cell that eventually won (OT included). A game can appear in several cells, so cells aren't independent. |
| What does "per minute" mean? | FGA (or turnovers) divided by game-clock minutes spent trailing in that cell, both teams' possessions included. |
| Why min–max scaling on the glyph spokes? | Raw values differ only by a few percent; scaling to the observed range makes differences visible. The side panel shows exact values. |
| Is J2 causal? | No. Teams that fall further behind may shoot more because they're losing. It is descriptive. |
| Why exclude the NBA Cup final? | It doesn't count in regular-season records; All-Star games are excluded because they aren't real games. |
| Linked views? | One shared selection (`src/lib/state.svelte.js`) drives charts 1–4, highlights chart 5's deficit panel and filters chart 6. |
| Turnover definition? | ESPN event type ids 62–90 and 206; this includes "Traveling" and excludes "No Turnover". |
| Sample size concerns? | Cells have 879–3,604 shots; teams in a single state often 20–60, hence the 95% intervals and min-attempt filter in H4. |
