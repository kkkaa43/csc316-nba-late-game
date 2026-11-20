<script>
  // J2: does speeding up pay off? One row per game where a team trailed at the 5:00 mark.
  // Games are grouped by how many more (or fewer) shots the trailing team took in the final
  // 5:00 than in the 5:00 before. Bubble area = number of games, y = share that came back,
  // whiskers = 95% interval. One small multiple per deficit band so each comparison is
  // made among games that started from the same deficit.
  import * as d3 from 'd3';
  import { DEFICITS, DEFICIT_COLORS, selection, selectState, asButton, restoreFocus, pct, wilson } from '$lib/state.svelte.js';

  let { data = [] } = $props();
  let node;
  let width = $state(900);
  let focusKey = null;
  let hovered = $state(null);
  let showCI = $state(true);
  const BUCKETS = [
    { key: 'b0', label: '3+ fewer', short: '−3+', test: (d) => d <= -3 },
    { key: 'b1', label: '1–2 fewer', short: '−1/2', test: (d) => d < 0 && d > -3 },
    { key: 'b2', label: 'same', short: '0', test: (d) => d === 0 },
    { key: 'b3', label: '1–2 more', short: '+1/2', test: (d) => d > 0 && d < 3 },
    { key: 'b4', label: '3+ more', short: '+3+', test: (d) => d >= 3 }
  ];
  const groups = $derived(DEFICITS.map((deficit) => {
    const games = data.filter((g) => g.deficit === deficit);
    const won = games.filter((g) => g.comeback === true || g.comeback === 'True').length;
    return {
      deficit, n: games.length, rate: games.length ? won / games.length : NaN,
      bins: BUCKETS.map((b) => {
        const inBin = games.filter((g) => b.test(g.last5_fga - g.prior5_fga));
        const k = inBin.filter((g) => g.comeback === true || g.comeback === 'True').length;
        return { ...b, deficit, n: inBin.length, k, rate: inBin.length ? k / inBin.length : NaN, ci: wilson(k, inBin.length) };
      })
    };
  }));
  const totalGames = $derived(data.length);

  function render(gs, w, ci) {
    if (!node || !gs.length || !data.length) return;
    const cols = w < 520 ? 1 : w < 860 ? 2 : 4;
    const rowsN = Math.ceil(gs.length / cols);
    const gap = 18, ml = 46, panelW = (w - ml - gap * (cols - 1)) / cols, panelH = 230, top = 34, bottom = 44;
    const H = rowsN * (panelH + top + bottom) + 8;
    const svg = d3.select(node).attr('width', w).attr('height', H).attr('viewBox', `0 0 ${w} ${H}`);
    svg.selectAll('*').remove();
    const maxN = d3.max(gs, (g) => d3.max(g.bins, (b) => b.n));
    const r = d3.scaleSqrt().domain([0, maxN]).range([0, Math.min(17, panelW / 12)]);
    const y = d3.scaleLinear().domain([0, 0.7]).clamp(true).range([panelH, 0]);
    const x = d3.scalePoint().domain(BUCKETS.map((b) => b.key)).range([0, panelW]).padding(0.6);
    const dim = selection.deficit !== null;
    gs.forEach((g, i) => {
      const ox = ml + (i % cols) * (panelW + gap), oy = Math.floor(i / cols) * (panelH + top + bottom) + top;
      const p = svg.append('g').attr('transform', `translate(${ox},${oy})`).attr('opacity', !dim || selection.deficit === g.deficit ? 1 : 0.35);
      p.append('rect').attr('width', panelW).attr('height', panelH).attr('fill', selection.deficit === g.deficit ? '#fff6f1' : '#f7f9fb').attr('rx', 8)
        .attr('stroke', selection.deficit === g.deficit ? '#17273b' : 'none');
      p.append('text').attr('x', 8).attr('y', -12).attr('font-size', 13).attr('font-weight', 700).attr('fill', DEFICIT_COLORS[g.deficit])
        .text(`Down ${g.deficit} at 5:00`);
      p.append('text').attr('x', panelW).attr('y', -12).attr('text-anchor', 'end').attr('font-size', 11).attr('fill', '#4d5e70')
        .text(`${g.n} games`);
      p.append('g').selectAll('line').data([0, 0.2, 0.4, 0.6]).join('line').attr('x1', 0).attr('x2', panelW).attr('y1', y).attr('y2', y).attr('stroke', '#e3e9ee');
      if (i % cols === 0) {
        p.append('g').call(d3.axisLeft(y).tickValues([0, 0.2, 0.4, 0.6]).tickFormat(d3.format('.0%')).tickSize(0))
          .call((a) => a.select('.domain').remove()).call((a) => a.selectAll('text').attr('fill', '#4d5e70').attr('font-size', 11).attr('dx', '-.3em'));
      }
      // Average comeback rate for this deficit band, regardless of pace.
      p.append('line').attr('x1', 0).attr('x2', panelW).attr('y1', y(g.rate)).attr('y2', y(g.rate)).attr('stroke', '#17273b').attr('stroke-dasharray', '4 4').attr('opacity', 0.6);
      p.append('text').attr('x', panelW - 4).attr('y', y(g.rate) - 5).attr('text-anchor', 'end').attr('font-size', 10).attr('fill', '#33475b').text(`avg ${pct(g.rate)}`);
      const valid = g.bins.filter((b) => b.n > 0);
      p.append('path').datum(valid).attr('d', d3.line().x((b) => x(b.key)).y((b) => y(b.rate))).attr('fill', 'none').attr('stroke', DEFICIT_COLORS[g.deficit]).attr('stroke-width', 1.5).attr('opacity', 0.5);
      const bubbles = p.selectAll('g.bubble').data(valid).join('g').attr('class', 'bubble')
        .attr('transform', (b) => `translate(${x(b.key)},${y(b.rate)})`)
        .on('mouseenter', (_, b) => (hovered = b)).on('mouseleave', () => (hovered = null));
      asButton(bubbles, {
        label: (b) => `Down ${g.deficit} at 5:00, ${b.label} shots in the final 5 minutes: ${b.k} of ${b.n} games came back (${pct(b.rate)})`,
        key: (b) => `${g.deficit}|${b.key}`,
        onActivate: (b) => { focusKey = `${g.deficit}|${b.key}`; hovered = b; selectState(g.deficit, '3–6'); }
      });
      if (ci) bubbles.append('line').attr('y1', (b) => y(b.ci[0]) - y(b.rate)).attr('y2', (b) => y(b.ci[1]) - y(b.rate)).attr('stroke', '#8d9aac').attr('stroke-width', 1.2);
      bubbles.append('circle').attr('r', (b) => Math.max(3, r(b.n))).attr('fill', DEFICIT_COLORS[g.deficit]).attr('fill-opacity', 0.78).attr('stroke', '#fff').attr('stroke-width', 1.5);
      p.append('g').attr('transform', `translate(0,${panelH})`).call(d3.axisBottom(x).tickSize(0).tickFormat((k) => { const b = BUCKETS.find((v) => v.key === k); return panelW < 230 ? b.short : b.label; }))
        .call((a) => a.select('.domain').attr('stroke', '#b8c4cf'))
        .call((a) => a.selectAll('text').attr('fill', '#4d5e70').attr('font-size', 10.5).attr('dy', '1.3em'));
    });
    restoreFocus(node, focusKey);
    focusKey = null;
  }
  $effect(() => render(groups, width, showCI, selection.deficit));
