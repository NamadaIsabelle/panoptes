// ---------------------------------------------------------------
// Panoptes — dashboard logic (live backend version)
//
// This dashboard is now a pure viewer: it polls the Flask API for
// state, logs, and alerts, and renders whatever it finds. Actual
// scan events are produced elsewhere — either backend/simulate_traffic.py
// standing in for hardware, or real scanners hitting POST /api/scan
// once those exist.
// ---------------------------------------------------------------

const state = {
  gates: {},           // gateId -> { ...gate, el }
  seenLogIds: new Set(),
  seenAlertIds: new Set(),
  firstPoll: true,
  backendUp: false,
};

const entranceListEl = document.getElementById('entranceList');
const logBody = document.getElementById('logBody');
const alertList = document.getElementById('alertList');
const emptyAlerts = document.getElementById('emptyAlerts');
const alertDot = document.getElementById('alertDot');
const alertStatus = document.getElementById('alertStatus');
const liveDot = document.querySelector('.dot.live');
const liveLabel = liveDot ? liveDot.nextSibling : null;

async function fetchJSON(path){
  const res = await fetch(`${API_BASE}${path}`);
  if(!res.ok) throw new Error(`${path} -> ${res.status}`);
  return res.json();
}

async function init(){
  updateClock();
  setInterval(updateClock, 1000);

  try {
    const gates = await fetchJSON('/api/gates');
    buildGateCards(gates);
    setBackendStatus(true);
  } catch (err) {
    console.error('Could not load gates from backend:', err);
    setBackendStatus(false);
    return; // nothing else works without gate config
  }

  poll();
  setInterval(poll, POLL_INTERVAL_MS);
}

function buildGateCards(gates){
  entranceListEl.innerHTML = '';
  gates.forEach(gate => {
    const card = document.createElement('div');
    card.className = 'entrance-card';
    card.innerHTML = `
      <div class="eye"><span class="letter">${gate.id}</span><div class="iris"></div><div class="pupil"></div></div>
      <div class="entrance-meta">
        <div class="name">${gate.name} <span class="type-tag ${gate.type}">${gate.type}</span></div>
        <div class="sub">idle</div>
      </div>
      <div class="count-pill">0 in</div>
    `;
    entranceListEl.appendChild(card);
    state.gates[gate.id] = { ...gate, el: card };
  });
}

function setBackendStatus(up){
  state.backendUp = up;
  if(up){
    liveDot?.classList.add('live');
    if(liveLabel) liveLabel.textContent = ' System live';
  } else {
    liveDot?.classList.remove('live');
    liveDot.style.background = 'var(--text-dimmer)';
    if(liveLabel) liveLabel.textContent = ' Backend offline';
  }
}

function fmtTime(unixSeconds){
  return new Date(unixSeconds * 1000).toTimeString().split(' ')[0];
}

function updateClock(){
  document.getElementById('clock').textContent = new Date().toTimeString().split(' ')[0];
}

function pulseGate(gateId, flagged){
  const gate = state.gates[gateId];
  if(!gate) return;
  gate.el.classList.add('scanning');
  if(flagged) gate.el.classList.add('flagged');
  gate.el.querySelector('.sub').textContent = 'scanning';
  setTimeout(() => {
    gate.el.classList.remove('scanning');
    gate.el.classList.remove('flagged');
    gate.el.querySelector('.sub').textContent = 'idle';
  }, 900);
}

function renderLogRow(log){
  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td class="mono">${fmtTime(log.timestamp)}</td>
    <td>${log.user}</td>
    <td>${state.gates[log.gate_id]?.name ?? log.gate_id}</td>
    <td><span class="dir ${log.direction}">${log.direction === 'in' ? 'ENTER' : 'EXIT'}</span></td>
    <td class="conf mono">${log.confidence}%</td>
    <td>${log.flagged ? 'Flagged' : 'Verified'}</td>
  `;
  logBody.prepend(tr);
  while(logBody.children.length > LOG_FETCH_LIMIT) logBody.removeChild(logBody.lastChild);
}

function renderAlert(alert){
  state.seenAlertIds.add(alert.id);
  emptyAlerts.style.display = 'none';
  const item = document.createElement('div');
  item.className = 'alert-item';
  item.innerHTML = `
    <div class="head"><span>${alert.title}</span><span>${fmtTime(alert.timestamp)}</span></div>
    <div class="body-text">${alert.body}</div>
  `;
  alertList.prepend(item);
  alertDot.classList.add('alert');
  alertStatus.textContent = `${state.seenAlertIds.size} alert${state.seenAlertIds.size>1?'s':''} logged`;
}

async function poll(){
  try {
    const [gateState, logs, alerts] = await Promise.all([
      fetchJSON('/api/state'),
      fetchJSON(`/api/logs?limit=${LOG_FETCH_LIMIT}`),
      fetchJSON(`/api/alerts?limit=${ALERT_FETCH_LIMIT}`),
    ]);

    if(!state.backendUp) setBackendStatus(true);

    // stats + per-gate counts always reflect latest snapshot
    document.getElementById('statInside').textContent = gateState.inside_count;
    document.getElementById('statScans').textContent = gateState.total_scans;
    Object.entries(gateState.per_gate_counts || {}).forEach(([gateId, count]) => {
      const gate = state.gates[gateId];
      if(gate) gate.el.querySelector('.count-pill').textContent = `${count} in`;
    });

    // logs come back newest-first; render newest-first, oldest of the
    // new batch first, so prepend ordering ends up correct on screen
    const newLogs = logs.filter(l => !state.seenLogIds.has(l.id)).reverse();

    if(state.firstPoll){
      // on first load, just render history without pulsing gates
      logs.slice().reverse().forEach(l => { state.seenLogIds.add(l.id); renderLogRow(l); });
    } else {
      newLogs.forEach(l => {
        state.seenLogIds.add(l.id);
        renderLogRow(l);
        pulseGate(l.gate_id, l.flagged);
      });
    }

    const newAlerts = alerts.filter(a => !state.seenAlertIds.has(a.id)).reverse();
    if(state.firstPoll){
      alerts.slice().reverse().forEach(a => renderAlert(a));
    } else {
      newAlerts.forEach(a => renderAlert(a));
    }

    state.firstPoll = false;

  } catch (err) {
    console.error('Poll failed:', err);
    setBackendStatus(false);
  }
}

init();
