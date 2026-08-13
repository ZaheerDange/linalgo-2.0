/**
 * LinAlgo — Solver Front-End
 *
 * Responsibilities:
 *  1. Build dynamic input forms per module type
 *  2. Load example data
 *  3. POST to /api/solve/<module> and receive step data
 *  4. Render step cards with MathJax
 *  5. Handle sidebar toggle
 */

/* ══════════════════════════════════════════════════════════════════════════════
   DOM HELPERS
   ══════════════════════════════════════════════════════════════════════════════ */
const $ = (id) => document.getElementById(id);
const el = (tag, cls, inner) => {
  const e = document.createElement(tag);
  if (cls)   e.className = cls;
  if (inner !== undefined) e.innerHTML = inner;
  return e;
};

/* ══════════════════════════════════════════════════════════════════════════════
   STATE
   ══════════════════════════════════════════════════════════════════════════════ */
let MODULE    = null;   // set by solver.html inline script
let META      = null;
let EXAMPLE   = null;

/* ══════════════════════════════════════════════════════════════════════════════
   PUBLIC ENTRY POINT  (called from solver.html)
   ══════════════════════════════════════════════════════════════════════════════ */
window.initSolver = function () {
  MODULE  = window.SOLVER_MODULE;
  META    = window.MODULE_META;
  EXAMPLE = window.MODULE_EXAMPLE;

  if (!MODULE) return;

  // Build initial form
  rebuildInputs();

  // Wire up size-change listeners
  wireListeners();

  // Sidebar toggle
  const toggle = $('sidebarToggle');
  const sidebar = $('sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    document.addEventListener('click', (e) => {
      if (!sidebar.contains(e.target) && e.target !== toggle) {
        sidebar.classList.remove('open');
      }
    });
  }

  // Solve button
  const solveBtn = $('btnSolve');
  if (solveBtn) solveBtn.addEventListener('click', handleSolve);

  // Example / Clear buttons
  const exBtn = $('btnExample');
  if (exBtn) exBtn.addEventListener('click', loadExample);

  const clearBtn = $('btnClear');
  if (clearBtn) clearBtn.addEventListener('click', clearInputs);
};

/* ══════════════════════════════════════════════════════════════════════════════
   INPUT BUILDING
   ══════════════════════════════════════════════════════════════════════════════ */
function rebuildInputs() {
  const t = META.input_type;
  if (t === 'augmented_matrix') buildAugmentedMatrix();
  else if (t === 'two_vectors')  buildTwoVectors();
  else if (t === 'multi_vectors') buildMultiVectors();
  else if (t === 'square_matrix') buildSquareMatrix();
}

function wireListeners() {
  const t = META.input_type;

  if (t === 'augmented_matrix') {
    const rowsInput = $('augRows');
    if (rowsInput) rowsInput.addEventListener('change', buildAugmentedMatrix);
  } else if (t === 'two_vectors') {
    const dimInput = $('vecDim');
    if (dimInput) dimInput.addEventListener('change', buildTwoVectors);
  } else if (t === 'multi_vectors') {
    const nInput  = $('numVecs');
    const dInput  = $('vecDim');
    if (nInput) nInput.addEventListener('change', buildMultiVectors);
    if (dInput) dInput.addEventListener('change', buildMultiVectors);
  } else if (t === 'square_matrix') {
    const nInput = $('sqN');
    if (nInput) nInput.addEventListener('change', buildSquareMatrix);
  }
}

/* ── Augmented Matrix [A | b] ─────────────────────────────────────────── */
function buildAugmentedMatrix() {
  const rows = parseInt($('augRows').value) || 3;
  const cols = rows + 1;          // n_vars + 1 constant
  const grid = $('matrixGrid');
  if (!grid) return;

  grid.innerHTML = '';
  const wrap = el('div', 'matrix-bracket');

  // Left bracket
  wrap.appendChild(el('div', 'bracket-char', '['));

  // Table of inputs
  const table = document.createElement('table');
  for (let r = 0; r < rows; r++) {
    const tr = document.createElement('tr');
    for (let c = 0; c < cols; c++) {
      const td = document.createElement('td');
      if (c === cols - 1) td.classList.add('aug-sep-col');
      td.appendChild(makeCellInput(`aug_${r}_${c}`, 0));
      tr.appendChild(td);
    }
    table.appendChild(tr);
  }
  wrap.appendChild(table);

  // Right bracket
  wrap.appendChild(el('div', 'bracket-char', ']'));
  grid.appendChild(wrap);

  // Re-render any MathJax in the label
  retypeset($('matrixGrid').parentElement);
}

