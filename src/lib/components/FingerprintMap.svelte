<script>
  // J4-R Tactical Fingerprint Map (novel view). One glyph per (deficit, time) game state:
  //   three spokes = three-point share, FGA per minute, turnovers per minute
  //   outer arc    = share of trailing team-games that came back to win
  // Each spoke is min-max scaled across the 16 states, so a long spoke means "high compared
  // with the other game states", not a raw unit. Exact values appear in the side panel.
  import * as d3 from 'd3';
  import { DEFICITS, TIMES, selection, selectState, isSelected, asButton, restoreFocus, pct, num2 } from '$lib/state.svelte.js';

  let { data = [] } = $props();
  let node;
  let focusKey = null;
  let hovered = $state(null);
  const metrics = [
    { key: 'three_share', label: '3PT share of attempts', color: '#c8441d', fmt: pct },
    { key: 'shots_per_min', label: 'Field-goal attempts / min', color: '#1f8a8a', fmt: num2 },
    { key: 'turnovers_per_min', label: 'Turnovers / min', color: '#6a5fc1', fmt: num2 }
  ];
  const ARC = '#e0784f';
  const shown = $derived(hovered ?? data.find((d) => isSelected(d)));
  const extremes = $derived(Object.fromEntries(metrics.map((m) => [m.key, d3.extent(data, (d) => d[m.key])])));

  function render(rows) {
    if (!node || !rows?.length) return;
    const svg = d3.select(node);
    svg.selectAll('*').remove();
    const W = 720, H = 470, left = 96, top = 52, cw = 151, ch = 96;
    const angles = [-Math.PI / 2, Math.PI / 6, (5 * Math.PI) / 6];
    svg.attr('viewBox', `0 0 ${W} ${H}`);
    svg.append('text').attr('x', 8).attr('y', 30).attr('fill', '#4d5e70').attr('font-size', 11).attr('font-weight', 700).attr('letter-spacing', 1).text('POINTS BEHIND');
    DEFICITS.forEach((d, i) => svg.append('text').attr('x', left - 14).attr('y', top + i * ch + ch / 2 + 5)
      .attr('fill', '#23374c').attr('font-size', 13).attr('text-anchor', 'end').attr('font-weight', 600).text(`${d} pts`));
    TIMES.forEach((t, j) => svg.append('text').attr('x', left + j * cw + cw / 2).attr('y', 30)
      .attr('fill', '#23374c').attr('font-size', 13).attr('text-anchor', 'middle').attr('font-weight', 600).text(`${t} min`));
    // Min–max scale each indicator across the 16 cells: lowest value at the inner end of the
    // spoke, highest at the outer ring.
    const scales = metrics.map(({ key }) => {
      const [lo, hi] = d3.extent(rows, (d) => d[key]);
      return d3.scaleLinear().domain(lo === hi ? [0, hi || 1] : [lo, hi]).range([6, 31]).clamp(true);
    });
    const dim = selection.deficit !== null;
    const cells = svg.append('g').selectAll('g').data(rows).join('g')
      .attr('class', 'glyph')
      .attr('transform', (d) => `translate(${left + TIMES.indexOf(d.time) * cw},${top + DEFICITS.indexOf(d.deficit) * ch})`)
      .attr('opacity', (d) => (!dim || isSelected(d) ? 1 : 0.4))
      .on('mouseenter', (_, d) => (hovered = d)).on('mouseleave', () => (hovered = null));
    asButton(cells, {
      label: (d) => `Down ${d.deficit} with ${d.time} minutes left: ${pct(d.three_share)} threes, ${num2(d.shots_per_min)} attempts per minute, ${num2(d.turnovers_per_min)} turnovers per minute, ${pct(d.comeback_rate)} came back to win`,
      key: (d) => `${d.deficit}|${d.time}`,
      onActivate: (d) => { focusKey = `${d.deficit}|${d.time}`; selectState(d.deficit, d.time); }
    });
    cells.append('rect').attr('x', 4).attr('y', 4).attr('width', cw - 9).attr('height', ch - 8).attr('rx', 12)
      .attr('fill', (d) => (isSelected(d) ? '#fff6f1' : '#f7f9fb'))
      .attr('stroke', (d) => (isSelected(d) ? '#17273b' : '#e3e8ef')).attr('stroke-width', (d) => (isSelected(d) ? 2.5 : 1));
    const cx = cw / 2, cy = ch / 2;
    cells.each(function (d) {
      const g = d3.select(this);
      [18.5, 31].forEach((r) => g.append('circle').attr('cx', cx).attr('cy', cy).attr('r', r).attr('fill', 'none').attr('stroke', '#cbd5df').attr('stroke-dasharray', '3 3'));
      angles.forEach((a) => g.append('line').attr('x1', cx).attr('y1', cy).attr('x2', cx + 31 * Math.cos(a)).attr('y2', cy + 31 * Math.sin(a)).attr('stroke', '#d0d9e3'));
      const pts = angles.map((a, k) => {
        const r = scales[k](d[metrics[k].key]);
        return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
      });
      g.append('path').attr('d', d3.line().curve(d3.curveLinearClosed)(pts)).attr('fill', '#48a6a4').attr('fill-opacity', 0.25).attr('stroke', '#157b84').attr('stroke-width', 1.5);
      pts.forEach(([px, py], k) => g.append('circle').attr('cx', px).attr('cy', py).attr('r', 3.3).attr('fill', metrics[k].color));
      const rate = Math.min(1, Number(d.comeback_rate) || 0);
      g.append('path').attr('transform', `translate(${cx},${cy})`)
        .attr('d', d3.arc().innerRadius(35).outerRadius(39).startAngle(0).endAngle(2 * Math.PI)).attr('fill', '#edf0f3');
      g.append('path').attr('transform', `translate(${cx},${cy})`)
        .attr('d', d3.arc().innerRadius(35).outerRadius(39).startAngle(0).endAngle(2 * Math.PI * rate)).attr('fill', ARC);
      g.append('text').attr('x', cw - 12).attr('y', ch - 12).attr('text-anchor', 'end').attr('font-size', 10.5).attr('fill', '#4d5e70')
        .text(`${Math.round(rate * 100)}%`);
    });
    svg.append('text').attr('x', left + (TIMES.length * cw) / 2).attr('y', H - 10).attr('text-anchor', 'middle').attr('fill', '#4d5e70').attr('font-size', 12)
      .text('Time left in the fourth quarter  →  clock running out');
    restoreFocus(node, focusKey);
    focusKey = null;
  }
  $effect(() => render(data, selection.deficit, selection.time));
