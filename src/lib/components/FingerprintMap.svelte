<script>
  import * as d3 from 'd3';
  let {data=[]}=$props();
  let node;
  let selected=$state(null);
  const ds=['1–3','4–6','7–10','11+'];
  const ts=['9–12','6–9','3–6','0–3'];
  const labels=['3-point share','Shot frequency','Turnover frequency'];
  const colors=['#e66f49','#289b9a','#7b82d7'];
  const fmt=d3.format('.1%');
  const fnum=v=>Number.isFinite(v)?v.toFixed(2):'N/A';
  function render(rows){
    if(!node||!rows?.length)return;
    const svg=d3.select(node);svg.selectAll('*').remove();
    const W=720,H=465,left=94,top=61,cw=149,ch=91,angles=[-Math.PI/2, Math.PI/6,5*Math.PI/6];
    svg.attr('viewBox',`0 0 ${W} ${H}`).attr('role','img').attr('aria-label','Tactical fingerprint glyphs across four deficit bands and four fourth-quarter time bands');
    svg.append('text').attr('x',18).attr('y',28).attr('fill','#75869a').attr('font-size',11).attr('letter-spacing',1.2).text('TRAILING BY');
    for(let i=0;i<4;i++) svg.append('text').attr('x',left-16).attr('y',top+i*ch+45).attr('fill','#23374c').attr('font-size',13).attr('text-anchor','end').attr('font-weight',600).text(ds[i]+' pts');
    for(let j=0;j<4;j++)svg.append('text').attr('x',left+j*cw+cw/2).attr('y',33).attr('fill','#23374c').attr('font-size',13).attr('text-anchor','middle').attr('font-weight',600).text(ts[j]+' min');
    // Min–max scale each indicator across the 16 cells: the lowest observed value sits at the
    // inner ring, the highest at the outer ring. Dividing by the max alone squeezed real-data
    // spokes into 77–100% of full length, so every glyph looked identical.
    const spokeScales=['three_share','shots_per_min','turnovers_per_min'].map(k=>{
      const [lo,hi]=d3.extent(rows.filter(d=>Number.isFinite(d[k])),d=>d[k]);
      return d3.scaleLinear().domain(lo===hi?[0,hi||1]:[lo,hi]).range([6,31]).clamp(true);
    });
    const grid=svg.append('g');
    for(let i=0;i<4;i++)for(let j=0;j<4;j++){
      const d=rows.find(v=>v.deficit===ds[i]&&v.time===ts[j]);
      const x=left+j*cw,y=top+i*ch;
      const g=grid.append('g').attr('transform',`translate(${x},${y})`);
      g.append('rect').attr('x',4).attr('y',4).attr('width',cw-9).attr('height',ch-7).attr('rx',12).attr('fill','#f7f9fb').attr('stroke','#e3e8ef');
      if(!d) {g.append('text').attr('x',cw/2).attr('y',ch/2).attr('text-anchor','middle').attr('font-size',12).attr('fill','#95a0ad').text('No data');continue;}
      const cx=cw/2,cy=ch/2+3;
      [18,29].forEach(r=>g.append('circle').attr('cx',cx).attr('cy',cy).attr('r',r).attr('fill','none').attr('stroke','#cbd5df').attr('stroke-dasharray','3 3'));
      for(const angle of angles)g.append('line').attr('x1',cx).attr('y1',cy).attr('x2',cx+31*Math.cos(angle)).attr('y2',cy+31*Math.sin(angle)).attr('stroke','#d0d9e3');
      const metrics=[d.three_share,d.shots_per_min,d.turnovers_per_min];
      const nodes=angles.map((a,k)=>{const r=Number.isFinite(metrics[k])?spokeScales[k](metrics[k]):6;return [cx+r*Math.cos(a),cy+r*Math.sin(a)];});
      const path=d3.line().curve(d3.curveLinearClosed)(nodes);
      g.append('path').attr('d',path).attr('fill','#48a6a4').attr('fill-opacity',.26).attr('stroke','#157b84').attr('stroke-width',1.5);
      nodes.forEach(([px,py],k)=>g.append('circle').attr('cx',px).attr('cy',py).attr('r',3.1).attr('fill',colors[k]));
      const rate=Number(d.comeback_rate)||0;
      const arc=d3.arc().innerRadius(34).outerRadius(37).startAngle(-Math.PI/2).endAngle(-Math.PI/2+2*Math.PI*Math.min(1,rate));
      g.append('path').attr('transform',`translate(${cx},${cy})`).attr('d',arc).attr('fill','#e87651');
      g.append('circle').attr('cx',cx).attr('cy',cy).attr('r',1.8).attr('fill','#153249');
      g.append('rect').attr('x',4).attr('y',4).attr('width',cw-9).attr('height',ch-7).attr('rx',12).attr('fill','transparent').attr('stroke','transparent').attr('stroke-width',2).style('cursor','pointer')
       .on('mouseover',function(){d3.select(this).attr('stroke','#e87651');})
       .on('mouseout',function(){d3.select(this).attr('stroke','transparent');})
       .on('click',()=>selected=d).append('title').text(`Trailing ${d.deficit} with ${d.time} min: 3PA ${fmt(d.three_share)}, ${fnum(d.shots_per_min)} FGA/min, ${fnum(d.turnovers_per_min)} TO/min, ${fmt(d.comeback_rate)} won; n=${d.state_games} state-games`);
    }
    svg.append('text').attr('x',W/2).attr('y',H-11).attr('text-anchor','middle').attr('fill','#7d8d9d').attr('font-size',12).text('FOURTH-QUARTER TIME REMAINING  →');
  }
  $effect(()=>render(data));
</script>
<div class="fingerprint-shell">
 <div class="fingerprint-chart"><svg bind:this={node}></svg></div>
 <aside class="fingerprint-explainer">
  <span class="eyebrow">HOW TO READ THIS VIEW</span>
  <h3>Each game state has a signature.</h3>
  <p>Each triangle describes three offensive indicators. Each spoke runs from the lowest value <em>of that indicator</em> in the grid (center) to the highest (outer ring), so a longer spoke means a higher value compared with the other game states.</p>
  <div class="metric-key"><span><i style="background:#e66f49"></i>Three-point attempt share</span><span><i style="background:#289b9a"></i>Field-goal attempts / minute</span><span><i style="background:#7b82d7"></i>Turnovers / minute</span><span><i class="key-arc"></i>Outer orange arc: comeback rate</span></div>
  <div class="selected-state" aria-live="polite">
   {#if selected}
    <span class="eyebrow">SELECTED GAME STATE</span><h4>{selected.deficit} points behind · {selected.time} min left</h4>
    <div class="metric-stat"><span>3PT attempt share</span><strong>{fmt(selected.three_share)}</strong></div>
    <div class="metric-stat"><span>Field-goal attempts/min</span><strong>{fnum(selected.shots_per_min)}</strong></div>
    <div class="metric-stat"><span>Turnovers/min</span><strong>{fnum(selected.turnovers_per_min)}</strong></div>
    <div class="metric-stat"><span>Eventual win rate</span><strong>{fmt(selected.comeback_rate)}</strong></div>
    <div class="metric-stat"><span>Unique game-state observations</span><strong>{selected.state_games ?? 'N/A'}</strong></div>
   {:else}<p class="muted">Click a fingerprint to reveal exact values, denominators, and historical game outcomes.</p>{/if}
  </div>
 </aside>
</div>
