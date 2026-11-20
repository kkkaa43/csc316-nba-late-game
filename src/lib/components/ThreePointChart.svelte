<script>
  import * as d3 from 'd3';
  let { data = [] } = $props();
  let node;
  let active = $state('All time windows');
  let hovered = $state(null);
  const times = ['9–12', '6–9', '3–6', '0–3'];
  const groups = ['1–3', '4–6', '7–10', '11+'];
  const colors = {'9–12':'#7a99b4','6–9':'#48a6a4','3–6':'#f1bd74','0–3':'#ec7148'};
  function render(rows, selectedTime) {
    if (!node || !rows?.length) return;
    const svg=d3.select(node); svg.selectAll('*').remove();
    const W=720,H=352,m={top:24,right:28,bottom:58,left:66};
    svg.attr('viewBox',`0 0 ${W} ${H}`).attr('role','img').attr('aria-label','Line chart of three-point shot share by deficit and fourth-quarter time window');
    const x=d3.scalePoint().domain(groups).range([m.left,W-m.right]).padding(.5);
    // Zoom the y-axis to the observed range (snapped to 5% steps) so differences of a few
    // percentage points stay visible; the axis label notes that it does not start at 0%.
    const [lo,hi]=d3.extent(rows.filter(d=>Number.isFinite(d.three_share)),d=>d.three_share);
    const yMin=Math.max(0,Math.floor((lo-.02)*20)/20), yMax=Math.min(1,Math.ceil((hi+.02)*20)/20);
    const y=d3.scaleLinear().domain([yMin,yMax]).range([H-m.bottom,m.top]);
    const yTicks=d3.range(yMin,yMax+1e-9,.05);
    const body=svg.append('g');
    body.append('g').selectAll('line').data(yTicks).join('line')
      .attr('x1',m.left).attr('x2',W-m.right).attr('y1',d=>y(d)).attr('y2',d=>y(d)).attr('stroke','#dfe6ec').attr('stroke-dasharray',(d,i)=>i===0?'0':'3,6');
    body.append('g').attr('transform',`translate(0,${H-m.bottom})`).call(d3.axisBottom(x).tickSize(0)).call(a=>a.select('.domain').attr('stroke','#8d9aac')).call(a=>a.selectAll('text').attr('dy','1.65em').attr('fill','#637288').attr('font-size',13));
    body.append('g').attr('transform',`translate(${m.left},0)`).call(d3.axisLeft(y).tickValues(yTicks).tickFormat(d3.format('.0%')).tickSize(0)).call(a=>a.select('.domain').remove()).call(a=>a.selectAll('text').attr('dx','-.6em').attr('fill','#637288').attr('font-size',12));
    body.append('text').attr('x',(m.left+W-m.right)/2).attr('y',H-6).attr('text-anchor','middle').attr('fill','#536277').attr('font-size',12).text('Score deficit before the attempt (points)');
    body.append('text').attr('transform',`translate(18,${(H-m.bottom+m.top)/2}) rotate(-90)`).attr('text-anchor','middle').attr('fill','#536277').attr('font-size',12).text(yMin>0?`Three-point share of FGA (axis starts at ${Math.round(yMin*100)}%)`:'Three-point share of FGA');
    const line=d3.line().defined(d=>Number.isFinite(d.three_share)).x(d=>x(d.deficit)).y(d=>y(d.three_share)).curve(d3.curveMonotoneX);
    for(const t of times){
      const s=groups.map(g=>rows.find(d=>d.deficit===g && d.time===t) ?? {deficit:g,three_share:NaN});
      const visible=selectedTime==='All time windows'||selectedTime===t;
      body.append('path').datum(s).attr('d',line).attr('fill','none').attr('stroke',colors[t]).attr('stroke-width',selectedTime===t?4:3).attr('opacity',visible?1:.12).attr('stroke-linejoin','round');
      body.selectAll('.dot'+times.indexOf(t)).data(s.filter(d=>Number.isFinite(d.three_share))).join('circle')
        .attr('cx',d=>x(d.deficit)).attr('cy',d=>y(d.three_share)).attr('r',selectedTime===t?6:4.6).attr('fill',colors[t])
        .attr('stroke','#fff').attr('stroke-width',2).attr('opacity',visible?1:.12)
        .style('cursor',visible?'pointer':'default')
        .on('mouseenter',(_,d)=>{if(visible)hovered={...d, time:t};})
        .on('mouseleave',()=>hovered=null)
        .append('title').text(d=>`${t} min left, ${d.deficit} behind: ${(d.three_share*100).toFixed(1)}% (n=${d.attempts})`);
    }
  }
  $effect(()=>render(data,active));
</script>
<div class="chart-controls"><div class="chart-legend">
 {#each times as t}<span class="legend-entry"><i style={`background:${colors[t]}`}></i>{t} min</span>{/each}
</div><label class="select-wrap"><span class="sr-only">Highlight time window</span><select bind:value={active}><option>All time windows</option>{#each times as t}<option value={t}>{t} minutes left</option>{/each}</select></label></div>
<div class="chart-surface"><svg bind:this={node}></svg></div>
<div class="chart-detail" aria-live="polite">{#if hovered}<strong>{(hovered.three_share*100).toFixed(1)}% 3PA share</strong> with {hovered.time} minutes left and {hovered.deficit} point deficit · {hovered.attempts} field-goal attempts{:else}Hover over a point to inspect the percentage and sample size.{/if}</div>
