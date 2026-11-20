<script>
  // H4: which teams lean on the three when trailing? Horizontal bars of each team's
  // three-point share of field-goal attempts in the chosen game state, with 95% intervals
  // and the league average. Follows the game state selected in any other chart.
  import * as d3 from 'd3';
  import { DEFICITS, TIMES, selection, clearSelection, asButton, restoreFocus, pct, wilson, ACCENT } from '$lib/state.svelte.js';

  let { data = [] } = $props();
  let node;
  let width = $state(800);
  let focusKey = null;
  let scope = $state('follow');
  let sortBy = $state('share');
  let minAttempts = $state(15);
  let pinned = $state(null);
  let hovered = $state(null);

  const filterFor = (s) => {
    if (s === 'late') return (d) => d.time === '0–3' || d.time === '3–6';
    if (s === 'all') return () => true;
    if (selection.deficit) return (d) => d.deficit === selection.deficit && d.time === selection.time;
    return () => true;
  };
  const scopeLabel = $derived(
    scope === 'late' ? 'final 6 minutes, any deficit'
      : scope === 'all' || !selection.deficit ? 'whole fourth quarter, any deficit'
        : `down ${selection.deficit} pts with ${selection.time} min left`
  );
  const teams = $derived.by(() => {
    const keep = filterFor(scope);
    void selection.deficit; void selection.time; // track the linked selection
    const rows = d3.rollups(data.filter(keep), (v) => ({ attempts: d3.sum(v, (d) => d.attempts), threes: d3.sum(v, (d) => d.threes) }), (d) => d.team)
      .map(([team, v]) => ({ team, ...v, share: v.threes / v.attempts, ci: wilson(v.threes, v.attempts) }));
    return rows;
  });
  const league = $derived(d3.sum(teams, (t) => t.threes) / d3.sum(teams, (t) => t.attempts));
  const visible = $derived(teams.filter((t) => t.attempts >= minAttempts)
    .sort(sortBy === 'share' ? (a, b) => b.share - a.share : sortBy === 'attempts' ? (a, b) => b.attempts - a.attempts : (a, b) => d3.ascending(a.team, b.team)));
  const hiddenCount = $derived(teams.length - visible.length);
  const shown = $derived(hovered ?? visible.find((t) => t.team === pinned) ?? null);

  function render(rows, w, avg) {
    if (!node) return;
    const svg = d3.select(node);
    svg.selectAll('*').remove();
    const rowH = 21, m = { t: 30, r: 64, b: 40, l: 52 };
    const H = Math.max(120, m.t + m.b + rows.length * rowH);
    svg.attr('width', w).attr('height', H).attr('viewBox', `0 0 ${w} ${H}`);
    if (!rows.length) {
      svg.append('text').attr('x', w / 2).attr('y', H / 2).attr('text-anchor', 'middle').attr('fill', '#4d5e70').text('No team reaches the minimum number of attempts here. Lower the threshold.');
      return;
    }
    const x = d3.scaleLinear().domain([0, Math.max(0.8, d3.max(rows, (d) => d.ci[1]))]).nice().range([m.l, w - m.r]);
    const y = d3.scaleBand().domain(rows.map((d) => d.team)).range([m.t, H - m.b]).padding(0.22);
    svg.append('g').attr('transform', `translate(0,${m.t - 6})`).call(d3.axisTop(x).ticks(w < 500 ? 4 : 8, '.0%').tickSize(-(H - m.t - m.b + 6)))
      .call((a) => a.select('.domain').remove())
      .call((a) => a.selectAll('line').attr('stroke', '#e6ecf1'))
      .call((a) => a.selectAll('text').attr('fill', '#4d5e70').attr('font-size', 11));
    const bars = svg.append('g').selectAll('g').data(rows).join('g').attr('class', 'bar')
      .attr('transform', (d) => `translate(0,${y(d.team)})`)
      .on('mouseenter', (_, d) => (hovered = d)).on('mouseleave', () => (hovered = null));
    asButton(bars, {
      label: (d) => `${d.team}: ${pct(d.share)} threes on ${d.attempts} attempts`,
      key: (d) => d.team,
      onActivate: (d) => { focusKey = d.team; pinned = pinned === d.team ? null : d.team; }
    });
    bars.append('rect').attr('x', m.l).attr('width', w - m.l - m.r).attr('height', y.bandwidth()).attr('fill', 'transparent');
    bars.append('rect').attr('x', m.l).attr('height', y.bandwidth()).attr('rx', 3)
      .attr('width', (d) => x(d.share) - m.l)
      .attr('fill', (d) => (d.team === pinned ? ACCENT : d.share >= avg ? '#2b8a8f' : '#9fb3c4'));
    bars.append('line').attr('x1', (d) => x(d.ci[0])).attr('x2', (d) => x(d.ci[1])).attr('y1', y.bandwidth() / 2).attr('y2', y.bandwidth() / 2)
      .attr('stroke', '#33475b').attr('stroke-width', 1.2).attr('opacity', 0.55);
    bars.append('text').attr('x', m.l - 8).attr('y', y.bandwidth() / 2).attr('dominant-baseline', 'middle').attr('text-anchor', 'end')
      .attr('font-size', 12).attr('font-weight', (d) => (d.team === pinned ? 800 : 600)).attr('fill', '#23374c').text((d) => d.team);
    bars.append('text').attr('x', (d) => Math.max(x(d.ci[1]), x(d.share)) + 6).attr('y', y.bandwidth() / 2).attr('dominant-baseline', 'middle')
      .attr('font-size', 11).attr('fill', '#4d5e70').text((d) => `${Math.round(d.share * 100)}% · ${d.attempts}`);
    svg.append('line').attr('x1', x(avg)).attr('x2', x(avg)).attr('y1', m.t - 6).attr('y2', H - m.b + 6).attr('stroke', '#17273b').attr('stroke-width', 1.5).attr('stroke-dasharray', '5 4');
    svg.append('text').attr('x', x(avg)).attr('y', H - m.b + 20).attr('text-anchor', 'middle').attr('font-size', 11).attr('font-weight', 700).attr('fill', '#17273b')
      .text(`league ${pct(avg)}`);
    svg.append('text').attr('x', m.l).attr('y', H - 4).attr('font-size', 11).attr('fill', '#4d5e70')
      .text('Three-point attempts as % of field-goal attempts · label: share · attempts');
    restoreFocus(node, focusKey);
    focusKey = null;
  }
  $effect(() => render(visible, width, league, pinned));