</script>

<div class="chart-controls">
  <p class="axis-caption">X: change in the trailing team's field-goal attempts, final 5:00 vs. the 5:00 before (10:00–5:00). Y: share of games the trailing team won. Bubble area = number of games.</p>
  <label class="check"><input type="checkbox" bind:checked={showCI} /> Show 95% intervals</label>
</div>
<div class="pace-surface" bind:clientWidth={width}>
  <svg bind:this={node} role="group" aria-label={`Small multiples: comeback rate by change in shot attempts, one panel per deficit at the 5:00 mark, ${totalGames} games`}></svg>
</div>
<div class="chart-detail" aria-live="polite">
  {#if hovered}
    Down <strong>{hovered.deficit}</strong> at 5:00 and took <strong>{hovered.label}</strong> shots in the final 5 minutes: <strong>{hovered.k} of {hovered.n}</strong> games ({pct(hovered.rate)}) ended in a comeback (95% interval {pct(hovered.ci[0])}–{pct(hovered.ci[1])}).
  {:else}
    If speeding up caused comebacks, bubbles on the right of each panel would sit higher. They don't: within each deficit, the rate stays near the dashed average and the intervals overlap. Hover a bubble for counts.
  {/if}
</div>

<style>
  .pace-surface { width: 100%; margin-top: 12px; }
  .pace-surface svg { display: block; overflow: visible; }
  .axis-caption { font-size: 12px; color: #4d5e70; margin: 0; max-width: 640px; line-height: 1.5; }
  .check { font-size: 12px; color: #33475b; display: inline-flex; gap: 6px; align-items: center; font-weight: 600; }
</style>
