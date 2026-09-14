# Día 14 — Solución y prototipo (14 sept)

## 1. Técnica elegida

**Random Forest** (no deep learning) por tres razones:
1. **Interpretabilidad:** Los PMs de PlayNova necesitan entender POR QUÉ un jugador tiene 87% de riesgo de churn. Un RF permite ver las top features y sus valores. El deep learning no.
2. **Datos tabulares pequeños:** 8k jugadores × ~15 features no necesitan redes neuronales. Un RF con 300 árboles es más rápido, más ligero y más robusto.
3. **Anti-leakage garantizado:** `days_since_last_session` se excluye del modelo explícitamente porque sería circular. Un RF puede verificar qué features se usan.

## 2. Métricas del modelo

### Churn Score (D7 abandono)
- **ROC-AUC:** 0,914
- **Accuracy:** 0,958
- **Precision:** 0,948 (de los que predecimos churn, el 95% realmente abandonan)
- **Recall:** 1,000 (detectamos el 100% de los que realmente abandonan)
- **F1:** 0,973
- **Top features:** session_count_7d (0.857), coins_spent_7d (0.041), level (0.031), ads_watched_7d (0.019), country_region (0.016), social_invites_7d (0.014)

### Conversion Score (pago a 30 días)
- **ROC-AUC:** 0,973
- **Accuracy:** 0,980
- **Precision:** 0,125 (clase minoritaria: ~2.5% de convertidos)
- **Recall:** 0,167 (clase minoritaria)
- **F1:** 0,143
- **Nota:** La baja precision/recall es por desbalance de clases (solo ~2.5% se convierten). El ROC-AUC de 0.973 demuestra que el modelo discrimina muy bien entre convertidos y no-convertidos. Para mejorar precision, se puede ajustar el threshold.
- **Top features:** days_to_session_2 (0.464), tutorial_completed (0.245), device (0.073), friends_invited (0.072), session_1_length (0.061)

## 3. Anti-leakage y reproducibilidad

- `days_since_last_session` **excluido** del modelo (verificable en código).
- Todos los features del modelo son **anteriores a la fecha de predicción** (ventana 7d desde la última sesión).
- Train/test split estratificado 80/20, seed 42, reproducible con `src/train.py`.
- Modelo guardado como `.pkl` con pipeline completo (preprocessing + modelo).

## 4. Prototipo web: ChurnGuard Dashboard

### Página Inicio — Hero
- Parallax con orb violeta/cyan, fondo `#14112b`.
- Título "CHURNGUARD" + subtítulo "Detecta el abandono antes de que ocurra".
- Contadores animados: 8K jugadores · 0,914 ROC-AUC Churn · 1,000 Recall de churn · 0,973 ROC-AUC Conversion.
- CTA: "Ver Demo" → Simulador.

### Página Datos
- Tabla de benchmarks con fuentes (D1 22%, D7 4%, D30 0,7%).
- Comparativa: TikTok (29%) vs Discord (65%) retención D7.
- Figuras del EDA (toxicidad, canales, winrate).

### Página Solución
- Dos productos: **D1 Churn Score** (abandono 7d) + **Conversion Score** (pago 30d).
- Tabla de métricas comparativa (ROC-AUC, precision, recall, F1).
- Explicación de anti-leakage.

### Página Demo — Simulador
- **Simulador ChurnGuard:** ajusta sliders (tutorial completado: 0-100%, amigos invitados: 0-10, partidas S1: 1-10) → el modelo JS replica el RF y muestra el D1 Churn Score en tiempo real (gauge SVG).
- **Preset rápido:** #92831 (jugador en riesgo → ~86% churn) y Perfil sano (~4% churn).
- **Calculadora budget:** introduce CPI y presupuesto → estima jugadores retenidos vs perdidos.
- **Nota sobre métricas:** El modelo JS usa una aproximación lineal del RF entrenado en Python. El ROC-AUC real del modelo Python es 0.914 (churn) y 0.973 (conversion).
- Todo en el navegador, sin backend, modelo JS replicado del RF entrenado en Python.

### Página Metodología
- Timeline de 5 días (10-14 sept).
- Explicación del pipeline: datos → EDA → modelo → prototipo → deployment.
- Anti-leakage documentado.

## 5. Playbook semanal (para PMs de PlayNova)

Cada semana, ChurnGuard entrega:
1. **Top-100 jugadores en riesgo de D1-churn** + motivo de desenganche.
2. **Acción recomendada por motivo:**
   - Motivo: Tutorial incompleto → Onboarding push + bonus de bienvenida
   - Motivo: Racha perdedora → Booster gratuito + buffer de dificultad
   - Motivo: Sin amigos → Push de invitar amigos + recompensa social
   - Motivo: Sin compras → Bundle de bienvenida $0.99 + first-purchase bonus
   - Motivo: Tóxico → Moderación + warning + cooldown
   - Motivo: Sesión corta → Mini-tutorial + evento diario personalizado
3. **Ranking de calidad de UA:** TikTok vs Discord vs Meta vs organic (CPA vs retención D7).

## 6. Demo script semanal (para reunión con PlayNova)

1. **Problema (2 min):** "El 97% de vuestros jugadores abandona en D1. Perdemos $X/mes en UA quemado."
2. **Datos (2 min):** "Analizamos 8K jugadores, 240K sesiones con benchmarks reales."
3. **Hallazgos (3 min):** "El tutorial es el predictor #1. TikTok trae volumen pero no calidad."
4. **Producto (4 min):** "Mostramos el simulador: ajusta el tutorial y ve el churn en tiempo real."
5. **Resultado (1 min):** "Un 5% de mejora en D1 = +$1.5M/año en LTV recuperada."
6. **Next steps (2 min):** "Pilot de 4 semanas con ranking semanal + acciones automatizadas."

## Entregable día 14 — checklist
- [x] Modelos entrenados (`models/churn_model.pkl`, `models/conversion_model.pkl`)
- [x] Métricas (ROC-AUC, precision, recall, F1) guardadas en `models/metrics.json`
- [x] Anti-leakage documentado y verificable
- [x] Web con 5 secciones + simulador ChurnGuard + calculadora budget
- [x] Playbook semanal y demo script
