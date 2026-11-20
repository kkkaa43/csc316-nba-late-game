<script>
  // J1: three-point share of the trailing team's field-goal attempts, by deficit (x) and
  // time window (one line each). Points are buttons that select the game state everywhere.
  import * as d3 from 'd3';
  import { DEFICITS, TIMES, TIME_COLORS, selection, selectState, isSelected, asButton, restoreFocus, pct } from '$lib/state.svelte.js';

  let { data = [] } = $props();
  let node;
  let focusKey = null;
  let hovered = $state(null);
  let pinnedTime = $state(null); // legend toggle, local to this chart
  const emphasis = $derived(selection.time ?? pinnedTime);
  const shown = $derived(hovered ?? data.find((d) => isSelected(d)));

  function render(rows, emph) {
    if (!node || !rows?.length) return;
    const svg = d3.select(node);
    svg.selectAll('*').remove();
    const W = 720, H = 380, m = { top: 26, right: 92, bottom: 58, left: 70 };
    svg.attr('viewBox', `0 0 ${W} ${H}`);
    const x = d3.scalePoint().domain(DEFICITS).range([m.left, W - m.right]).padding(0.35);
    // Zoom the y-axis to the observed range (5% steps) so differences of a few points stay
    // visible; the axis title says where it starts.
    const [lo, hi] = d3.extent(rows, (d) => d.three_share);
    const yMin = Math.max(0, Math.floor((lo - 0.02) * 20) / 20), yMax = Math.min(1, Math.ceil((hi + 0.02) * 20) / 20);
    const y = d3.scaleLinear().domain([yMin, yMax]).range([H - m.bottom, m.top]);
    const ticks = d3.range(yMin, yMax + 1e-9, 0.05);
    svg.append('g').selectAll('line').data(ticks).join('line')
      .attr('x1', m.left).attr('x2', W - m.right).attr('y1', y).attr('y2', y)
      .attr('stroke', '#e3e9ee').attr('stroke-dasharray', (d, i) => (i === 0 ? null : '3,5'));
    svg.append('g').attr('transform', `translate(0,${H - m.bottom})`).call(d3.axisBottom(x).tickSize(0).tickFormat((d) => `${d} pts`))
      .call((a) => a.select('.domain').attr('stroke', '#8d9aac'))
      .call((a) => a.selectAll('text').attr('dy', '1.4em').attr('fill', '#4d5e70').attr('font-size', 13));
    svg.append('g').attr('transform', `translate(${m.left},0)`).call(d3.axisLeft(y).tickValues(ticks).tickFormat(d3.format('.0%')).tickSize(0))
      .call((a) => a.select('.domain').remove()).call((a) => a.selectAll('text').attr('dx', '-.5em').attr('fill', '#4d5e70').attr('font-size', 12));
    svg.append('text').attr('x', (m.left + W - m.right) / 2).attr('y', H - 8).attr('text-anchor', 'middle').attr('fill', '#4d5e70').attr('font-size', 12)
      .text('Points behind before the shot');
    svg.append('text').attr('transform', `translate(18,${(H - m.bottom + m.top) / 2}) rotate(-90)`).attr('text-anchor', 'middle').attr('fill', '#4d5e70').attr('font-size', 12)
      .text(`Threes as % of field-goal attempts${yMin > 0 ? ` (axis starts at ${Math.round(yMin * 100)}%)` : ''}`);

    // Annotation on the highest point of the chart.
    const peak = d3.greatest(rows, (d) => d.three_share);
    if (peak) {
      const px = x(peak.deficit), py = y(peak.three_share);
      svg.append('line').attr('x1', px + 10).attr('y1', py - 4).attr('x2', px + 46).attr('y2', py - 16).attr('stroke', '#7b8794');
      svg.append('text').attr('x', px + 50).attr('y', py - 22).attr('font-size', 11.5).attr('fill', '#33475b').attr('font-weight', 700)
        .text(`${pct(peak.three_share)}: the highest share`);
      svg.append('text').attr('x', px + 50).attr('y', py - 8).attr('font-size', 11).attr('fill', '#4d5e70')
        .text(`down ${peak.deficit}, ${peak.time} min left`);
    }

    // End-of-line labels, nudged apart so they never overlap.
    const ends = TIMES.map((t) => ({ t, d: rows.find((d) => d.deficit === DEFICITS.at(-1) && d.time === t) })).filter((e) => e.d)
      .map((e) => ({ ...e, y: y(e.d.three_share) })).sort((a, b) => a.y - b.y);
    for (let i = 1; i < ends.length; i++) ends[i].y = Math.max(ends[i].y, ends[i - 1].y + 15);
    const labelY = Object.fromEntries(ends.map((e) => [e.t, e.y]));
    const line = d3.line().x((d) => x(d.deficit)).y((d) => y(d.three_share)).curve(d3.curveMonotoneX);
    for (const t of TIMES) {
      const series = DEFICITS.map((g) => rows.find((d) => d.deficit === g && d.time === t)).filter(Boolean);
      const on = !emph || emph === t;
      const g = svg.append('g').attr('opacity', on ? 1 : 0.18);
      g.append('path').datum(series).attr('d', line).attr('fill', 'none').attr('stroke', TIME_COLORS[t])
        .attr('stroke-width', emph === t ? 4 : 3).attr('stroke-linejoin', 'round');
      const last = series[series.length - 1];
      g.append('text').attr('x', x(last.deficit) + 12).attr('y', labelY[t] ?? y(last.three_share)).attr('dominant-baseline', 'middle')
        .attr('font-size', 12).attr('font-weight', 700).attr('fill', TIME_COLORS[t]).text(`${t} min`);
      const dots = g.selectAll('g.pt').data(series).join('g').attr('class', 'pt')
        .attr('transform', (d) => `translate(${x(d.deficit)},${y(d.three_share)})`)
        .on('mouseenter', (_, d) => (hovered = d)).on('mouseleave', () => (hovered = null));
      asButton(dots, {
        label: (d) => `Down ${d.deficit} with ${d.time} minutes left: ${pct(d.three_share)} of ${d.attempts} attempts were threes`,
        key: (d) => `${d.deficit}|${d.time}`,
        onActivate: (d) => { focusKey = `${d.deficit}|${d.time}`; selectState(d.deficit, d.time); }
      });
      dots.append('circle').attr('r', 14).attr('fill', 'transparent'); // larger hit area
      dots.append('circle').attr('r', (d) => (isSelected(d) ? 8 : 5)).attr('fill', TIME_COLORS[t])
        .attr('stroke', (d) => (isSelected(d) ? '#17273b' : '#fff')).attr('stroke-width', (d) => (isSelected(d) ? 3 : 2));
    }
    restoreFocus(node, focusKey);
    focusKey = null;
  }
  $effect(() => render(data, emphasis, selection.deficit, selection.time));
</script>

<div class="chart-controls">
  <div class="chart-legend" role="group" aria-label="Highlight a time window">
    {#each TIMES as t}
      <button class="legend-entry legend-button" class:active={emphasis === t} aria-pressed={pinnedTime === t}
        onclick={() => (pinnedTime = pinnedTime === t ? null : t)}>
        <i style={`background:${TIME_COLORS[t]}`}></i>{t} min left
      </button>
    {/each}
  </div>
</div>
<div class="chart-surface scroll-x"><svg bind:this={node} role="group" aria-label="Line chart: three-point share of field-goal attempts by points behind, one line per time window"></svg></div>
<div class="chart-detail" aria-live="polite">
  {#if shown}
    Down <strong>{shown.deficit} pts</strong> with <strong>{shown.time} min</strong> left: <strong>{pct(shown.three_share)}</strong> of {shown.attempts.toLocaleString()} field-goal attempts were threes ({shown.three_attempts.toLocaleString()} 3PA).
  {:else}
    Hover a point for exact values; click it to select that game state in every chart. Use the legend to highlight one time window.
  {/if}
</div>