/* ── Two Vectors ──────────────────────────────────────────────────────── */
function buildTwoVectors() {
  const dim = parseInt($('vecDim').value) || 3;
  buildOneVector('vecU', 'u', dim);
  buildOneVector('vecV', 'v', dim);
  retypeset($('inputBlock'));
}

function buildOneVector(containerId, prefix, dim) {
  const cont = $(containerId);
  if (!cont) return;
  cont.innerHTML = '';
  for (let i = 0; i < dim; i++) {
    const row = el('div', 'vec-entry');
    row.appendChild(el('span', null, subscriptLabel(prefix, i + 1)));
    row.appendChild(makeCellInput(`${prefix}_${i}`, 0));
    cont.appendChild(row);
  }
}

/* ── Multi Vectors ────────────────────────────────────────────────────── */
function buildMultiVectors() {
  const k   = parseInt($('numVecs').value) || 3;
  const dim = parseInt($('vecDim').value) || 3;
  const grid = $('multiVecGrid');
  if (!grid) return;
  grid.innerHTML = '';
  for (let vi = 0; vi < k; vi++) {
    const block = el('div', 'mvec-block');
    block.appendChild(el('div', 'mvec-label', `\\(\\mathbf{v}_{${vi+1}}\\)`));
    const entries = el('div', 'mvec-entries');
    for (let di = 0; di < dim; di++) {
      entries.appendChild(makeCellInput(`mv_${vi}_${di}`, 0));
    }
    block.appendChild(entries);
    grid.appendChild(block);
  }
  retypeset(grid);
}

/* ── Square Matrix ────────────────────────────────────────────────────── */
function buildSquareMatrix() {
  const n    = parseInt($('sqN').value) || 3;
  const grid = $('sqMatrixGrid');
  if (!grid) return;

  grid.innerHTML = '';
  const wrap = el('div', 'matrix-bracket');
  wrap.appendChild(el('div', 'bracket-char', '['));

  const table = document.createElement('table');
  for (let r = 0; r < n; r++) {
    const tr = document.createElement('tr');
    for (let c = 0; c < n; c++) {
      const td = document.createElement('td');
      td.appendChild(makeCellInput(`sq_${r}_${c}`, r === c ? 1 : 0));
      tr.appendChild(td);
    }
    table.appendChild(tr);
  }
  wrap.appendChild(table);
  wrap.appendChild(el('div', 'bracket-char', ']'));
  grid.appendChild(wrap);
}

/* ── Helpers ──────────────────────────────────────────────────────────── */
function makeCellInput(id, defaultVal) {
  const inp = document.createElement('input');
  inp.type        = 'text';
  inp.id          = id;
  inp.className   = 'cell-input';
  inp.value       = String(defaultVal);
  inp.inputMode   = 'decimal';
  inp.autocomplete = 'off';
  inp.setAttribute('aria-label', id.replace(/_/g, ' '));
  inp.addEventListener('focus', () => inp.select());
  return inp;
}

function subscriptLabel(letter, n) {
  return `<span style="font-family:var(--font-mono);font-size:0.78rem;color:var(--text-muted);">${letter}<sub>${n}</sub> =</span>`;
}

/* ══════════════════════════════════════════════════════════════════════════════
   DATA COLLECTION
   ══════════════════════════════════════════════════════════════════════════════ */
function collectPayload() {
  const t = META.input_type;
  if (t === 'augmented_matrix') return collectAugmented();
  if (t === 'two_vectors')      return collectTwoVectors();
  if (t === 'multi_vectors')    return collectMultiVectors();
  if (t === 'square_matrix')    return collectSquareMatrix();
  throw new Error('Unknown input type: ' + t);
}

