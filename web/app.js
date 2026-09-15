// Nav shadow + reveal on scroll + animated counters
window.addEventListener('scroll', () => {
  document.getElementById('navbar').classList.toggle('scrolled', window.scrollY > 50);
});

document.addEventListener('DOMContentLoaded', () => {
  updateSim();
  const counters = document.querySelectorAll('.counter .num');
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      const el = e.target;
      io.unobserve(el);
      const target = parseFloat(el.dataset.target);
      const fmt = el.dataset.format;
      const dur = 1200, t0 = performance.now();
      const tick = (t) => {
        const p = Math.min(1, (t - t0) / dur);
        const v = target * (0.2 + 0.8 * p * (2 - p));
        el.textContent = fmt === 'int'
          ? Math.round(v).toLocaleString('es-ES')
          : v.toFixed(3);
        if (p < 1) requestAnimationFrame(tick);
        else el.textContent = fmt === 'int' ? target.toLocaleString('es-ES') : target.toFixed(3);
      };
      requestAnimationFrame(tick);
    });
  }, { threshold: 0.4 });
  counters.forEach((c) => io.observe(c));

  document.querySelectorAll('section .card, section .product, .hero-mock').forEach((el) => {
    el.classList.add('reveal');
    new IntersectionObserver((es, obs) => {
      es.forEach((x) => { if (x.isIntersecting) { x.target.classList.add('visible'); obs.disconnect(); } });
    }, { threshold: 0.12 }).observe(el);
  });

  document.querySelectorAll('.faq-item h4').forEach((h) => {
    h.addEventListener('click', () => h.parentElement.classList.toggle('open'));
  });

  // Lightbox para las 3 figuras de #datos (presentación)
  const lb = document.getElementById('lightbox');
  const lbImg = document.getElementById('lightboxImg');
  const lbCap = document.getElementById('lightboxCap');
  const closeLb = () => { lb.classList.remove('open'); lb.setAttribute('aria-hidden', 'true'); document.body.style.overflow = ''; };
  document.querySelectorAll('.fig-grid img.zoomable').forEach((img) => {
    img.addEventListener('click', (e) => {
      e.stopPropagation();
      const card = img.closest('.card');
      const title = card ? card.querySelector('h3').textContent : img.alt;
      lbImg.src = img.src;
      lbImg.alt = img.alt;
      const suf = (typeof __t === 'function') ? __t('sim.lbSuffix') : '(pulsa Esc o clic fuera para cerrar)';
      lbCap.textContent = title + ' — ' + img.alt + ' ' + suf;
      lb.classList.add('open');
      lb.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    });
  });
  lb.addEventListener('click', closeLb);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeLb(); });
});

// Demo ilustrativa calibrada con las importancias reales (NO es el .pkl productivo).
const TITLE_ADJ = { dota: -10, apex: -10, tf2: -6, warframe: -6, poe: 6, fallguys: 14 };
const TITLE_NAME = { dota: 'Dota 2', apex: 'Apex Legends', tf2: 'Team Fortress 2', warframe: 'Warframe', poe: 'Path of Exile', fallguys: 'Fall Guys' };

function updateSim() {
  const h = +document.getElementById('hours').value;
  const g = +document.getElementById('games').value;
  const age = +document.getElementById('age').value;
  const t = document.getElementById('title').value;
  const voted = document.getElementById('voted').value === '1';
  document.getElementById('hoursVal').textContent = h;
  document.getElementById('gamesVal').textContent = g;
  document.getElementById('ageVal').textContent = age;

  let score = 58 - 34 * h / (h + 120) - (voted ? 6 : 0) - 5 * g / (g + 60)
    + (TITLE_ADJ[t] || 0) + Math.min(12, age / 30);
  score = Math.max(3, Math.min(97, Math.round(score)));

  const circ = 2 * Math.PI * 80;
  document.getElementById('gaugeArc').style.strokeDashoffset = circ * (1 - score / 100);
  const arc = document.getElementById('gaugeArc');
  arc.style.stroke = score > 65 ? '#ef4444' : score > 35 ? '#f59e0b' : '#22d3ee';
  const val = document.getElementById('gaugeVal');
  val.textContent = score + '%';
  val.style.color = score > 65 ? '#f87171' : score > 35 ? '#fbbf24' : '#22d3ee';

  let motive, action;
  const T = (typeof __t === 'function') ? __t : ((k) => k);
  if (h <= 18) { motive = T('sim.motiveEarly'); action = T('sim.actionEarly'); }
  else if (age > 90) { motive = T('sim.motiveOld'); action = T('sim.actionOld'); }
  else if (!voted) { motive = T('sim.motiveNoRec'); action = T('sim.actionNoRec'); }
  else if ((TITLE_ADJ[t] || 0) > 0) { motive = T('sim.motiveDecline') + ' (' + TITLE_NAME[t] + ')'; action = T('sim.actionDecline'); }
  else { motive = T('sim.motiveHealthy'); action = T('sim.actionHealthy'); }
  const level = score > 65 ? T('sim.levelHigh') : score > 35 ? T('sim.levelMid') : T('sim.levelLow');
  document.getElementById('motiveBox').innerHTML =
    '<strong>' + level + ' · ' + score + '%</strong><br>' + T('sim.motiveLabel') + ' <strong>' + motive + '</strong><br>' + T('sim.actionLabel') + ' ' + action;
}

function setPreset(h, g, age, t, voted) {
  document.getElementById('hours').value = h;
  document.getElementById('games').value = g;
  document.getElementById('age').value = age;
  document.getElementById('title').value = t;
  document.getElementById('voted').value = String(voted);
  updateSim();
}

function calcBudget() {
  const budget = Math.max(100, +document.getElementById('budget').value || 10000);
  const cpi = Math.max(0.5, +document.getElementById('cpi').value || 5);
  const ltv = Math.max(1, +document.getElementById('ltv').value || 45);
  window.__budget = { budget, cpi, ltv };
  renderBudget();
}

function renderBudget() {
  const box = document.getElementById('budgetResult');
  if (!window.__budget) return;
  const { budget, cpi, ltv } = window.__budget;
  const installs = budget / cpi;
  const hv = installs * 0.199;
  const value = hv * ltv;
  const T = (typeof __t === 'function') ? __t : ((k) => k);
  const loc = (window.__lang || 'es') === 'en' ? 'en-US' : (window.__lang || 'es') === 'es' ? 'es-ES' : (window.__lang || 'es') + '-' + (window.__lang || 'es').toUpperCase();
  box.innerHTML =
    '<strong>' + installs.toFixed(0) + ' installs</strong> → ~' + hv.toFixed(0) +
    ' ' + T('sim.budgetA') + ' ≈ <strong>$' + value.toLocaleString(loc, { maximumFractionDigits: 0 }) + '</strong> ' + T('sim.budgetB') + ltv + '.' +
    '<br>' + T('sim.budgetC');
  box.classList.add('show');
}
