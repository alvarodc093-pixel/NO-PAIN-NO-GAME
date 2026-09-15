# Día 10 — Idea, problema y startup (10 sept)

## 1. Las 3 ideas iniciales

### Idea A — ChurnGuard (PC F2P / retención) — ELEGIDA
- **¿Qué problema existe?** Los juegos F2P pierden a la mayoría de nuevos jugadores en la primera semana (D1 22% mediana, D7 4%, D30 0,7% · GameAnalytics 2026, referencia mercado F2P). Los publishers gastan miles de millones en adquisición (UA) sin retorno porque no saben quién va a abandonar en 7 días ni quién se convertirá en jugador de pago.
- **¿Quién tiene ese problema?** PlayNova Games (ficticio, mid-tier publisher PC free-to-play en Steam: shooter por equipos, survival co-op, action RPG). Product Managers de Live-Ops, equipo de Growth y Monetización.
- **¿Por qué es importante?** Adquirir un jugador nuevo cuesta $3-8 (CAC medio PC F2P vía Steam/creadores). Si 2 de cada 3 se van en 7 días, el CAC se pierde. Retener un solo jugador genera $15-50 de LTV (lifetime value).
- **¿Qué pierde actualmente?** Gasto de UA desperdiciado (CPI sin conversión), churn silencioso (el jugador no reporta nada, simplemente deja de jugar), oportunidad de monetización perdida, reputación (1 estrella en store review).
- **¿Cómo ayudan los datos?** Eventos del juego (sesiones, tutorial progreso, compras, notificaciones, sesión length) permiten predecir quién abandona en 7 días y quién se convertirá en paying player a 30 días.
- **¿Por qué pagarían?** Porque un ranking semanal de "Top-100 jugadores en riesgo de D1-churn + acción de onboarding personalizada" es accionable y medible en LTV recuperado.

### Idea B — StreamInsight (streaming / viewers)
- Predicción de churn de viewers en Twitch/YouTube. Interesante pero datos de viewer poco estandarizados y cliente difuso.

### Idea C — NewsPulse (news / engagement)
- Predicción de abandono de suscriptores de newsletters. Buen problema pero sin API de engagement estandarizada y sin dataset limpio.

## 2. Idea elegida: CHURNGUARD (PC F2P)

- **Nombre:** ChurnGuard
- **Sector:** Data Science para gaming PC / entretenimiento F2P
- **Qué hace:** Startup especializada en retención de jugadores y monetización para juegos PC free-to-play (Steam). Convierte eventos de juego en decisiones: a quién retener, a quién re-enganchar y quién va a ser paying player.
- **Cliente objetivo:** PlayNova Games (ficticio, mid-tier publisher PC F2P en Steam, 3 títulos, ~2M MAU).
- **Problema que resuelve:** Abandono silencioso de jugadores actuales (churn 7d ~67% en demo) + adquisición ineficiente de nuevos jugadores.
- **Propuesta de valor:** "Detectamos al jugador que va a dejar el juego antes de que lo haga, y al lead que se quedará jugando antes de que empiece — con acciones automatizadas de onboarding y re-engagement."
- **Servicios / producto principal:**
  1. **Churn Score 7d (producto principal):** probabilidad de abandono a 7 días por jugador (0-100%) + motivo de desenganche + acción de retención automatizada.
  2. **Conversion Score (segunda línea):** probabilidad de que un nuevo registro (install) se convierta en jugador de pago a 30 días — para optimizar el budget de UA.
  3. **Dashboard Live-Ops:** ranking de riesgo D1, alertas de churn masivo, simulador de campañas de re-engagement.

## 3. Enfoque para 5 días (recomendación mentor)

> Visión grande (Adquisición → Retención → Monetización) pero proyecto concreto: **predicción de abandono D1 y conversión a pago**.
> La captación se presenta como segunda línea / análisis ligero, no con la misma profundidad.

```
                 CHURNGUARD
                        │
            ┌───────────┴───────────┐
            ▼                       ▼
     NUEVOS JUGADORES       JUGADORES ACTIVOS
            │                       │
      ¿Quién se convierte?    ¿Quién abandona?
            │                       │
    Conversion Score         Churn Score 7d ← FOCO DÍAS 13-14
       (pago a 30d)           (abandono a 7d)
            │                       │
            └───────────┬───────────┘
                        ▼
               CRECIMIENTO DEL
                  PLAYER BASE
```

## 4. Definición oficial (para web y pitch)

> **ChurnGuard es una startup de Data Science especializada en retención y monetización para juegos PC F2P (Steam). Ayuda a publishers a utilizar datos de eventos de juego para detectar jugadores con riesgo de abandono en 7 días, re-engancharlos con acciones de onboarding automatizadas y predecir qué nuevos jugadores se convertirán en jugadores de pago.**
>
> **Primer producto para PlayNova Games:** un sistema predictivo capaz de identificar jugadores actuales con alto riesgo de churn D1 y analizar qué perfiles de nuevos installs se convierten a paying.

## Entregable día 10 — checklist
- [x] 3 ideas con las 6 preguntas
- [x] Idea elegida + problema + cliente + nombre + propuesta de valor
- [x] Enfoque de 5 días con FOCO DÍAS 13-14
