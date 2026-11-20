<script>
  // S4: shooting accuracy of the trailing team by (deficit, time). Colour is diverging around
  // the all-states average, so cells that are worse than usual stand out in orange.
  import * as d3 from 'd3';
  import { DEFICITS, TIMES, selection, selectState, isSelected, asButton, restoreFocus, pct, wilson } from '$lib/state.svelte.js';

  let { data = [] } = $props();
  let node;
  let focusKey = null;
  let metric = $state('fg');
  const M = {
    fg: { rate: 'fg_pct', made: 'makes', att: 'attempts', name: 'Field-goal %', short: 'FG%' },
    three: { rate: 'three_pct', made: 'three_makes', att: 'three_attempts', name: 'Three-point %', short: '3P%' }
  };
  const cfg = $derived(M[metric]);
  const average = $derived(d3.sum(data, (d) => d[cfg.made]) / d3.sum(data, (d) => d[cfg.att]));
  const current = $derived(data.find((d) => isSelected(d)));
  // Diverging scale in percentage points from the average: orange = below, blue = above.
  const color = d3.scaleDiverging(d3.interpolateRgbBasis(['#c8441d', '#f2b89a', '#f4f4f2', '#a9c6dd', '#2f6b98'])).domain([-0.07, 0, 0.07]).clamp(true);

  function render(rows, c, avg) {
    if (!node || !rows?.length) return;
    const svg = d3.select(node);
    svg.selectAll('*').remove();
    const W = 650, H = 360, m = { l: 96, t: 16, r: 18, b: 58 };
    svg.attr('viewBox', `0 0 ${W} ${H}`);
    const x = d3.scaleBand().domain(TIMES).range([m.l, W - m.r]).padding(0.06);
    const y = d3.scaleBand().domain(DEFICITS).range([m.t, H - m.b]).padding(0.08);
    const dim = selection.deficit !== null;
    const cells = svg.append('g').selectAll('g').data(rows).join('g').attr('class', 'cell')
      .attr('transform', (d) => `translate(${x(d.time)},${y(d.deficit)})`);
    asButton(cells, {
      label: (d) => `Down ${d.deficit} with ${d.time} minutes left: ${c.name} ${pct(d[c.rate])} on ${d[c.att]} attempts`,
      key: (d) => `${d.deficit}|${d.time}`,
      onActivate: (d) => { focusKey = `${d.deficit}|${d.time}`; selectState(d.deficit, d.time); }
    });
    cells.append('rect').attr('width', x.bandwidth()).attr('height', y.bandwidth()).attr('rx', 8)
      .attr('fill', (d) => color(d[c.rate] - avg))
      .attr('opacity', (d) => (!dim || isSelected(d) ? 1 : 0.45))
      .attr('stroke', (d) => (isSelected(d) ? '#17273b' : '#fff')).attr('stroke-width', (d) => (isSelected(d) ? 3.5 : 1.5));
    const dark = (d) => Math.abs(d[c.rate] - avg) > 0.045;
    cells.append('text').attr('x', x.bandwidth() / 2).attr('y', y.bandwidth() / 2 - 3).attr('text-anchor', 'middle').attr('dominant-baseline', 'middle')
      .attr('font-size', 21).attr('font-weight', 700).attr('fill', (d) => (dark(d) ? '#fff' : '#1f2f40')).attr('pointer-events', 'none')
      .text((d) => (100 * d[c.rate]).toFixed(1) + '%');
    cells.append('text').attr('x', x.bandwidth() / 2).attr('y', y.bandwidth() / 2 + 19).attr('text-anchor', 'middle')
      .attr('font-size', 11).attr('fill', (d) => (dark(d) ? '#fff' : '#4d5e70')).attr('pointer-events', 'none')
      .text((d) => {
        const diff = 100 * (d[c.rate] - avg);
        return `${diff >= 0 ? '+' : '−'}${Math.abs(diff).toFixed(1)} pts · n=${d[c.att].toLocaleString()}`;
      });
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
  $effect(() => render(data, cfg, average, selection.deficit, selection.time));
</script>

<div class="chart-controls">
  <div class="segmented" role="radiogroup" aria-label="Shooting measure">
    {#each Object.entries(M) as [k, v]}
      <button role="radio" aria-checked={metric === k} class:active={metric === k} onclick={() => (metric = k)}>{v.name}</button>
    {/each}
  </div>
  <div class="diverging-legend" aria-hidden="true">
    <span>below average</span><i></i><span>above average</span>
  </div>
</div>
<div class="heatmap-wrap scroll-x scroll-x-sm"><svg bind:this={node} role="group" aria-label="Heatmap of trailing-team shooting accuracy by points behind and minutes left. Each cell is a button that selects that game state."></svg></div>
<div class="chart-detail" aria-live="polite">
  {#if current}
    {@const ci = wilson(current[cfg.made], current[cfg.att])}
    Down <strong>{current.deficit} pts</strong> with <strong>{current.time} min</strong> left, trailing teams shot <strong>{pct(current[cfg.rate])}</strong> ({current[cfg.made].toLocaleString()} of {current[cfg.att].toLocaleString()}; 95% interval {pct(ci[0])}–{pct(ci[1])}). Average across all 16 states: {pct(average)}.
  {:else}
    Colours compare each state with the all-states average {cfg.short} of <strong>{pct(average)}</strong>. Click a cell for its 95% interval; switch to three-point % to see where the extra threes stop falling.
  {/if}
</div>

<style>
  .segmented { display: inline-flex; border: 1px solid #d5dee6; border-radius: 6px; overflow: hidden; }
  .segmented button { background: #f8fafb; border: 0; padding: 9px 14px; font-size: 12px; font-weight: 700; color: #4d5e70; cursor: pointer; }
  .segmented button + button { border-left: 1px solid #d5dee6; }
  .segmented button.active { background: #17273b; color: #fff; }
  .diverging-legend { display: flex; align-items: center; gap: 8px; font-size: 11px; color: #4d5e70; }
  .diverging-legend i { width: 120px; height: 10px; border-radius: 3px; background: linear-gradient(to right, #c8441d, #f2b89a, #f4f4f2, #a9c6dd, #2f6b98); }
</style>
