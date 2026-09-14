// Nav shadow + reveal on scroll + animated counters
window.addEventListener('scroll', () => {
  document.getElementById('navbar').classList.toggle('scrolled', window.scrollY > 50);
});

document.addEventListener('DOMContentLoaded', () => {
  updateSim();
  // Counters
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

  // Reveal
  document.querySelectorAll('section .card, section .product, .hero-mock').forEach((el) => {
    el.classList.add('reveal');
    new IntersectionObserver((es, obs) => {
      es.forEach((x) => { if (x.isIntersecting) { x.target.classList.add('visible'); obs.disconnect(); } });
    }, { threshold: 0.12 }).observe(el);
  });

  // FAQ (también funciona el onclick inline)
  document.querySelectorAll('.faq-item h4').forEach((h) => {
    h.addEventListener('click', () => h.parentElement.classList.toggle('open'));
  });
});

// Demo ilustrativa calibrada con las importancias del RF (no es el modelo productivo).
const CHAN_ADJ = { organic: -6, referral: -3, google_uac: 0, meta: 1, tiktok: 2, unity_ads: 3, ironsource: 3.5, applovin: 4 };

function updateSim() {
  const tut = +document.getElementById('tutorial').value;
  const fri = +document.getElementById('friends').value;
  const ses = +document.getElementById('sessions').value;
  const ch = document.getElementById('channel').value;
  document.getElementById('tutVal').textContent = tut;
  document.getElementById('friVal').textContent = fri;
  document.getElementById('sesVal').textContent = ses;
  let score = 78 - tut * 0.35 - fri * 3 - (ses - 1) * 2.2 + (CHAN_ADJ[ch] || 0);
  score = Math.max(3, Math.min(97, Math.round(score)));

  const circ = 2 * Math.PI * 80;
  document.getElementById('gaugeArc').style.strokeDashoffset = circ * (1 - score / 100);
  const arc = document.getElementById('gaugeArc');
  arc.style.stroke = score > 65 ? '#ef4444' : score > 35 ? '#f59e0b' : '#22d3ee';
  const val = document.getElementById('gaugeVal');
  val.textContent = score + '%';
  val.style.color = score > 65 ? '#f87171' : score > 35 ? '#fbbf24' : '#22d3ee';

  // Motivo + acción (playbook semanal)
  let motive, action;
  if (tut < 50) { motive = 'Tutorial incompleto'; action = 'Push de onboarding + bonus de bienvenida en las próximas 24 h.'; }
  else if (fri === 0) { motive = 'Sin círculo social'; action = 'Prompt de invitar amigos + recompensa social (2× retención).'; }
  else if (ses <= 3) { motive = 'Sesiones cortas / pocas'; action = 'Evento diario personalizado + booster anti-frustración.'; }
  else if ((CHAN_ADJ[ch] || 0) > 0) { motive = 'Canal de volumen (' + ch + ')'; action = 'Onboarding reforzado + recordatorio D1/D3.'; }
  else { motive = 'Engagement estable'; action = 'Mantener cadencia; bundle de temporada como acelerador.'; }
  const level = score > 65 ? '🔴 Riesgo alto' : score > 35 ? '🟡 Riesgo medio' : '🟢 Riesgo bajo';
  document.getElementById('motiveBox').innerHTML =
    '<strong>' + level + ' · ' + score + '%</strong><br>Motivo probable: <strong>' + motive + '</strong><br>Acción playbook: ' + action;
}

function setPreset(t, f, s, ch) {
  document.getElementById('tutorial').value = t;
  document.getElementById('friends').value = f;
  document.getElementById('sessions').value = s;
  document.getElementById('channel').value = ch;
  updateSim();
}

function calcBudget() {
  const cpi = Math.max(0.5, +document.getElementById('cpi').value || 5);
  const budget = Math.max(100, +document.getElementById('budget').value || 10000);
  const ltv = Math.max(1, +document.getElementById('ltv').value || 21);
  const installs = budget / cpi;
  const baseRate = 0.33, lift = 0.05; // retención D7 base demo + lift del piloto
  const baseRet = installs * baseRate;
  const newRet = installs * (baseRate + lift);
  const extra = newRet - baseRet;
  const revenue = extra * ltv;
  const roi = revenue / 2500;
  document.getElementById('budgetResult').innerHTML =
    '<strong>' + installs.toFixed(0) + ' installs</strong> → retenidos base ~' + baseRet.toFixed(0) +
    ' · con piloto ~' + newRet.toFixed(0) + ' (<strong>+' + extra.toFixed(0) + '</strong>).<br>' +
    'Valor incremental: <strong>$' + revenue.toLocaleString('es-ES', { maximumFractionDigits: 0 }) + '</strong> con LTV $' + ltv +
    ' → <strong>' + roi.toFixed(1) + '×</strong> el coste del piloto (2.500 €). Supuesto: +5 pp en D7 validados en A/B.';
  document.getElementById('budgetResult').classList.add('show');
}