</script>

<div class="fingerprint-shell">
  <div class="fingerprint-chart scroll-x"><svg bind:this={node} role="group" aria-label="Tactical fingerprint glyphs for 16 game states. Each glyph is a button that selects that game state."></svg></div>
  <aside class="fingerprint-explainer">
    <span class="eyebrow">HOW TO READ A GLYPH</span>
    <div class="glyph-key" aria-hidden="true">
      <svg viewBox="0 0 200 128" width="200" height="128">
        <circle cx="100" cy="66" r="31" fill="none" stroke="#cbd5df" stroke-dasharray="3 3" />
        <path d="M100 66 m0 -37 a37 37 0 1 1 -32 55" fill="none" stroke={ARC} stroke-width="4" />
        <line x1="100" y1="66" x2="100" y2="35" stroke="#d0d9e3" /><line x1="100" y1="66" x2="127" y2="81.5" stroke="#d0d9e3" /><line x1="100" y1="66" x2="73" y2="81.5" stroke="#d0d9e3" />
        <path d="M100 39 L122 78.5 L84 75" fill="#48a6a4" fill-opacity=".25" stroke="#157b84" />
        <circle cx="100" cy="39" r="3.5" fill="#c8441d" /><circle cx="122" cy="78.5" r="3.5" fill="#1f8a8a" /><circle cx="84" cy="75" r="3.5" fill="#6a5fc1" />
        <text x="100" y="14" text-anchor="middle" font-size="10.5" fill="#c8441d">3PT share</text>
        <text x="160" y="104" text-anchor="middle" font-size="10.5" fill="#1f8a8a">attempts / min</text>
        <text x="40" y="104" text-anchor="middle" font-size="10.5" fill="#6a5fc1">turnovers / min</text>
        <text x="152" y="40" font-size="10.5" fill="#b4532f">win arc</text>
      </svg>
    </div>
    <p>Each spoke runs from the <em>lowest</em> value of that indicator among the 16 game states (centre) to the <em>highest</em> (dashed ring). A bigger triangle means a more aggressive offence than in other states. The orange arc fills clockwise with the share of trailing teams that came back to win.</p>
    <div class="selected-state" aria-live="polite">
      {#if shown}
        <span class="eyebrow">{hovered ? 'HOVERED' : 'SELECTED'} GAME STATE</span>
        <h4>Down {shown.deficit} pts · {shown.time} min left</h4>
        {#each metrics as m}
          <div class="metric-stat"><span><i style={`background:${m.color}`}></i>{m.label}</span><strong>{m.fmt(shown[m.key])}</strong></div>
        {/each}
        <div class="metric-stat"><span><i class="arc-dot"></i>Came back to win</span><strong>{pct(shown.comeback_rate)}</strong></div>
        <div class="metric-stat"><span>Sample</span><strong>{shown.shots.toLocaleString()} FGA · {shown.state_games} team-games</strong></div>
      {:else}
        <p class="muted">Hover or click a glyph to see its exact values. Range across all states: 3PT share {pct(extremes.three_share?.[0])}–{pct(extremes.three_share?.[1])}, attempts/min {num2(extremes.shots_per_min?.[0])}–{num2(extremes.shots_per_min?.[1])}, turnovers/min {num2(extremes.turnovers_per_min?.[0])}–{num2(extremes.turnovers_per_min?.[1])}.</p>
      {/if}
    </div>
  </aside>
</div>

<style>
  .glyph-key { display: flex; justify-content: center; margin: 6px 0 4px; }
  .metric-stat span { display: inline-flex; align-items: center; gap: 8px; }
  .metric-stat i { width: 9px; height: 9px; border-radius: 50%; display: inline-block; }
  .metric-stat .arc-dot { background: transparent; border: 2.5px solid #e0784f; width: 10px; height: 10px; }
</style>
