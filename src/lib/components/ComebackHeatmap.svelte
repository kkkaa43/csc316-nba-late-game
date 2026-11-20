<script>
  // Comeback-rate heatmap: share of trailing team-games in each (deficit, time) cell that won.
  // Click or press Enter on a cell to select that game state in every linked view.
  import * as d3 from 'd3';
  import { DEFICITS, TIMES, selection, selectState, isSelected, asButton, restoreFocus, pct } from '$lib/state.svelte.js';

  let { data = [] } = $props();
  let node;
  let focusKey = null;
  const color = d3.scaleSequential(d3.interpolateRgbBasis(['#f6efe9', '#f0aa75', '#d66b51', '#853c53'])).domain([0, 0.45]);
  const current = $derived(data.find((d) => isSelected(d)));

  function render(rows) {
    if (!node || !rows?.length) return;
    const svg = d3.select(node);
    svg.selectAll('*').remove();
    const W = 650, H = 360, m = { l: 96, t: 16, r: 18, b: 58 };
    svg.attr('viewBox', `0 0 ${W} ${H}`);
    const x = d3.scaleBand().domain(TIMES).range([m.l, W - m.r]).padding(0.06);
    const y = d3.scaleBand().domain(DEFICITS).range([m.t, H - m.b]).padding(0.08);
    const cells = svg.append('g').selectAll('g').data(rows.filter((d) => Number.isFinite(d.comeback_rate))).join('g')
      .attr('transform', (d) => `translate(${x(d.time)},${y(d.deficit)})`)
      .attr('class', 'cell');
    asButton(cells, {
      label: (d) => `Down ${d.deficit} points with ${d.time} minutes left: ${pct(d.comeback_rate)} of ${d.state_games} trailing team-games won`,
      key: (d) => `${d.deficit}|${d.time}`,
      onActivate: (d) => { focusKey = `${d.deficit}|${d.time}`; selectState(d.deficit, d.time); }
    });
    const dim = selection.deficit !== null;
    cells.append('rect').attr('width', x.bandwidth()).attr('height', y.bandwidth()).attr('rx', 8)
      .attr('fill', (d) => color(d.comeback_rate))
      .attr('opacity', (d) => (!dim || isSelected(d) ? 1 : 0.45))
      .attr('stroke', (d) => (isSelected(d) ? '#17273b' : '#fff'))
      .attr('stroke-width', (d) => (isSelected(d) ? 3.5 : 1.5));
    const dark = (d) => d.comeback_rate > 0.17;
    cells.append('text').attr('x', x.bandwidth() / 2).attr('y', y.bandwidth() / 2 - 3).attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle').attr('font-weight', 700).attr('font-size', 21)
      .attr('fill', (d) => (dark(d) ? '#fff' : '#4a2a33')).attr('pointer-events', 'none')
      .text((d) => (100 * d.comeback_rate).toFixed(1) + '%');
    cells.append('text').attr('x', x.bandwidth() / 2).attr('y', y.bandwidth() / 2 + 19).attr('text-anchor', 'middle')
      .attr('font-size', 11).attr('fill', (d) => (dark(d) ? '#fff' : '#5f4750')).attr('pointer-events', 'none')
      .text((d) => `${d.comeback_games} of ${d.state_games} won`);
    svg.append('g').attr('transform', `translate(0,${H - m.b + 6})`).call(d3.axisBottom(x).tickSize(0).tickFormat((t) => `${t} min`))
      .call((a) => a.select('.domain').remove()).call((a) => a.selectAll('text').attr('fill', '#4d5e70').attr('font-size', 13));
    svg.append('g').attr('transform', `translate(${m.l - 8},0)`).call(d3.axisLeft(y).tickSize(0).tickFormat((d) => `${d} pts`))
      .call((a) => a.select('.domain').remove()).call((a) => a.selectAll('text').attr('fill', '#4d5e70').attr('font-size', 13));
    svg.append('text').attr('x', (m.l + W - m.r) / 2).attr('y', H - 8).attr('text-anchor', 'middle').attr('font-size', 12).attr('fill', '#4d5e70')
      .text('Time left in the fourth quarter (minutes)  →  clock running out');
    svg.append('text').attr('x', 14).attr('y', (m.t + H - m.b) / 2).attr('text-anchor', 'middle')
      .attr('transform', `rotate(-90,14,${(m.t + H - m.b) / 2})`).attr('font-size', 12).attr('fill', '#4d5e70').text('Points behind');
    restoreFocus(node, focusKey);
    focusKey = null;
  }
  $effect(() => render(data, selection.deficit, selection.time));
</script>

<div class="heatmap-layout">
  <div class="heatmap-wrap scroll-x scroll-x-sm">
    <svg bind:this={node} role="group" aria-label="Comeback rate by points behind and minutes left. Each cell is a button that selects that game state."></svg>
  </div>
  <div class="legend-col" aria-hidden="true">
    <span class="legend-title">Trailing team won</span>
    <div class="ramp"></div>
    <div class="ramp-labels"><span>45%+</span><span>30%</span><span>15%</span><span>0%</span></div>
  </div>
</div>
<div class="chart-detail" aria-live="polite">
  {#if current}
    Down <strong>{current.deficit} points</strong> with <strong>{current.time} minutes</strong> left, <strong>{current.comeback_games} of {current.state_games}</strong> trailing team-games ({pct(current.comeback_rate)}) ended in a win. Click the cell again to clear.
  {:else}
    Click any cell (or Tab to it and press Enter) to follow that game state through every chart below. Read across a row: the same deficit becomes much harder to overcome as the clock runs down.
  {/if}
</div>

<style>
  .heatmap-layout { display: grid; grid-template-columns: minmax(0, 1fr) 80px; gap: 14px; align-items: center; max-width: 780px; margin: 0 auto; }
  .heatmap-layout .heatmap-wrap { width: 100%; max-width: none; margin: 0; }
  .legend-col { display: grid; grid-template-columns: 14px auto; grid-template-rows: auto 190px; column-gap: 8px; row-gap: 8px; }
  .legend-title { grid-column: 1 / -1; font-size: 10px; font-weight: 800; letter-spacing: .06em; color: #4d5e70; line-height: 1.3; }
  .ramp { border-radius: 4px; background: linear-gradient(to top, #f6efe9, #f0aa75, #d66b51, #853c53); }
  .ramp-labels { display: flex; flex-direction: column; justify-content: space-between; font-size: 11px; color: #4d5e70; }
  @media (max-width: 560px) {
    .heatmap-layout { grid-template-columns: 1fr; }
    .legend-col { grid-template-columns: 1fr; grid-template-rows: auto 12px auto; }
    .ramp { background: linear-gradient(to right, #f6efe9, #f0aa75, #d66b51, #853c53); }
    .ramp-labels { flex-direction: row-reverse; }
  }
</style>
