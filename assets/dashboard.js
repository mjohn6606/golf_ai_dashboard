// assets/dashboard.js
// Loads data from /data/*.json and renders charts + simple AI insight
async function loadJSON(path){ try{ const r = await fetch(path+'?cachebust='+Date.now()); return await r.json(); }catch(e){ console.warn('load',path,e); return null; } }

function elKPI(title, value){ const d = document.createElement('div'); d.className='kpi'; d.innerHTML=`<div class="muted">${title}</div><div style="font-weight:700;font-size:18px">${value}</div>`; return d; }

async function render(){ const rapsodo = await loadJSON('data/sample_rapsodo.json'); const swing = await loadJSON('data/sample_swing_analysis.json'); const mobility = await loadJSON('data/sample_mobility.json'); const kpiRow = document.getElementById('kpiRow'); kpiRow.innerHTML=''; if(rapsodo){ const avgCarry = Math.round(rapsodo.reduce((a,b)=>a+(b.Carry||0),0)/(rapsodo.length||1)); kpiRow.appendChild(elKPI('Avg Carry (yds)', avgCarry)); kpiRow.appendChild(elKPI('Clubs Logged', rapsodo.length)); } if(swing){ const frames = swing.frames||0; kpiRow.appendChild(elKPI('Swing Frames', frames)); } if(mobility){ const last = mobility[mobility.length-1]; if(last) kpiRow.appendChild(elKPI('Latest Trunk Rot', last.trunk_rotation_deg+'°')); }

  // Rapsodo chart (avg carry by club)
  if(rapsodo && rapsodo.length){
    const labels = rapsodo.map(r=>r.Club||r.club||'Unknown'); const data = rapsodo.map(r=>r.Carry||r.carry||0);
    new Chart(document.getElementById('carryChart'),{type:'bar',data:{labels, datasets:[{label:'Carry (yds)',data,backgroundColor:'rgba(14,165,163,0.6)'}]}});
  }

  // Swing rotation chart
  if(swing && swing.raw && swing.raw.length){
    const labels = swing.raw.map((s,i)=>i+1); const data = swing.raw.map(s=>s.shoulder_angle || s.rotation || 0);
    new Chart(document.getElementById('swingRotationChart'),{type:'line',data:{labels,datasets:[{label:'Shoulder rotation (deg)',data,borderColor:'#0ea5a3',tension:0.2}]}});
    document.getElementById('swingSummary').textContent = swing.summary || 'Swing summary: ' + (swing.frames? (swing.frames+' frames') : 'no summary');
  }

  // Mobility chart
  if(mobility && mobility.length){
    const labels = mobility.map(m=>m.date); const trunk = mobility.map(m=>m.trunk_rotation_deg||0);
    new Chart(document.getElementById('mobilityChart'),{type:'line',data:{labels,datasets:[{label:'Trunk Rotation (deg)',data:trunk,borderColor:'#3b82f6',tension:0.2}]}});
  }

  // Quick AI insight (rule-based)
  const aiBox = document.getElementById('aiInsight'); aiBox.textContent = 'Analyzing...';
  let insights = [];
  if(swing && swing.shoulder_mean && swing.shoulder_mean < 40) insights.push('Increase thoracic rotation — practice open-book and seated torso turns.');
  if(mobility && mobility.length && mobility[mobility.length-1].trunk_rotation_deg < 40) insights.push('Mobility: trunk rotation low — add daily 90/90 and thoracic rotations.');
  if(rapsodo && rapsodo.length){ const avg = Math.round(rapsodo.reduce((a,b)=>a+(b.Carry||0),0)/(rapsodo.length||1)); if(avg < 200) insights.push('Consider strength work on posterior chain to gain distance.'); }
  if(!insights.length) insights.push('No urgent issues detected. Keep the plan.');
  aiBox.innerHTML = insights.map(i=>'<div>• '+i+'</div>').join('');
}

document.addEventListener('DOMContentLoaded', render);
