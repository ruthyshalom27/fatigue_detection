// Configuration
const API_BASE = 'http://localhost:5000/api';
const BUCKETS = 20;

// State
let blinkHistory = new Array(BUCKETS).fill(0);
let prevBlinks = 0;
let lastLogStatus = '';
let apiConnected = false;

// Clock
const clockEl = document.getElementById('clock');
setInterval(() => {
  clockEl.textContent = new Date().toLocaleTimeString('en-GB');
}, 1000);

// Initialize blink chart
const blinkChart = document.getElementById('blink-chart');
for (let i = 0; i < BUCKETS; i++) {
  const b = document.createElement('div');
  b.className = 'blink-bar';
  b.style.height = '2px';
  blinkChart.appendChild(b);
}

function updateBlinkChart() {
  const bars = blinkChart.querySelectorAll('.blink-bar');
  const max = Math.max(...blinkHistory, 1);
  bars.forEach((b, i) => {
    const h = Math.max(2, (blinkHistory[i] / max) * 38);
    b.style.height = h + 'px';
  });
}

// Gauge arc math: circumference = 2π×60 ≈ 376.99
const CIRC = 2 * Math.PI * 60;
const gaugeArc = document.getElementById('gauge-fill');

function setGauge(pct) {
  const offset = CIRC - (pct / 100) * CIRC;
  gaugeArc.style.strokeDashoffset = offset;
  if (pct >= 70) gaugeArc.style.stroke = 'var(--red)';
  else if (pct >= 40) gaugeArc.style.stroke = 'var(--yellow)';
  else gaugeArc.style.stroke = 'var(--green)';
}

// Log helper
function addLog(msg, type = '') {
  const log = document.getElementById('event-log');
  const ts = new Date().toLocaleTimeString('en-GB');
  const div = document.createElement('div');
  div.className = `log-entry ${type}`;
  div.innerHTML = `<span class="ts">${ts}</span><span class="msg">${msg}</span>`;
  log.prepend(div);
  while (log.children.length > 40) log.removeChild(log.lastChild);
}

// Poll stats every 500ms
let bucketTimer = 0;
setInterval(async () => {
  try {
    const res = await fetch(`${API_BASE}/stats`);
    if (!res.ok) throw new Error('API error');
    const data = await res.json();

    // Update API status
    if (!apiConnected) {
      apiConnected = true;
      document.getElementById('api-status').textContent = 'Connected ✓';
      document.getElementById('api-status').style.color = 'var(--green)';
      addLog('Connected to backend API', 'ok');
    }

    // Status card
    const statusEl = document.getElementById('s-status');
    const statusStr = data.status || 'Awake';
    statusEl.textContent = statusStr;
    statusEl.className = 'value ' +
      (statusStr === 'DROWSY' ? 'red' : statusStr === 'Tired' ? 'yellow' : 'green');

    document.getElementById('s-ear').textContent = (data.ear || 0).toFixed(3);
    document.getElementById('s-bpm').textContent = (data.blink_rate || 0).toFixed(1);
    document.getElementById('s-blinks').textContent = data.blink_count || 0;

    // Gauge
    const fs = data.fatigue_score || 0;
    document.getElementById('gauge-pct').textContent = fs + '%';
    setGauge(fs);
    const gst = document.getElementById('gauge-status-text');
    if (statusStr === 'DROWSY') {
      gst.textContent = '● DROWSY';
      gst.style.color = 'var(--red)';
    } else if (statusStr === 'Tired') {
      gst.textContent = '◑ TIRED';
      gst.style.color = 'var(--yellow)';
    } else {
      gst.textContent = '● AWAKE';
      gst.style.color = 'var(--green)';
    }

    // Alert overlay
    const overlay = document.getElementById('alert-overlay');
    statusStr === 'DROWSY' ? overlay.classList.add('visible') : overlay.classList.remove('visible');

    // Face detection
    document.getElementById('m-face').textContent = data.face_detected ? 'Yes ✓' : 'No —';
    document.getElementById('m-cf').textContent = data.closed_frames || 0;

    // EAR bar
    const earVal = data.ear || 0;
    const earPct = Math.min(earVal / 0.45 * 100, 100).toFixed(1);
    const earBar = document.getElementById('ear-bar');
    earBar.style.width = earPct + '%';
    earBar.style.background = earVal < 0.25 ? 'var(--red)' : earVal < 0.32 ? 'var(--yellow)' : 'var(--green)';
    document.getElementById('ear-bar-val').textContent = earVal.toFixed(3);

    // Blink history bucket (updates every 1s)
    bucketTimer++;
    if (bucketTimer >= 2) {
      bucketTimer = 0;
      const newBlinks = (data.blink_count || 0) - prevBlinks;
      prevBlinks = data.blink_count || 0;
      blinkHistory.shift();
      blinkHistory.push(newBlinks);
      updateBlinkChart();
    }

    // Event log
    if (statusStr !== lastLogStatus) {
      const type = statusStr === 'DROWSY' ? 'danger' : statusStr === 'Tired' ? 'warn' : 'ok';
      addLog(`Status changed → ${statusStr}`, type);
      lastLogStatus = statusStr;
    }

  } catch (e) {
    if (apiConnected) {
      apiConnected = false;
      document.getElementById('api-status').textContent = 'Disconnected';
      document.getElementById('api-status').style.color = 'var(--red)';
      addLog('Cannot connect to backend API', 'danger');
    }
  }
}, 500);

// Init log
addLog('Web app started', 'ok');
addLog('Connecting to backend API...', 'ok');