function cellVal(id) {
  const inp = $(id);
  if (!inp) return 0;
  const v = parseFloat(inp.value.replace(/\s/g, ''));
  return isNaN(v) ? 0 : v;
}

function collectAugmented() {
  const rows = parseInt($('augRows').value) || 3;
  const cols = rows + 1;
  const matrix = [];
  for (let r = 0; r < rows; r++) {
    const row = [];
    for (let c = 0; c < cols; c++) row.push(cellVal(`aug_${r}_${c}`));
    matrix.push(row);
  }
  return { matrix };
}

function collectTwoVectors() {
  const dim = parseInt($('vecDim').value) || 3;
  const u = [], v = [];
  for (let i = 0; i < dim; i++) {
    u.push(cellVal(`u_${i}`));
    v.push(cellVal(`v_${i}`));
  }
  return { u, v };
}

function collectMultiVectors() {
  const k   = parseInt($('numVecs').value) || 3;
  const dim = parseInt($('vecDim').value)  || 3;
  const vectors = [];
  for (let vi = 0; vi < k; vi++) {
    const row = [];
    for (let di = 0; di < dim; di++) row.push(cellVal(`mv_${vi}_${di}`));
    vectors.push(row);
  }
  return { vectors };
}

function collectSquareMatrix() {
  const n = parseInt($('sqN').value) || 3;
  const matrix = [];
  for (let r = 0; r < n; r++) {
    const row = [];
    for (let c = 0; c < n; c++) row.push(cellVal(`sq_${r}_${c}`));
    matrix.push(row);
  }
  return { matrix };
}

/* ══════════════════════════════════════════════════════════════════════════════
   EXAMPLE LOADING
   ══════════════════════════════════════════════════════════════════════════════ */
function loadExample() {
  if (!EXAMPLE) return;
  const t = META.input_type;

  if (t === 'augmented_matrix' && EXAMPLE.matrix) {
    const rows = EXAMPLE.matrix.length;
    $('augRows').value = rows;
    buildAugmentedMatrix();
    const cols = EXAMPLE.matrix[0].length;
    for (let r = 0; r < rows; r++)
      for (let c = 0; c < cols; c++)
        setCell(`aug_${r}_${c}`, EXAMPLE.matrix[r][c]);

  } else if (t === 'two_vectors' && EXAMPLE.u) {
    const dim = EXAMPLE.u.length;
    $('vecDim').value = dim;
    buildTwoVectors();
    EXAMPLE.u.forEach((v, i) => setCell(`u_${i}`, v));
    EXAMPLE.v.forEach((v, i) => setCell(`v_${i}`, v));

  } else if (t === 'multi_vectors' && EXAMPLE.vectors) {
    const k   = EXAMPLE.vectors.length;
    const dim = EXAMPLE.vectors[0].length;
    $('numVecs').value = k;
    $('vecDim').value  = dim;
    buildMultiVectors();
    EXAMPLE.vectors.forEach((vec, vi) =>
      vec.forEach((val, di) => setCell(`mv_${vi}_${di}`, val))
    );

  } else if (t === 'square_matrix' && EXAMPLE.matrix) {
    const n = EXAMPLE.matrix.length;
    $('sqN').value = n;
    buildSquareMatrix();
    for (let r = 0; r < n; r++)
      for (let c = 0; c < n; c++)
        setCell(`sq_${r}_${c}`, EXAMPLE.matrix[r][c]);
  }
}

function setCell(id, val) {
  const inp = $(id);
  if (inp) inp.value = String(val);
}

function clearInputs() {
  rebuildInputs();
  hideError();
  const ss = $('stepsSection');
  if (ss) ss.hidden = true;
}

/* ══════════════════════════════════════════════════════════════════════════════
   SOLVE HANDLER
   ══════════════════════════════════════════════════════════════════════════════ */
