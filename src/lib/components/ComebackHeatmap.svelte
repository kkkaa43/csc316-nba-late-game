<script>
  import * as d3 from 'd3';
  let {data=[]}=$props(); let node;let selected=$state(null);
  const ds=['1–3','4–6','7–10','11+'];const ts=['9–12','6–9','3–6','0–3'];
  function render(rows){
    if(!node||!rows?.length)return;
    const svg=d3.select(node);svg.selectAll('*').remove();
    const W=650,H=352,m={l:94,t:42,r:24,b:54};
    svg.attr('viewBox',`0 0 ${W} ${H}`).attr('role','img').attr('aria-label','Heatmap of historical trailing team wins across deficit and remaining-time buckets');
    const x=d3.scaleBand().domain(ts).range([m.l,W-m.r]).padding(.06);
    const y=d3.scaleBand().domain(ds).range([m.t,H-m.b]).padding(.08);
    const color=d3.scaleSequential(d3.interpolateRgbBasis(['#f4eee9','#f0aa75','#d66b51','#853c53'])).domain([0,.5]);
    const marks=svg.append('g');
    for(let i=0;i<4;i++)for(let j=0;j<4;j++){
      const d=rows.find(a=>a.deficit===ds[i]&&a.time===ts[j]);
      const has=d&&Number.isFinite(d.comeback_rate);
      marks.append('rect').attr('x',x(ts[j])).attr('y',y(ds[i])).attr('width',x.bandwidth()).attr('height',y.bandwidth()).attr('rx',8)
        .attr('fill',has?color(d.comeback_rate):'#e7ebf0').attr('stroke','white').attr('stroke-width',1.5)
        .style('cursor',has?'pointer':'default').on('click',()=>{if(has)selected=d;})
        .append('title').text(has?`${(d.comeback_rate*100).toFixed(1)}% historical wins; ${d.state_games} state-games`:'No observations');
      marks.append('text').attr('x',x(ts[j])+x.bandwidth()/2).attr('y',y(ds[i])+y.bandwidth()/2-1).attr('text-anchor','middle').attr('dominant-baseline','middle')
        .attr('font-weight','700').attr('font-size',19).attr('fill',has&&d.comeback_rate>.17?'#fff':'#5c3541').attr('pointer-events','none')
        .text(has?(100*d.comeback_rate).toFixed(1)+'%':'—');
      marks.append('text').attr('x',x(ts[j])+x.bandwidth()/2).attr('y',y(ds[i])+y.bandwidth()/2+20).attr('text-anchor','middle')
        .attr('font-size',10).attr('fill',has&&d.comeback_rate>.17?'#fff':'#775e66').attr('pointer-events','none')
        .text(has?`n = ${d.state_games}`:'No data');
    }
    svg.append('g').attr('transform',`translate(0,${H-m.b+7})`).call(d3.axisBottom(x).tickSize(0)).call(a=>a.select('.domain').remove()).call(a=>a.selectAll('text').attr('fill','#667789').attr('font-size',12));
    svg.append('g').attr('transform',`translate(${m.l-8},0)`).call(d3.axisLeft(y).tickSize(0)).call(a=>a.select('.domain').remove()).call(a=>a.selectAll('text').attr('fill','#667789').attr('font-size',12));
    svg.append('text').attr('x',(m.l+W-m.r)/2).attr('y',H-5).attr('text-anchor','middle').attr('font-size',11).attr('fill','#667789').text('Time remaining in the fourth quarter (minutes)');
    svg.append('text').attr('x',14).attr('y',H/2).attr('text-anchor','middle').attr('transform',`rotate(-90,14,${H/2})`).attr('font-size',11).attr('fill','#667789').text('Score deficit (points)');
  }
  $effect(()=>render(data));
</script>
<div class="heatmap-wrap"><svg bind:this={node}></svg></div>
<div class="chart-detail" aria-live="polite">{#if selected}When trailing by <strong>{selected.deficit} points</strong> with {selected.time} minutes left, <strong>{(100*selected.comeback_rate).toFixed(1)}%</strong> of {selected.state_games} observed team-games ended in a win.{:else}Click a cell to inspect historical win rates and sample sizes. Each team-game is counted once per cell.{/if}</div>
