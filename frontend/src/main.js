import { readActiveDocumentAsPNG, placeImageFromBytes } from './photoshop-bridge.js';

const BACKEND_URL = (window.BACKEND_URL || 'http://localhost:8000') + '/api/v1';

async function runRetouch() {
  const prompt = document.getElementById('prompt').value || '';
  const img = await readActiveDocumentAsPNG();
  const output = document.getElementById('output');

  if (!img) {
    output.textContent = 'No image from Photoshop (bridge not implemented yet).';
    return;
  }

  const form = new FormData();
  form.append('prompt', prompt);
  form.append('operation', 'img2img');
  form.append('image', new Blob([img], { type: 'image/png' }), 'document.png');

  output.textContent = 'Processing...';
  try {
    const res = await fetch(`${BACKEND_URL}/retouch/process`, { method: 'POST', body: form });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    if (data.image_base64) {
      const imgEl = new Image();
      imgEl.src = `data:image/png;base64,${data.image_base64}`;
      output.innerHTML = '';
      output.appendChild(imgEl);
      // Place result back into Photoshop as a new layer
      try {
        const bytes = Uint8Array.from(atob(data.image_base64), c => c.charCodeAt(0));
        await placeImageFromBytes(bytes, `AI Edit: ${prompt}`);
      } catch (e) {
        console.warn('Placement to Photoshop failed or unavailable:', e);
      }
    } else {
      output.textContent = JSON.stringify(data, null, 2);
    }
  } catch (e) {
    output.textContent = 'Error: ' + (e?.message || e);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('run').addEventListener('click', runRetouch);
  setupSAMControls();
});

// -----------------------------
// SAM UI integration
// -----------------------------
let samPoints = [];
let samLabels = [];

function setupSAMControls() {
  const tools = document.querySelector('.ai-tools');
  if (!tools) return;

  const samSection = document.createElement('div');
  samSection.className = 'sam-section';
  samSection.innerHTML = `
    <div class="section-header"><h3>Precision Masking (SAM)</h3></div>
    <div class="sam-controls">
      <div class="sam-buttons">
        <button id="startSamMode" class="btn-secondary">Start Point Collection</button>
        <button id="clearSamPoints" class="btn-secondary" disabled>Clear Points</button>
        <button id="createSamMask" class="btn-primary" disabled>Create Mask</button>
      </div>
      <div class="sam-status" id="samStatus">Ready for precision masking</div>
      <div class="sam-points-list" id="samPointsList"></div>
      <div class="sam-coordinate-input" style="margin-top: 10px;">
        <label>Manual Point Input:</label>
        <div style="display:flex; gap:8px; margin-top:5px;">
          <input type="number" id="samPointX" placeholder="X" style="width:60px;">
          <input type="number" id="samPointY" placeholder="Y" style="width:60px;">
          <select id="samPointType">
            <option value="1">Foreground</option>
            <option value="0">Background</option>
          </select>
          <button id="addSamPoint" class="btn-secondary">Add Point</button>
        </div>
      </div>
    </div>
  `;
  tools.appendChild(samSection);

  document.getElementById('startSamMode').addEventListener('click', startSAMMode);
  document.getElementById('clearSamPoints').addEventListener('click', clearSAMPoints);
  document.getElementById('createSamMask').addEventListener('click', createSAMMask);
  document.getElementById('addSamPoint').addEventListener('click', addManualSAMPoint);
}

function startSAMMode() {
  updateSAMStatus('SAM Mode Active: Add points using manual input below');
  updateSAMButtons(true);
}

function addManualSAMPoint() {
  const x = document.getElementById('samPointX').value;
  const y = document.getElementById('samPointY').value;
  const label = parseInt(document.getElementById('samPointType').value);
  if (!x || !y) {
    alert('Please enter both X and Y coordinates');
    return;
  }
  addSAMPoint(parseInt(x), parseInt(y), label);
  document.getElementById('samPointX').value = '';
  document.getElementById('samPointY').value = '';
}

function addSAMPoint(x, y, label) {
  samPoints.push([x, y]);
  samLabels.push(label);
  updateSAMStatus(`Point added: (${x}, ${y}) - ${label === 1 ? 'Foreground' : 'Background'}`);
  updateSAMPointsList();
  updateSAMButtons(true);
}

async function createSAMMask() {
  if (samPoints.length === 0) {
    alert('Please add at least one point first');
    return;
  }
  updateSAMStatus('Creating precision mask with SAM...');
  try {
    const imageBytes = await readActiveDocumentAsPNG();
    if (!imageBytes) throw new Error('No active document in Photoshop');

    const formData = new FormData();
    const blob = new Blob([imageBytes], { type: 'image/png' });
    formData.append('image', blob, 'document.png');
    formData.append('points', JSON.stringify(samPoints));
    formData.append('labels', JSON.stringify(samLabels));

    const res = await fetch(`${BACKEND_URL}/segmentation/segment-from-points`, { method: 'POST', body: formData });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`SAM request failed: ${res.status} - ${text}`);
    }
    const result = await res.json();

    const maskBytes = Uint8Array.from(atob(result.mask), c => c.charCodeAt(0));
    await placeImageFromBytes(maskBytes, `SAM Mask (${samPoints.length} points)`);
    updateSAMStatus(`✅ Mask created! Confidence: ${(result.score * 100).toFixed(1)}%`);
    clearSAMPoints();
  } catch (e) {
    console.error('SAM mask creation failed:', e);
    updateSAMStatus(`❌ Mask creation failed: ${e.message || e}`);
  }
}

function updateSAMButtons(hasPoints) {
  const clr = document.getElementById('clearSamPoints');
  const crt = document.getElementById('createSamMask');
  if (clr) clr.disabled = !hasPoints;
  if (crt) crt.disabled = !hasPoints;
}

function updateSAMStatus(message) {
  const status = document.getElementById('samStatus');
  if (!status) return;
  status.textContent = message;
  status.style.color = message.includes('❌') ? '#dc3545' : (message.includes('✅') ? '#28a745' : 'inherit');
}

function updateSAMPointsList() {
  const list = document.getElementById('samPointsList');
  if (!list) return;
  list.innerHTML = samPoints.map((p, i) => (
    `<div style="font-size:11px; margin:2px 0;">Point ${i + 1}: (${p[0]}, ${p[1]}) - 
      <span style="color:${samLabels[i] === 1 ? '#28a745' : '#dc3545'}">${samLabels[i] === 1 ? 'Foreground' : 'Background'}</span>
    </div>`
  )).join('');
}

function clearSAMPoints() {
  samPoints = [];
  samLabels = [];
  updateSAMStatus('Points cleared. Ready for new points.');
  updateSAMPointsList();
  updateSAMButtons(false);
}
