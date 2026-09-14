# Día 14 — Solución y prototipo (14 sept)

## 1. Técnica elegida

**Random Forest** (no deep learning) por tres razones:
1. **Interpretabilidad:** Los PMs de PlayNova necesitan entender POR QUÉ un jugador tiene alto riesgo de churn. Un RF permite ver las top features y sus valores. El deep learning no.
2. **Datos tabulares pequeños:** 8k jugadores × ~15 features no necesitan redes neuronales. Un RF con 300 árboles es más rápido, más ligero y más robusto.
3. **Anti-leakage garantizado:** `days_since_last_session` se excluye del modelo explícitamente porque sería circular. Un RF puede verificar qué features se usan.

## 2. Métricas del modelo

### Churn Score (abandono 7d, threshold 0,50)
- **ROC-AUC:** 0,914 · **PR-AUC:** 0,950 · **Accuracy:** 0,844
- **Precision:** 0,888 · **Recall:** 0,878 · **F1:** 0,883
- **Matriz (test 1.600):** [[409, 119], [131, 941]] — falla en ambos sentidos, como en producción. Nada de recall 1,000.
- **Top features:** sesiones_7d 0.36, monedas 0.24, ads 0.12, boosters 0.07, nivel 0.06, tutorial 0.04, canal 0.03, país 0.03.

### Conversion Score (pago a 30 días, threshold 0,40 sintonizado por F1)
- **ROC-AUC:** 0,901 · **PR-AUC:** 0,279 · **Accuracy:** 0,913
- **Precision:** 0,362 · **Recall:** 0,758 · **F1:** 0,490
- **Matriz (test 600):** [[523, 44], [8, 25]] — con 5,4% de positivos, el PR-AUC manda sobre el ROC.
- **Lectura de negocio:** con threshold 0,40 capturamos el 76% de futuros pagadores; los falsos positivos cuestan un push, un pagador perdido cuesta LTV.
- **Top features:** días_hasta_2ª_sesión 0.31, duración_sesión_1 0.22, tutorial 0.16, canal 0.10, país 0.10.

## 3. Anti-leakage y reproducibilidad

- `days_since_last_session` **excluido** del modelo (verificable en código).
- Todos los features del modelo son **anteriores a la fecha de predicción** (ventana 7d desde la última sesión).
- Train/test split estratificado 80/20, seed 42, reproducible con `src/train.py`.
- Modelo guardado como `.pkl` con pipeline completo (preprocessing + modelo).

## 4. Prototipo web: ChurnGuard Dashboard

### Página Inicio — Hero
- Parallax con orb violeta/cyan, fondo `#14112b`.
- Título "CHURNGUARD" + subtítulo "Detecta el abandono antes de que ocurra".
- Contadores: 8K jugadores · ROC-AUC churn 0,914 · F1 churn 0,883 · ROC-AUC conversión 0,901.
- CTA: "Ver Demo" → Simulador.

### Página Datos
- Tabla de benchmarks con fuentes (D1 22%, D7 4%, D30 0,7%).
- Comparativa real (medida): orgánico 42,3% retenidos vs paid ~30% (TikTok 30,9%).
- Figuras del EDA (ads, canales, engagement).

### Página Solución
- Dos productos: **Churn Score 7d** + **Conversion Score 30d** (threshold 0,40).
- Tabla de métricas comparativa (ROC-AUC, precision, recall, F1).
- Explicación de anti-leakage.

### Página Demo — Simulador
- **Simulador:** sliders (tutorial %, amigos, sesiones 1–20) + selector de canal → gauge de riesgo con **motivo probable + acción del playbook**. Demo ilustrativa calibrada (declarado en la web), no el `.pkl` productivo.
- **Presets:** en riesgo (0, 0, 1, TikTok → ~80%) · típico TikTok (40, 2, 5 → ~51%) · sano orgánico (100, 5, 8 → ~7%).
- **Calculadora ROI:** CPI + budget + LTV → installs, retenidos base vs con piloto (+5 pp D7), € incremental y múltiplo sobre los 2.500 € del piloto.
- **Sección piloto:** alcance 4 semanas, A/B con métrica primaria D7, precio fijo 2.500 €, integración (`POST /score`, p95 <200 ms) y GDPR (IDs anonimizados, borrado a petición).
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
3. **Ranking de calidad de UA:** orgánico vs referral vs TikTok vs resto paid (CPI vs retención D7 × conversión).

## 6. Demo script semanal (para reunión con PlayNova)

1. **Problema (2 min):** "El 67% de vuestros jugadores abandona en 7 días. Con CPI $5 y 10k installs/mes, ~$33k/mes en UA sin retorno."
2. **Datos (2 min):** "8K jugadores, 3K leads, ~53K sesiones (seed 42), calibrados con GameAnalytics/Sensor Tower."
3. **Hallazgos (3 min):** "Tutorial ×2,2 retención. Orgánico 42% vs paid ~30%. La ventana crítica son 4 días."
4. **Producto (4 min):** "Simulador con motivo+acción; ranking semanal Top-100; threshold de conversión sintonizado a F1."
5. **Resultado (1 min):** "+5 pp en D7 validados en A/B = € incrementales calculados en la web con vuestro CPI y LTV."
6. **Next steps (2 min):** "Piloto 4 semanas, 2.500 € fijos, go/no-go por lift D7 con IC 95%."

## Entregable día 14 — checklist
- [x] Modelos entrenados (`models/churn_model.pkl`, `models/conversion_model.pkl`)
- [x] Métricas (ROC-AUC, precision, recall, F1) guardadas en `models/metrics.json`
- [x] Anti-leakage documentado y verificable
- [x] Web con 5 secciones + simulador ChurnGuard + calculadora budget
- [x] Playbook semanal y demo script
