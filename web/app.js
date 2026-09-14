/* NO PAIN, NO GAME — interacciones refinadas */
(function () {
  "use strict";

  /* ===== barra de progreso ===== */
  const prog = document.getElementById("progress");
  addEventListener("scroll", () => {
    const h = document.documentElement;
    const p = h.scrollTop / (h.scrollHeight - h.clientHeight);
    prog.style.width = (p * 100).toFixed(2) + "%";
  }, { passive: true });

  /* ===== nav con sombra al scroll ===== */
  const nav = document.getElementById("nav");
  addEventListener("scroll", () => {
    nav.classList.toggle("scrolled", scrollY > 40);
  }, { passive: true });

  /* ===== parallax de orbes ===== */
  const orbs = [...document.querySelectorAll(".orb[data-parallax]")];
  addEventListener("scroll", () => {
    const cx = scrollY * 0.3;
    orbs.forEach((orb) => {
      const f = parseFloat(orb.dataset.parallax);
      orb.style.transform = "translateY(" + (cx * f).toFixed(1) + "px)";
    });
  }, { passive: true });

  /* ===== menú móvil ===== */
  const burger = document.getElementById("burger");
  const links = document.getElementById("navLinks");
  burger.addEventListener("click", () => links.classList.toggle("open"));
  links.addEventListener("click", (e) => { if (e.target.tagName === "A") links.classList.remove("open"); });

  /* ===== reveal con stagger ===== */
  const io = new IntersectionObserver((es) => {
    es.forEach((e) => {
      if (!e.isIntersecting) return;
      const d = parseInt(e.target.dataset.delay || "0", 10);
      setTimeout(() => e.target.classList.add("visible"), d);
      io.unobserve(e.target);
    });
  }, { threshold: 0.12 });
  document.querySelectorAll(".reveal").forEach((el) => io.observe(el));

  /* ===== contadores animados ===== */
  const cio = new IntersectionObserver((es) => {
    es.forEach((e) => {
      if (!e.isIntersecting) return;
      const el = e.target, target = parseFloat(el.dataset.count), dec = parseInt(el.dataset.dec || "0", 10);
      const t0 = performance.now(), dur = 1400;
      (function tick(t) {
        const k = Math.min(1, (t - t0) / dur), ease = 1 - Math.pow(1 - k, 3);
        el.textContent = (target * ease).toFixed(dec);
        if (k < 1) requestAnimationFrame(tick);
      })(t0);
      cio.unobserve(el);
    });
  }, { threshold: 0.6 });
  document.querySelectorAll("[data-count]").forEach((el) => cio.observe(el));

  /* ===== barras animadas ===== */
  const bio = new IntersectionObserver((es) => {
    es.forEach((e) => { if (e.isIntersecting) { e.target.style.width = e.target.dataset.w + "%"; bio.unobserve(e.target); } });
  }, { threshold: 0.5 });
  document.querySelectorAll(".bar span").forEach((el) => bio.observe(el));

  /* ===== nav activa ===== */
  const secs = [...document.querySelectorAll("section[id]")];
  const navA = [...document.querySelectorAll(".nav .links a")];
  const sio = new IntersectionObserver((es) => {
    es.forEach((e) => {
      if (!e.isIntersecting) return;
      navA.forEach((a) => a.classList.toggle("active", a.getAttribute("href") === "#" + e.target.id));
    });
  }, { rootMargin: "-40% 0px -55% 0px" });
  secs.forEach((s) => sio.observe(s));

  /* ===== tabs ===== */
  document.querySelectorAll(".tab").forEach((t) => {
    t.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((x) => x.classList.remove("active"));
      t.classList.add("active");
      document.getElementById("tab-sim").classList.toggle("hidden", t.dataset.tab !== "sim");
      document.getElementById("tab-budget").classList.toggle("hidden", t.dataset.tab !== "budget");
    });
  });

  /* ===== simulador churn ===== */
  const $ = (id) => document.getElementById(id);
  const ACCIONES = {
    "Quemado por derrotas": "Misión comeback + emparejar con squad de su nivel",
    "Expulsado por toxicidad": "Sugerir squad cerrado + mute-guía + pausa recompensada",
    "Solo sin squad": "Sugerir club/Discord + bonus por jugar en grupo",
    "Desenganchado silencioso": "Push con recompensa 7 días + evento de temporada",
    "Nunca enganchó al pago": "Oferta pase de batalla + skin de su main",
    "Bajada de actividad": "Contenido personalizado + recordatorio de amigos online"
  };
  function score(v) {
    const logit = 0.64 - 0.06 * v.m30 - 0.08 * v.m7 - 0.037 * (v.wr - 50)
      - 0.24 * (v.kda - 2.5) + 0.28 * v.tox + 0.0094 * (v.solo - 50)
      - 0.02 * Math.min(v.gasto, 40) - 0.067 * v.activ;
    return 1 / (1 + Math.exp(-logit));
  }
  function motivo(v) {
    if (v.wr < 42 && v.m30 >= 7) return "Quemado por derrotas";
    if (v.tox >= 2) return "Expulsado por toxicidad";
    if (v.solo > 66 && v.m30 >= 4) return "Solo sin squad";
    if (v.m30 <= 4 && v.activ <= 4) return "Desenganchado silencioso";
    if (v.gasto === 0 && v.m30 <= 8) return "Nunca enganchó al pago";
    return "Bajada de actividad";
  }
  const ARC = 267;
  function renderSim() {
    const v = {};
    ["m30", "m7", "wr", "kda", "tox", "solo", "gasto", "activ"].forEach((k) => {
      v[k] = parseFloat($("in-" + k).value);
      $("v-" + k).textContent = k === "kda" ? v[k].toFixed(1) : v[k];
    });
    const p = score(v), m = motivo(v);
    $("gaugeTxt").textContent = Math.round(p * 100) + "%";
    const lvl = p >= 0.7 ? "🔴 prioritario" : (p >= 0.4 ? "🟡 vigilar" : "🟢 sano");
    $("gaugeLvl").textContent = lvl;
    const arc = $("gaugeArc");
    arc.style.strokeDashoffset = ARC * (1 - p);
    arc.style.stroke = p >= 0.7 ? "#ef4444" : (p >= 0.4 ? "#f59e0b" : "#22c55e");
    $("out-motivo").textContent = m;
    $("out-accion").textContent = ACCIONES[m];
  }
  ["m30", "m7", "wr", "kda", "tox", "solo", "gasto", "activ"].forEach((k) =>
    $("in-" + k).addEventListener("input", renderSim));
  $("preset-risk").addEventListener("click", () => {
    const p = { m30: 6, m7: 1, wr: 35, kda: 1.8, tox: 3, solo: 85, gasto: 0, activ: 4 };
    Object.entries(p).forEach(([k, val]) => { $("in-" + k).value = val; });
    renderSim();
  });
  $("preset-healthy").addEventListener("click", () => {
    const p = { m30: 20, m7: 6, wr: 55, kda: 3.0, tox: 0, solo: 30, gasto: 25, activ: 18 };
    Object.entries(p).forEach(([k, val]) => { $("in-" + k).value = val; });
    renderSim();
  });
  renderSim();

  /* ===== calculadora budget ===== */
  function budget() {
    const b = parseFloat($("in-budget").value), t = parseFloat($("in-tiktok").value);
    $("v-budget").textContent = b;
    $("v-tiktok").textContent = t;
    const ret = b * t / 100 / 8 * 0.29 + (b - b * t / 100) / 8 * 0.60;
    $("out-retenidos").textContent = Math.round(ret).toLocaleString("es-ES");
  }
  $("in-budget").addEventListener("input", budget);
  $("in-tiktok").addEventListener("input", budget);
  budget();
})();
