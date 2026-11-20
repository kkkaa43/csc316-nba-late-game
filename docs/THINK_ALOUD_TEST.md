# Think-aloud user test: protocol and note template

The rubric's **Test** section asks for: complete think-aloud notes by the team **including the name and
email of the test subject**; the main findings; a list of improvement ideas; evidence that the comments
were addressed in the final submission; and (under Prototype) screenshots before and after the test.

> Privacy: the subject's name and email go **only in the process book** (Google Doc / submitted PDF),
> never in this public repository.

## Plan

- **Subject:** one person outside the team, ideally close to the audience (follows the NBA, has placed a
  sports bet or knows box-score stats). Ask for consent to take notes; no recording needed.
- **Roles:** facilitator (reads tasks, prompts "what are you thinking?"), note-taker (writes quotes and
  timestamps), observer (watches where the subject clicks or hesitates). Rotate if testing several people.
- **Length:** 20–25 minutes. Live site on a laptop; subject drives.
- **Rules for the facilitator:** do not explain the charts; if the subject is stuck for 30 s, ask "what
  would you try next?"; only help after 60 s, and note that you helped.

## Script

1. **Intro (1 min).** "We're testing the website, not you. Please say out loud what you see, what you
   expect and what confuses you."
2. **First impression (2 min).** Let them read the hero. Ask: "What do you think this page is about? Who is it for?"
3. **Tasks** (note time to complete, success / partial / fail, quotes):
   1. Using the first chart, how often did teams down 7–10 with 9–12 minutes left come back? (expect 17.7%)
   2. In which situation do trailing teams take the largest share of threes? (down 4–6, final 3 min, 51.7%)
   3. Select "down 4–6, final 3 minutes" in any chart. Without being told, do you notice the other charts change? What changed?
   4. In the Fingerprint Map, which spoke means turnovers? Is the triangle for "down 11+, 0–3 min" bigger or smaller than for "down 4–6, 0–3 min"?
   5. Does shooting accuracy drop late in close games? By how much?
   6. In the pace chart, do teams that speed up come back more often? How sure are you?
   7. Find the team that takes the highest share of threes when trailing in the final 6 minutes.
4. **Debrief (5 min).** "In one sentence, what is the main message?" · "What was most / least useful?" ·
   "Would this change how you read a live game or a live bet?" · "Anything you expected to be clickable that wasn't?"

## Note template (copy into the process book)

```
Think-aloud test #__   Date: ____   Location / mode: ____
Subject: name ____________  email ____________  background (NBA / betting / stats): ____
Team roles: facilitator ____  note-taker ____  observer ____
Site version: commit ______ (https://kkkaa43.github.io/csc316-nba-late-game/)

First impression (quote): ...
Task | Time | Result (✓ / partial / ✗) | What they did / said | Issue observed
T1   |      |                          |                       |
T2   |      |                          |                       |
T3   |      |                          |                       |
T4   |      |                          |                       |
T5   |      |                          |                       |
T6   |      |                          |                       |
T7   |      |                          |                       |
Main message in their words: ...
Debrief answers: ...

Main findings (3–5 bullets):
Improvement ideas (issue → proposed change → priority → owner):
Addressed in final? (change made + commit hash + before/after screenshot):
```

## After the test

1. Paste the filled template into the process book under "Testing".
2. Take "before" screenshots of each chart (the version tested) and "after" screenshots once fixes land.
3. Turn each issue into a change, commit it, and record the commit hash next to the issue.
