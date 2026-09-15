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
  if (h <= 18) { motive = 'Engagement temprano bajo (Q1: 35,7% de churn)'; action = 'Onboarding + evento diario personalizado en 24 h.'; }
  else if (age > 90) { motive = 'Señal antigua en título frío'; action = 'Campaña win-back + bundle de retorno.'; }
  else if (!voted) { motive = 'No recomienda (29,6% de churn)'; action = 'Soporte proactivo + oferta de guardado.'; }
  else if ((TITLE_ADJ[t] || 0) > 0) { motive = 'Título en fase de declive (' + TITLE_NAME[t] + ')'; action = 'Contenido/evento de retorno + recordatorio.'; }
  else { motive = 'Perfil sano'; action = 'Mantener cadencia; pase de temporada como acelerador.'; }
  const level = score > 65 ? '🔴 Riesgo alto' : score > 35 ? '🟡 Riesgo medio' : '🟢 Riesgo bajo';
  document.getElementById('motiveBox').innerHTML =
    '<strong>' + level + ' · ' + score + '%</strong><br>Motivo probable: <strong>' + motive + '</strong><br>Acción playbook: ' + action;
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
  const installs = budget / cpi;
  const hv = installs * 0.199;
  const value = hv * ltv;
  document.getElementById('budgetResult').innerHTML =
    '<strong>' + installs.toFixed(0) + ' installs</strong> → ~' + hv.toFixed(0) +
    ' en grupo de alto valor aprox. (19,9% en nuestra muestra) ≈ <strong>$' + value.toLocaleString('es-ES', { maximumFractionDigits: 0 }) + '</strong> de valor potencial con LTV $' + ltv + '.' +
    '<br>Estimación basada en nuestro proxy, no una garantía de ingresos. En proyecto real se sustituye por datos reales de PlayNova Games.';
  document.getElementById('budgetResult').classList.add('show');
}
