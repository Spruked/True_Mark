import { getCurrentWindow } from '@tauri-apps/api/window';
import './styles.css';

const API_URL = 'http://127.0.0.1:8000/api/time';
const app = document.querySelector('#app');

app.innerHTML = `
  <section class="widget-shell">
    <header class="widget-header" data-tauri-drag-region>
      <div class="brand"><span class="signal"></span><span>ISS SCALE</span></div>
      <div class="header-actions">
        <span id="status" class="status">CONNECTING</span>
        <button id="close" class="close" aria-label="Close widget">×</button>
      </div>
    </header>
    <div class="hero">
      <span class="eyebrow">INTERPLANETARY STARDATE SYNCROMETER</span>
      <strong id="iss">ISS --.-- --:--:--.---</strong>
      <span id="ns" class="raw">-- ns since 2000 epoch</span>
    </div>
    <div class="time-grid">
      <div><small>EPOCH / UNIX NS</small><span id="epoch">--</span></div>
      <div><small>STANDARD</small><span id="standard">--</span></div>
      <div><small>JULIAN</small><span id="julian">--</span></div>
      <div><small>ISS RAW NS</small><span id="iss-raw">--</span></div>
    </div>
    <div class="detail-grid">
      <div><small>PROPER TIME</small><span id="proper">--</span></div>
      <div><small>MISSION ELAPSED</small><span id="mission">--</span></div>
      <div><small>LOCAL DISPLAY</small><span id="local">--</span></div>
    </div>
    <div class="mission-bar">
      <div><small>MISSION SESSION</small><strong id="mission-label">NO ACTIVE SESSION</strong></div>
      <div class="mission-actions">
        <button id="start-mission" class="mission-button start">START MISSION</button>
        <button id="end-mission" class="mission-button end" disabled>END MISSION</button>
      </div>
    </div>
    <footer><span id="frame">SOLAR-SYSTEM BARYCENTRIC</span><span id="hash">ANCHOR --</span></footer>
  </section>
`;

const $ = (id) => document.querySelector(`#${id}`);

function setStatus(online) {
  $('status').textContent = online ? 'LIVE' : 'OFFLINE';
  $('status').classList.toggle('offline', !online);
}

function render(data) {
  $('iss').textContent = data.human_iss_precise || data.iss || 'ISS unavailable';
  $('ns').textContent = `${Number(data.iss_time_ns).toLocaleString()} ns since epoch`;
  $('epoch').textContent = Number(data.epoch).toLocaleString();
  $('standard').textContent = data.standard || '--';
  $('julian').textContent = data.julian || '--';
  $('iss-raw').textContent = Number(data.iss_time_ns).toLocaleString();
  $('proper').textContent = data.proper_time_ns == null ? 'not supplied' : `${Number(data.proper_time_ns).toLocaleString()} ns`;
  $('mission').textContent = data.mission_elapsed_ns == null ? 'not supplied' : `${Number(data.mission_elapsed_ns).toLocaleString()} ns`;
  $('local').textContent = data.local_display_time || '--';
  const mission = data.mission;
  $('mission-label').textContent = mission ? `${mission.label} · MET ${formatElapsed(mission.mission_elapsed_ns)}` : 'NO ACTIVE SESSION';
  $('start-mission').disabled = Boolean(mission);
  $('end-mission').disabled = !mission;
  $('frame').textContent = (data.reference_frame || 'solar-system-barycentric').toUpperCase();
  $('hash').textContent = `ANCHOR ${(data.anchor_hash || '').slice(0, 10) || '--'}`;
  setStatus(true);
}

function formatElapsed(ns) {
  const totalSeconds = Math.floor(Number(ns || 0) / 1_000_000_000);
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  return `${String(days).padStart(3, '0')}/${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

async function missionAction(path, body) {
  const response = await fetch(`http://127.0.0.1:8000${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  await refresh();
}

async function refresh() {
  try {
    const response = await fetch(`${API_URL}?t=${Date.now()}`, { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    render(await response.json());
  } catch {
    setStatus(false);
    $('ns').textContent = 'Start the ISS service on port 8000';
  }
}

$('close').addEventListener('click', () => getCurrentWindow().hide());
document.querySelector('.widget-shell').addEventListener('mousedown', async (event) => {
  if (event.button === 0 && !event.target.closest('button')) {
    await getCurrentWindow().startDragging();
  }
});
$('start-mission').addEventListener('click', async () => {
  const label = window.prompt('Mission label', 'Work Session');
  if (label === null) return;
  try { await missionAction('/api/mission/start', { label }); } catch (error) { window.alert(error.message); }
});
$('end-mission').addEventListener('click', async () => {
  try { await missionAction('/api/mission/end'); } catch (error) { window.alert(error.message); }
});
refresh();
setInterval(refresh, 250);