</script>

<div class="chart-controls team-controls">
  <label class="field"><span>Game state</span>
    <select bind:value={scope}>
      <option value="follow">{selection.deficit ? `Selected: down ${selection.deficit}, ${selection.time} min left` : 'Selected state (none yet: whole Q4)'}</option>
      <option value="late">Final 6 minutes, any deficit</option>
      <option value="all">Whole fourth quarter, any deficit</option>
    </select>
  </label>
  <label class="field"><span>Sort by</span>
    <select bind:value={sortBy}>
      <option value="share">3PT share</option>
      <option value="attempts">Attempts (sample size)</option>
      <option value="team">Team A–Z</option>
    </select>
  </label>
  <label class="field"><span>Min. attempts: {minAttempts}</span>
    <input type="range" min="5" max="150" step="5" bind:value={minAttempts} />
  </label>
  {#if selection.deficit && scope === 'follow'}<button class="link-button" onclick={clearSelection}>Clear selected state</button>{/if}
</div>
<p class="scope-line">Showing <strong>{scopeLabel}</strong> · {visible.length} teams{hiddenCount ? ` (${hiddenCount} hidden: fewer than ${minAttempts} attempts)` : ''}</p>
<div class="team-surface" bind:clientWidth={width}><svg bind:this={node} role="group" aria-label={`Bar chart of each team's three-point share, ${scopeLabel}`}></svg></div>
<div class="chart-detail" aria-live="polite">
  {#if shown}
    <strong>{shown.team}</strong>, {scopeLabel}: {shown.threes} threes on {shown.attempts} attempts = <strong>{pct(shown.share)}</strong> (95% interval {pct(shown.ci[0])}–{pct(shown.ci[1])}; league {pct(league)}). {#if shown.ci[0] > league}Clearly above the league.{:else if shown.ci[1] < league}Clearly below the league.{:else}The interval overlaps the league average, so this gap may be noise.{/if}
  {:else}
    Teal bars are above the league average, grey below. Whiskers show 95% intervals: in a single game state most teams have only 20–60 attempts, so many gaps are noise. Click a bar to pin a team while you change the game state.
  {/if}
</div>

<style>
  .team-controls { align-items: end; gap: 18px; }
  .field { display: flex; flex-direction: column; gap: 5px; font-size: 11px; font-weight: 700; color: #4d5e70; }
  .field select { appearance: none; background: #f8fafb; padding: 9px 12px; border: 1px solid #d5dee6; border-radius: 5px; color: #23374c; font-size: 12px; cursor: pointer; max-width: 300px; }
  .field input { width: 170px; accent-color: #c8441d; }
  .link-button { background: none; border: 0; color: #a8401f; font-weight: 700; font-size: 12px; text-decoration: underline; cursor: pointer; padding: 8px 0; }
  .scope-line { font-size: 12px; color: #4d5e70; margin: 14px 0 0; }
  .team-surface { width: 100%; margin-top: 8px; }
  @media (max-width: 760px) { .team-controls { align-items: stretch; } .field select { max-width: none; width: 100%; } .field input { width: 100%; } }
  .team-surface svg { display: block; }
</style>