async function handleSolve() {
  hideError();
  const ss = $('stepsSection');
  if (ss) ss.hidden = true;

  let payload;
  try {
    payload = collectPayload();
  } catch (e) {
    showError('Could not read inputs: ' + e.message);
    return;
  }

  const solveBtn = $('btnSolve');
  setLoading(solveBtn, true);

  try {
    const resp = await fetch(`/api/solve/${MODULE}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();

    if (!data.success) {
      if (data.error === 'INSUFFICIENT_CREDITS') {
        showErrorHTML(
          '<strong>Out of Credits!</strong> You have used all your credits. ' +
          '<a href="/pricing" style="color:var(--color-wine);font-weight:700;text-decoration:underline;">Upgrade Plan or Buy Credits here &rarr;</a>'
        );
      } else {
        showError(data.message || data.error || 'Unknown server error.');
      }
      return;
    }

    if (data.remaining_credits !== undefined && data.remaining_credits !== null) {
      updateNavbarCredits(data.remaining_credits);
    }

    renderSteps(data.steps);
  } catch (e) {
    showError('Network error: ' + e.message);
  } finally {
    setLoading(solveBtn, false);
  }
}

function setLoading(btn, state) {
  if (!btn) return;
  btn.disabled = state;
  btn.innerHTML = state
    ? '<span class="btn-icon">⏳</span> Solving…'
    : '<span class="btn-icon">⚡</span> Solve Step-by-Step';
}

/* ══════════════════════════════════════════════════════════════════════════════
   STEP RENDERING
   ══════════════════════════════════════════════════════════════════════════════ */
const TYPE_CLASS = {
  initial:   'step-type-initial',
  swap:      'step-type-swap',
  scale:     'step-type-scale',
  eliminate: 'step-type-eliminate',
  back_sub:  'step-type-back_sub',
  milestone: 'step-type-milestone',
  solution:  'step-type-solution',
  error:     'step-type-error',
  info:      'step-type-info',
  header:    'step-type-header',
};

function renderSteps(steps) {
  const container = $('stepsContainer');
  const section   = $('stepsSection');
  const countEl   = $('stepsCount');
  if (!container || !section) return;

  container.innerHTML = '';

  steps.forEach((step, idx) => {
    const card = buildStepCard(step, idx + 1);
    card.style.animationDelay = `${idx * 0.04}s`;
    container.appendChild(card);
  });

  if (countEl) countEl.textContent = `${steps.length} step${steps.length !== 1 ? 's' : ''}`;
  section.hidden = false;

  // Typeset all new math
  retypeset(container).then(() => {
    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
}

function buildStepCard(step, num) {
  const type = step.type || 'info';
  const card = el('div', `step-card ${TYPE_CLASS[type] || 'step-type-info'}`);
  if (step.highlight) card.classList.add('step-highlight');

  // Title row
  const titleRow = el('div', 'step-title');
  titleRow.appendChild(el('span', 'step-number', String(num)));
  const titleText = el('span', null);
  titleText.innerHTML = step.title || '';
  titleRow.appendChild(titleText);
  card.appendChild(titleRow);

  // Description
  if (step.description) {
    const desc = el('div', 'step-desc');
    desc.innerHTML = markdownBold(step.description);
    card.appendChild(desc);
  }

  // Matrix display
  if (step.matrix_latex) {
    const blk = el('div', 'step-math-block matrix-block');
    blk.innerHTML = `\\[${step.matrix_latex}\\]`;
    card.appendChild(blk);
  }

  // Operation / formula
  if (step.operation_latex) {
    const blk = el('div', 'step-math-block operation-block');
    blk.innerHTML = `\\[${step.operation_latex}\\]`;
    card.appendChild(blk);
  }

  // Result (e.g. boxed solution)
  if (step.result_latex) {
    const blk = el('div', 'step-math-block result-block');
    blk.innerHTML = `\\[${step.result_latex}\\]`;
    card.appendChild(blk);
  }

  return card;
}

/**
 * Convert **bold** and line-break markers in description strings.
 * Also wraps $...$ so MathJax can pick them up.
 */
function markdownBold(text) {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\\n\\n/g, '<br/><br/>')
    .replace(/\\n/g, '<br/>');
}

/* ══════════════════════════════════════════════════════════════════════════════
   ERROR DISPLAY
   ══════════════════════════════════════════════════════════════════════════════ */
function showError(msg) {
  const banner = $('errorBanner');
  const msgEl  = $('errorMessage');
  if (!banner || !msgEl) return;
  msgEl.textContent = msg;
  banner.hidden = false;
  banner.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showErrorHTML(htmlContent) {
  const banner = $('errorBanner');
  const msgEl  = $('errorMessage');
  if (!banner || !msgEl) return;
  msgEl.innerHTML = htmlContent;
  banner.hidden = false;
  banner.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideError() {
  const banner = $('errorBanner');
  if (banner) banner.hidden = true;
}

/* ══════════════════════════════════════════════════════════════════════════════
   MATHJAX UTILITY
   ══════════════════════════════════════════════════════════════════════════════ */
function retypeset(element) {
  if (typeof MathJax === 'undefined' || !MathJax.typesetPromise) {
    return Promise.resolve();
  }
  const targets = element ? [element] : undefined;
  return MathJax.typesetPromise(targets).catch((err) => {
    console.warn('MathJax typeset error:', err);
  });
}

/* ══════════════════════════════════════════════════════════════════════════════
   NAVBAR SCROLL BEHAVIOUR
   ══════════════════════════════════════════════════════════════════════════════ */
(function () {
  const navbar = document.getElementById('navbar');
  if (!navbar) return;
  let lastY = 0;
  window.addEventListener('scroll', () => {
    const y = window.scrollY;
    if (y > 80) {
      navbar.style.boxShadow = '0 2px 20px rgba(0,0,0,0.4)';
    } else {
      navbar.style.boxShadow = '';
    }
    lastY = y;
  }, { passive: true });
})();

function updateNavbarCredits(remCredits) {
  const countEl = document.querySelector('.nav-credits-badge .credit-count');
  const iconEl = document.querySelector('.nav-credits-badge .credit-icon');
  if (!countEl) return;

  if (remCredits === 'unlimited') {
    countEl.textContent = 'Unlimited';
    if (iconEl) iconEl.textContent = '♾️';
  } else {
    countEl.textContent = `${remCredits} Credits`;
    if (iconEl) iconEl.textContent = '🪙';
  }
}

/* ══════════════════════════════════════════════════════════════════════════════
   AMBIENT MATH SYMBOLS BACKGROUND
   ══════════════════════════════════════════════════════════════════════════════ */
function initAmbientMathBg() {
  const container = document.getElementById('ambientMathBg');
  if (!container) return;

  const SYMBOLS = ['Σ', '∫', 'π', 'λ', '√', '∞', 'Δ', 'θ', '∇', '±', '∈', '≠', '≤', '∀', '∂', '⊥', '×'];
  const NUM_SYMBOLS = 28;

  container.innerHTML = '';

  for (let i = 0; i < NUM_SYMBOLS; i++) {
    const span = document.createElement('span');
    span.className = 'ambient-symbol';

    // Pick a random symbol from the set
    const char = SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)];
    span.textContent = char;

    // Random horizontal position (1% to 98%)
    const left = (Math.random() * 97 + 1).toFixed(2);
    // Random font size (14px to 48px)
    const fontSize = Math.floor(Math.random() * (48 - 14 + 1)) + 14;
    // Random animation duration (14s to 32s)
    const duration = (Math.random() * (32 - 14) + 14).toFixed(1);
    // Random negative delay so symbols start pre-dispersed vertically across screen
    const delay = (-Math.random() * duration).toFixed(1);
    // Random slight rotation (-45deg to 45deg)
    const rotation = (Math.random() * 90 - 45).toFixed(1);
    // Random peak opacity (0.40 to 0.60)
    const maxOpacity = (Math.random() * 0.20 + 0.40).toFixed(2);

    span.style.left = `${left}%`;
    span.style.fontSize = `${fontSize}px`;
    span.style.animationDuration = `${duration}s`;
    span.style.animationDelay = `${delay}s`;
    span.style.setProperty('--rot', `${rotation}deg`);
    span.style.setProperty('--max-opacity', maxOpacity);

    container.appendChild(span);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initAmbientMathBg);
} else {
  initAmbientMathBg();
}

