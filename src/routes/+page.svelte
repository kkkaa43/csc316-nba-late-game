<script>
  // The data story. Every number quoted in the text is read from the CSVs at load time,
  // so the narrative always matches the data built by scripts/build_data.py.
  import * as d3 from 'd3';
  import { onMount } from 'svelte';
  import { base } from '$app/paths';
  import ComebackHeatmap from '$lib/components/ComebackHeatmap.svelte';
  import ThreePointChart from '$lib/components/ThreePointChart.svelte';
  import FingerprintMap from '$lib/components/FingerprintMap.svelte';
  import AccuracyHeatmap from '$lib/components/AccuracyHeatmap.svelte';
  import PaceChart from '$lib/components/PaceChart.svelte';
  import TeamBars from '$lib/components/TeamBars.svelte';
  import SelectionBar from '$lib/components/SelectionBar.svelte';
  import { selectState, pct, num2 } from '$lib/state.svelte.js';

  let three = $state([]), states = $state([]), accuracy = $state([]), teamStates = $state([]), paceGames = $state([]);
  let meta = $state(null), error = $state(''), navOpen = $state(false);

  onMount(async () => {
    try {
      const load = (f) => d3.csv(`${base}/data/${f}`, d3.autoType);
      [three, states, accuracy, teamStates, paceGames, meta] = await Promise.all([
        load('three_point.csv'), load('fingerprint.csv'), load('accuracy.csv'), load('team_states.csv'), load('pace.csv'),
        d3.json(`${base}/data/metadata.json`)
      ]);
    } catch (e) {
      error = `Unable to load chart data: ${e.message}`;
    }
  });

  const cell = (rows, d, t) => rows.find((r) => r.deficit === d && r.time === t) ?? {};
  const s = (d, t) => cell(states, d, t);
  const a = (d, t) => cell(accuracy, d, t);
  const ready = $derived(states.length > 0 && accuracy.length > 0);
  const peak3 = $derived(d3.greatest(states, (r) => r.three_share) ?? {});
  const peakPace = $derived(d3.greatest(states, (r) => r.shots_per_min) ?? {});
  const fgOthers = $derived(accuracy.length ? d3.sum(accuracy.filter((r) => !(r.deficit === '1–3' && r.time === '0–3')), (r) => r.makes) / d3.sum(accuracy.filter((r) => !(r.deficit === '1–3' && r.time === '0–3')), (r) => r.attempts) : NaN);
  const attemptRange = $derived(d3.extent(three, (r) => r.attempts));
  const blowout = $derived(d3.extent(states.filter((r) => r.deficit === '11+'), (r) => r.shots_per_min));
  const seasonLabel = $derived(meta?.season_end_year ? `${meta.season_end_year - 1}–${String(meta.season_end_year).slice(-2)}` : '2024–25');
  const games = $derived(meta?.regular_season_games?.toLocaleString() ?? '1,230');
  const repo = 'https://github.com/kkkaa43/csc316-nba-late-game';
  const nav = [['odds', 'The odds'], ['shots', 'Shot choice'], ['fingerprint', 'Fingerprint'], ['accuracy', 'Accuracy'], ['pace', 'Speeding up'], ['teams', 'Teams'], ['methodology', 'Method & credits']];

  function show(d, t, id) {
    selectState(d, t);
    if (id) document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
</script>

<svelte:head>
  <title>Desperation Meter | NBA teams trailing late in the fourth quarter</title>
  <meta name="description" content="When NBA teams trail late, they shoot faster and take more threes, yet their chance of winning keeps falling. An interactive data story built on 2024–25 play-by-play data." />
</svelte:head>

<a class="skip-link" href="#story">Skip to the story</a>
<nav class="topbar" aria-label="Sections">
  <a class="wordmark" href="#top" aria-label="Desperation Meter, back to top"><span class="brand-ball" aria-hidden="true">◉</span><span>DESPERATION<span class="brand-accent">/</span>METER</span></a>
  <button class="nav-toggle" aria-label="Toggle navigation" aria-expanded={navOpen} onclick={() => (navOpen = !navOpen)}>☰</button>
  <div class:show={navOpen} class="nav-links">
    {#each nav as [id, label]}<a href={`#${id}`} onclick={() => (navOpen = false)}>{label}</a>{/each}
  </div>
</nav>
{#if error}<div class="error" role="alert">{error}</div>{/if}

<header id="top" class="hero">
  <div class="court-art" aria-hidden="true"><div class="court-circle"></div><div class="court-key"></div><div class="court-half"></div></div>
  <div class="hero-container">
    <div class="hero-copy">
      <div class="hero-eyebrow"><span class="pulse-dot"></span> NBA FOURTH QUARTERS · {seasonLabel} SEASON · {games} GAMES</div>
      <h1>When the clock runs out, <em>desperation</em> takes over.</h1>
      <p class="hero-dek">
        {#if ready}
          Down {peak3.deficit} points in the final {peak3.time.split('–')[1]} minutes, NBA teams take threes on <strong>{pct(peak3.three_share)}</strong> of their shots and shoot faster than in any other situation. Only <strong>{pct(peak3.comeback_rate)}</strong> of them win.
        {:else}
          Trailing late, NBA teams shoot faster and take more threes. Their chance of winning still keeps falling.
        {/if}
        Here is why that frantic finish looks like momentum but isn't.
      </p>
      <div class="hero-cta"><a class="primary-button" href="#story">Explore the story <span aria-hidden="true">↘</span></a></div>
      <p class="byline">By <strong>Jinhao Zhang, Herui Zhang &amp; Shiyuan Lyu</strong> · Data: ESPN play-by-play via <a href="https://github.com/sportsdataverse/sportsdataverse-data" target="_blank" rel="noreferrer">SportsDataverse</a></p>
    </div>
    <div class="scoreboard" role="img" aria-label="Example game state: fourth quarter, 1:28 left, trailing by 7. Not a real game.">
      <div class="board-top"><span>4TH QUARTER</span><span class="live-indicator"><i></i> EXAMPLE</span></div>
      <div class="board-clock">01:28<span class="clock-decimal">.0</span></div>
      <div class="board-bottom"><div><small>TRAILING BY</small><strong>07</strong><span>POINTS</span></div><div class="shot-clock"><small>WIN CHANCE</small><b>{ready ? pct(s('7–10', '0–3').comeback_rate) : '—'}</b></div></div>
      <div class="board-caption">HISTORICAL WIN RATE WHEN DOWN 7–10 WITH UNDER 3 MINUTES LEFT</div>
    </div>
  </div>
  <div class="hero-footer"><span>FOR BETTORS WHO KNOW THE BOX SCORE</span><a href="#story">SCROLL TO BEGIN ↓</a></div>
</header>

<main id="story">
  <section class="intro container">
    <div class="section-index">01 / THE QUESTION</div>
    <div class="intro-grid">
      <div><p class="kicker">SAME SCORE, DIFFERENT GAME</p><h2>Is a seven-point deficit always a seven-point deficit?</h2></div>
      <div class="intro-right">
        <p>With twelve minutes left, a trailing team can run its normal offence. With one minute left, it has to create chances right away. The scoreboard shows the same gap, but the situation is very different.</p>
        <p>We follow two numbers together, <strong>points behind</strong> and <strong>time left</strong>, through every fourth quarter of the {seasonLabel} regular season to see how trailing teams change their play, and whether that change actually wins games.</p>
      </div>
    </div>
    <div class="versus-grid">
      <div class="scenario-card"><span class="scenario-tag">SCENARIO A</span><div class="scenario-clock">12:00</div><span class="scenario-annotation">Fourth quarter begins, down 7–10</span><div class="scenario-rule"></div><p>{#if ready}<strong>{pct(s('7–10', '9–12').comeback_rate)}</strong> of teams in this spot went on to win.{/if} There are enough possessions left to stay patient.</p></div>
      <div class="versus-center" aria-hidden="true">VS</div>
      <div class="scenario-card late"><span class="scenario-tag">SCENARIO B</span><div class="scenario-clock">02:00</div><span class="scenario-annotation">Final three minutes, down 7–10</span><div class="scenario-rule"></div><p>{#if ready}Only <strong>{pct(s('7–10', '0–3').comeback_rate)}</strong> won.{/if} Teams need quick points, so they take quick shots and more risk.</p></div>
    </div>
  </section>

  <section id="odds" class="chapter section-light">
    <div class="container">
      <div class="chapter-heading">
        <div class="section-index">02 / THE ODDS</div>
        <div class="chapter-row">
          <div><p class="kicker">INSIGHT 1 · THE CLOCK MATTERS AS MUCH AS THE SCORE</p><h2>The same deficit gets harder to overcome every minute.</h2></div>
          <p>{#if ready}Down 1–3 at the start of the quarter, {pct(s('1–3', '9–12').comeback_rate)} of teams came back. Down 7–10, it falls from {pct(s('7–10', '9–12').comeback_rate)} to {pct(s('7–10', '0–3').comeback_rate)} as the clock runs out.{/if} Click any cell: your pick follows you through every chart below.</p>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-card-header">
          <div><span class="chart-overline">CHART 1 · HISTORICAL OUTCOMES</span><h3>How often trailing teams came back to win</h3><p class="chart-sub">Share of trailing team-games that won, by points behind and minutes left in the fourth quarter</p></div>
          <span class="chart-pill">HEATMAP · CLICK TO SELECT</span>
        </div>
        {#if states.length}<ComebackHeatmap data={states} />{:else}<div class="skeleton">Loading fourth-quarter game states…</div>{/if}
        <div class="chart-note"><span>HOW IT'S COUNTED</span><p>A team-game counts once per cell if the team trailed by that margin at any event in that time window; the same game can appear in several cells. "Won" includes overtime wins. The final cell (0–3 min) includes 3:00 exactly.</p></div>
      </div>
    </div>
  </section>

  <section id="shots" class="chapter">
    <div class="container">
      <div class="chapter-heading">
        <div class="section-index">03 / THE RESPONSE</div>
        <div class="chapter-row">
          <div><p class="kicker">INSIGHT 2 · SHOT SELECTION SHIFTS LATE</p><h2>In the final minutes, the three-pointer becomes the plan.</h2></div>
          <p>{#if ready}For the first nine minutes, about 40–44% of a trailing team's shots are threes, whatever the score. In the final three minutes the lines jump, peaking at <strong>{pct(peak3.three_share)}</strong> when down {peak3.deficit}, the deficit where one or two threes could tie the game.{/if}
            {#if ready}<button class="story-link" onclick={() => show(peak3.deficit, peak3.time)}>Select that state →</button>{/if}</p>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-card-header">
          <div><span class="chart-overline">CHART 2 · J1 · SHOT SELECTION</span><h3>Threes as a share of the trailing team's shots</h3><p class="chart-sub">Three-point attempts ÷ all field-goal attempts, by points behind; one line per time window</p></div>
          <span class="chart-pill">LINE CHART</span>
        </div>
        {#if three.length}<ThreePointChart data={three} />{:else}<div class="skeleton">Loading shot-selection data…</div>{/if}
        <div class="chart-note"><span>HOW IT'S COUNTED</span><p>The deficit is measured <em>before</em> each shot, so a made three is filed under the score the shooter faced. Each point is based on {attemptRange[0]?.toLocaleString()}–{attemptRange[1]?.toLocaleString()} attempts; hover a point for its exact count.</p></div>
      </div>
    </div>
  </section>

  <section id="fingerprint" class="chapter section-tinted">
    <div class="container">
      <div class="chapter-heading">
        <div class="section-index">04 / THE TACTICS</div>
        <div class="chapter-row">
          <div><p class="kicker">INSIGHT 3 · MORE THREES, FASTER SHOTS, SAME TURNOVERS</p><h2>Every game state leaves a tactical fingerprint.</h2></div>
          <p>{#if ready}Our custom glyph shows three habits at once. Close games swell in the final three minutes: down {peakPace.deficit}, trailing teams take <strong>{num2(peakPace.shots_per_min)}</strong> shots per minute, the most of any state. Down 11+, the fingerprint barely changes ({num2(blowout[0])}–{num2(blowout[1])} shots per minute): teams far behind don't really speed up.{/if}</p>
        </div>
      </div>
      <div class="chart-card fingerprint-card">
        <div class="chart-card-header">
          <div><span class="chart-overline">CHART 3 · J4-R · OUR NOVEL VIEW</span><h3>The Tactical Fingerprint Map</h3><p class="chart-sub">Three-point share, attempts per minute and turnovers per minute (spokes) plus comeback rate (arc), per game state</p></div>
          <span class="chart-pill novel">NOVEL GLYPH DESIGN</span>
        </div>
        {#if states.length}<FingerprintMap data={states} />{:else}<div class="skeleton">Loading tactical fingerprints…</div>{/if}
        <div class="chart-note"><span>DESIGN NOTE</span><p>Spokes use separate min–max scales, so compare a spoke with the same spoke in other glyphs, not with the other spokes. "Per minute" means per minute of game clock spent trailing in that state. The arc is the historical outcome, not a prediction.</p></div>
      </div>
    </div>
  </section>

  <section id="accuracy" class="chapter">
    <div class="container">
      <div class="chapter-heading">
        <div class="section-index">05 / THE COST</div>
        <div class="chapter-row">
          <div><p class="kicker">INSIGHT 4 · RUSHED SHOTS MISS MORE</p><h2>In one-possession games, the late shots stop falling.</h2></div>
          <p>{#if ready}Across the other 15 states, trailing teams shoot about {pct(fgOthers)} from the field. Down 1–3 in the final three minutes, that drops to <strong>{pct(a('1–3', '0–3').fg_pct)}</strong>, and their threes fall just <strong>{pct(a('1–3', '0–3').three_pct)}</strong> of the time.{/if}
            {#if ready}<button class="story-link" onclick={() => show('1–3', '0–3')}>Select that state →</button>{/if}</p>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-card-header">
          <div><span class="chart-overline">CHART 4 · S4 · SHOOTING ACCURACY</span><h3>How well trailing teams shoot in each game state</h3><p class="chart-sub">Field-goal % (or three-point %) of the trailing team; colour shows the gap from the all-states average</p></div>
          <span class="chart-pill">DIVERGING HEATMAP</span>
        </div>
        {#if accuracy.length}<AccuracyHeatmap data={accuracy} />{:else}<div class="skeleton">Loading accuracy data…</div>{/if}
        <div class="chart-note"><span>READING THIS CHART</span><p>Orange cells are below the average, blue above; "pts" in each cell is the gap in percentage points. With about 1,000 attempts per cell, gaps under ±3 points are within normal noise; use the 95% interval in the detail line.</p></div>
      </div>
    </div>
  </section>

  <section id="pace" class="chapter section-light">
    <div class="container">
      <div class="chapter-heading">
        <div class="section-index">06 / THE TEST</div>
        <div class="chapter-row">
          <div><p class="kicker">INSIGHT 5 · SPEEDING UP IS NOT A STRATEGY</p><h2>Teams that sped up didn't come back more often.</h2></div>
          <p>We compared each trailing team's shots in the last five minutes with the five minutes before. If urgency worked, the faster teams (right side of each panel) would win more. Within each deficit, they don't: the comeback rate stays close to that deficit's average.</p>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-card-header">
          <div><span class="chart-overline">CHART 5 · J2 · PACE CHANGE VS. COMEBACKS</span><h3>Change in shot volume vs. comeback rate</h3><p class="chart-sub">{paceGames.length.toLocaleString()} games in which a team trailed at the 5:00 mark, split by the deficit at 5:00</p></div>
          <span class="chart-pill">BUBBLE CHART · SMALL MULTIPLES</span>
        </div>
        {#if paceGames.length}<PaceChart data={paceGames} />{:else}<div class="skeleton">Loading game-level pace data…</div>{/if}
        <div class="chart-note"><span>CAVEAT</span><p>This is descriptive, not causal: a team that falls further behind may shoot more <em>because</em> it is losing, and a team that takes the lead stops needing to hurry. Clicking a bubble selects that deficit with 3–6 minutes left (the 5:00 mark) in the other charts.</p></div>
      </div>
    </div>
  </section>

  <section id="teams" class="chapter">
    <div class="container">
      <div class="chapter-heading">
        <div class="section-index">07 / THE TEAMS</div>
        <div class="chapter-row">
          <div><p class="kicker">INSIGHT 6 · LEAGUE AVERAGES HIDE TEAM STYLES</p><h2>Some teams lean on the three far more than others.</h2></div>
          <p>Pick a game state in any chart above and this ranking updates to show each team's three-point share in that exact situation. Watch the whiskers: inside a single state most teams have only a few dozen attempts, so only the extremes stand out from the league average.</p>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-card-header">
          <div><span class="chart-overline">CHART 6 · H4 · TEAM COMPARISON</span><h3>Each team's three-point share while trailing</h3><p class="chart-sub">Three-point attempts ÷ field-goal attempts, with 95% intervals; dashed line = league</p></div>
          <span class="chart-pill">LINKED BAR CHART</span>
        </div>
        {#if teamStates.length}<TeamBars data={teamStates} />{:else}<div class="skeleton">Loading team data…</div>{/if}
      </div>
    </div>
  </section>

  <section class="closing">
    <div class="container closing-grid">
      <div><p class="kicker">THE TAKEAWAY</p><h2>More urgency does not mean more momentum.</h2></div>
      <div>
        <p>When NBA teams trail late, they shoot faster and take more threes as time runs out, but that urgency does not turn into comebacks. The win rate keeps falling, and in one-possession games the rushed shots miss more often.</p>
        <ol class="takeaways">
          <li><strong>Read the score and the clock together.</strong> Down 7–10 is a {ready ? pct(s('7–10', '9–12').comeback_rate) : '~18%'} spot at 12:00 and a {ready ? pct(s('7–10', '0–3').comeback_rate) : '~3%'} spot in the final three minutes.</li>
          <li><strong>A late flurry of threes is a symptom, not a signal.</strong> The most three-heavy state ({ready ? `down ${peak3.deficit}, final 3 min` : 'down 4–6 late'}) wins only {ready ? pct(peak3.comeback_rate) : '~12%'} of the time.</li>
          <li><strong>Pace alone tells you little.</strong> Teams that sped up did not come back more often than teams that didn't.</li>
        </ol>
        <p class="conclusion-note">A descriptive look at one season ({seasonLabel}), not a betting model or a causal claim. Rates in small cells move a lot from season to season.</p>
      </div>
    </div>
  </section>

  <section id="methodology" class="methodology">
    <div class="container method-grid">
      <div>
        <p class="section-index">08 / METHOD &amp; CREDITS</p>
        <h2>Built from the play-by-play.</h2>
        <p>We used ESPN's NBA play-by-play for the {seasonLabel} regular season, published by the <a class="inline-link" href="https://github.com/sportsdataverse/sportsdataverse-data" target="_blank" rel="noreferrer">SportsDataverse / hoopR</a> project. A Python (pandas) script keeps the {games} regular-season games (the NBA Cup final and All-Star games are excluded), reconstructs the score <em>before</em> every event, and aggregates {meta?.trailing_q4_field_goal_attempts?.toLocaleString() ?? '26,716'} fourth-quarter shots by trailing teams into the CSV files behind each chart.</p>
        <p>Deficit bands: 1–3, 4–6, 7–10, 11+ points. Time windows: 12–9, 9–6, 6–3 and the final 3 minutes of the fourth quarter (overtime excluded). Rates in each cell are descriptive historical frequencies, not predictions.</p>
        <div class="method-links">
          <a class="text-link" href={repo} target="_blank" rel="noreferrer">Code, data &amp; data dictionary ↗</a>
          <a class="text-link" href="https://py.sportsdataverse.org/docs/nba/reference/loaders/other" target="_blank" rel="noreferrer">Data source docs ↗</a>
        </div>
      </div>
      <div class="method-list">
        <div><strong>Authors</strong><span>Jinhao Zhang · Herui Zhang · Shiyuan Lyu</span></div>
        <div><strong>Course</strong><span>CSC316 Data Visualization · University of Toronto · Fall 2026</span></div>
        <div><strong>Audience</strong><span>Sports bettors who know basic NBA statistics</span></div>
        <div><strong>Data</strong><span>ESPN NBA play-by-play via SportsDataverse / hoopR · {seasonLabel} regular season · {games} games</span></div>
        <div><strong>Analysis</strong><span>Python · pandas · scripts/build_data.py</span></div>
        <div><strong>Visualization</strong><span>SvelteKit 5 · D3 v7 · SVG</span></div>
        <div><strong>Limitations</strong><span>One season; some cells hold a few hundred games; no shot location or line-up data; not affiliated with the NBA or ESPN</span></div>
      </div>
    </div>
  </section>
</main>
<footer class="footer">
  <div class="container footer-inner">
    <span class="wordmark"><span class="brand-ball" aria-hidden="true">◉</span> DESPERATION<span class="brand-accent">/</span>METER</span>
    <span>CSC316 · University of Toronto · Jinhao Zhang, Herui Zhang, Shiyuan Lyu</span>
    <a href="#top">BACK TO TOP ↑</a>
  </div>
</footer>
<SelectionBar {states} {accuracy} />
