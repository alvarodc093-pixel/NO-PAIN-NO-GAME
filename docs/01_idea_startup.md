# Día 10 — Idea, problema y startup (10 sept)

## 1. Las 3 ideas iniciales

### Idea A — No Pain, No Game (gaming / retención) — ELEGIDA
- **¿Qué problema existe?** Riot Games pierde cada año entre 15-25% de jugadores activos. Cada jugador que abandona deja de gastar (skins, pases) y debilita la comunidad (colas más largas, menos amigos online).
- **¿Quién tiene ese problema?** Riot Games (League of Legends, Valorant, TFT). Product Managers de Live-Ops, equipo de Growth y Monetización.
- **¿Por qué es importante?** Adquirir un jugador nuevo cuesta 5-7x más que retener uno. Una caída del 5% en churn equivale a millones en ingresos recurrentes + efecto red.
- **¿Qué pierde actualmente?** Ingresos (ARPU ~35€/año), engagement (horas jugadas), coste de adquisición desperdiciado, reputación si el jugador se va a la competencia.
- **¿Cómo ayudan los datos?** Logs de partidas, sesiones, compras, reportes de toxicidad y campañas permiten predecir quién se va a ir 30-60 días antes y por qué.
- **¿Por qué pagarían?** Porque un ranking semanal de "top 500 jugadores en riesgo + acción recomendada" es accionable y medible en ROI.

### Idea B — QueueCare (salud / listas de espera)
Predicción de no-shows en clínicas. Buena pero sin datos accesibles y cliente difuso.

### Idea C — StockSense (retail / inventario)
Predicción de rotura de stock. Interesante pero mercado muy competido y sin diferenciación clara.

## 2. Idea elegida: NO PAIN, NO GAME

- **Nombre:** No Pain, No Game
- **Sector:** Data Science para gaming / entretenimiento
- **Qué hace:** Startup especializada en crecimiento y retención de jugadores. Convierte logs de juego en decisiones: a quién retener, a quién atraer y cómo.
- **Cliente objetivo:** Riot Games (inicialmente equipo EUW de Live-Ops y Growth).
- **Problema que resuelve:** Abandono silencioso de jugadores actuales + adquisición ineficiente de nuevos jugadores.
- **Propuesta de valor:** "Detectamos al jugador que se va a ir antes de que se vaya, y te decimos qué hacer para que se quede — y qué perfiles traer para crecer."
- **Servicios / producto principal:**
  1. **Churn Score (producto principal):** probabilidad de abandono a 60 días por jugador (0-100%) + segmento de motivo + acción recomendada.
  2. **Player Conversion Score (segunda línea):** probabilidad de que un nuevo registro se convierta en habitual a 30 días.
  3. **Dashboard Live-Ops:** ranking de riesgo, alertas, simulador de campañas.

## 3. Enfoque para 5 días (recomendación mentor)

> Visión grande (Adquisición → Retención) pero proyecto concreto: **predicción de abandono**.
> La captación se presenta como segunda línea / análisis ligero, no con la misma profundidad.

```
                 NO PAIN, NO GAME
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
        NUEVOS JUGADORES       JUGADORES ACTUALES
             │                       │
       ¿Quién atraer?           ¿Quién se va?
             │                       │
      Conversion Score           Churn Score  ← FOCO DÍAS 13-14
             │                       │
             └───────────┬───────────┘
                         ▼
                 CRECIMIENTO DEL
                  PLAYER BASE
```

## 4. Definición oficial (para web y pitch)

> **No Pain, No Game es una startup de Data Science especializada en crecimiento y retención de jugadores. Ayuda a empresas de videojuegos a utilizar sus datos para atraer nuevos jugadores, detectar aquellos con riesgo de abandono y tomar decisiones que mejoren el crecimiento de su comunidad.**
>
> **Primer producto para Riot Games:** un sistema predictivo capaz de identificar jugadores actuales con alto riesgo de abandono y analizar qué perfiles y estrategias tienen mayor potencial para generar nuevos jugadores.

## Entregable día 10 — checklist
- [x] 3 ideas con las 6 preguntas
- [x] Idea elegida + problema + cliente + nombre + propuesta de valor
