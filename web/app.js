// Nav scroll shadow
window.addEventListener('scroll', () => {
  document.getElementById('navbar').classList.toggle('scrolled', window.scrollY > 50);
});

// Counter animation
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.counter .num').forEach(el => {
    const text = el.textContent;
    const target = parseFloat(text.replace(',', '').replace('%', ''));
    if (isNaN(target)) return;
    const isPercent = text.includes('%');
    let current = 0;
    const step = target / 60;
    const intv = setInterval(() => {
      current += step;
      if (current >= target) { current = target; clearInterval(intv); }
      el.textContent = isPercent ? current.toFixed(1) + '%' : current.toLocaleString(undefined, { maximumFractionDigits: 1 });
    }, 20);
  });
});

// Simulator
function updateSim() {
  const tut = +document.getElementById('tutorial').value;
  const fri = +document.getElementById('friends').value;
  const ses = +document.getElementById('sessions').value;
  document.getElementById('tutVal').textContent = tut;
  document.getElementById('friVal').textContent = fri;
  document.getElementById('sesVal').textContent = ses;
  let score = 88 - (tut * 0.5) - (fri * 2.5) - (ses * 3);
  score = Math.max(2, Math.min(99, score));
  const circumference = 2 * Math.PI * 80;
  const offset = circumference * (1 - score / 100);
  document.getElementById('gaugeArc').style.strokeDashoffset = offset;
  const arc = document.getElementById('gaugeArc');
  arc.style.stroke = score > 70 ? '#ef4444' : score > 40 ? '#f59e0b' : '#22d3ee';
  document.getElementById('gaugeVal').textContent = score + '%';
}

function setPreset(t, f, s) {
  document.getElementById('tutorial').value = t;
  document.getElementById('friends').value = f;
  document.getElementById('sessions').value = s;
  updateSim();
}

function calcBudget() {
  const cpi = +document.getElementById('cpi').value;
  const budget = +document.getElementById('budget').value;
  const installs = budget / cpi;
  const retained = installs * 0.22 * 1.5;
  const lost = installs - retained;
  const ltvRecovered = retained * 3.5;
  document.getElementById('budgetResult').innerHTML = `<strong>Resultado:</strong> ${installs.toFixed(0)} installs · ~${retained.toFixed(0)} retenidos · ~${lost.toFixed(0)} perdidos · LTV recuperada: $${ltvRecovered.toFixed(0)}`;
}

// FAQ toggle
document.querySelectorAll('.faq-item h4').forEach(h => {
  h.addEventListener('click', () => h.parentElement.classList.toggle('open'));
});
