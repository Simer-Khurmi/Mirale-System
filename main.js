const $ = (sel)=>document.querySelector(sel);
const api = (path, opts={}) => fetch(path, {headers: {'Content-Type':'application/json'}, ...opts}).then(r=>r.json());

async function loadDevices(){
  const list = await api('/api/devices');
  const container = $('#devices');
  container.innerHTML = '';
  for(const d of list){
    const el = document.createElement('div');
    el.className='dev';
    el.innerHTML = `<div>
        <div><strong>${d.name}</strong> <span class="badge">${d.type}</span></div>
        <div class="meta">${d.id} • room: ${d.room} • topic: ${d.topic}</div>
      </div>
      <div>
        <button data-id="${d.id}" data-action="power">Power</button>
      </div>`;
    container.appendChild(el);
  }
  container.addEventListener('click', async (e)=>{
    const b = e.target.closest('button'); if(!b) return;
    const id = b.dataset.id;
    await api('/api/command', {method:'POST', body: JSON.stringify({device_id:id, action:'power', params:{toggle:true}})});
  }, {once:true});
}

async function parseNL(){
  const text = $('#nl').value.trim();
  if(!text) return;
  const parsed = await api('/api/parse', {method:'POST', body: JSON.stringify({text})});
  $('#parsed').textContent = JSON.stringify(parsed, null, 2);

  // Example: automatically dispatch if clearly resolved
  if(parsed.intent !== 'unknown' && parsed.confidence >= 0.75){
    // naive routing: pick a device by heuristic
    const devices = await api('/api/devices');
    const match = devices.find(d => (parsed.device ? d.type===parsed.device : true) && (parsed.room ? d.room.includes(parsed.room) : true));
    if(match){
      let action = 'power';
      let params = {};
      if(parsed.action === 'power_on') { action='power'; params={value:true}; }
      else if(parsed.action === 'power_off') { action='power'; params={value:false}; }
      else if(parsed.action === 'set_temperature') { action='temperature'; params={target: parsed.params?.target}; }
      else if(parsed.action === 'set_swing') { action='swing_timer'; params={seconds: parsed.params?.timer ?? 1800}; }
      else if(parsed.action === 'set_scene') { action='scene'; params={name: parsed.params?.scene || 'movie'}; }

      await api('/api/command', {method:'POST', body: JSON.stringify({device_id: match.id, action, params})});
    }
  }
}

async function loadLogs(){
  const logs = await api('/api/logs');
  $('#logs').textContent = logs.map(l => `[${l.type}] ${JSON.stringify(l.payload)}`).join('\n');
}

// WebSocket realtime
function connectWS(){
  const ws = new WebSocket((location.protocol==='https:'?'wss':'ws')+'://'+location.host+'/ws');
  ws.onopen = ()=>{};
  ws.onmessage = (ev)=>{
    try{
      const data = JSON.parse(ev.data);
      if(data.type==='mqtt'){
        // append to logs
        const pre = $('#logs');
        pre.textContent += `\n[mqtt] ${JSON.stringify(data.data)}`;
        pre.scrollTop = pre.scrollHeight;
      }
    }catch{}
  };
  ws.onclose = ()=>{
    $('#wsDot').style.background = '#f87171';
    setTimeout(connectWS, 1000);
  };
}

document.addEventListener('DOMContentLoaded', ()=>{
  $('#parseBtn').addEventListener('click', parseNL);
  loadDevices();
  loadLogs();
  connectWS();
  setInterval(loadLogs, 4000);
});
