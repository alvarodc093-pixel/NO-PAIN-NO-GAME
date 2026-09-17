# ChurnGuard — que ningún jugador se vaya sin avisar

**En una frase:** ayudamos a los juegos gratuitos (F2P) de PC a detectar qué jugadores necesitan atención, por qué y qué hacer.

Somos **NO PAIN NO GAME**. Cliente piloto: **PlayNova Games**.

---

## 1. Ver la web en tu ordenador (30 segundos)

La web está en la carpeta `web/`. Es solo HTML/CSS/JS, no hay que instalar nada.

**Opción A - la más fácil:**
1. Abre la carpeta `web`
2. Doble clic en `index.html`

**Opción B - como se verá online (recomendada para presentar):**
```bash
cd web
python -m http.server 8321
```
Luego abre en el navegador: `http://localhost:8321`

Qué vas a ver: problema → datos reales → solución → demo con sliders → piloto 4 semanas. Arriba a la derecha puedes cambiar idioma 🇪🇸 🇬🇧 🇫🇷 🇩🇪.

---

## 2. Ver la web online (Vercel)

Una vez desplegada, la URL es algo como:

`https://tu-proyecto.vercel.app`

Cada vez que subes un cambio a `main` en GitHub, Vercel la actualiza sola.

---

## 3. Re-desplegar desde cero (2 minutos)

Solo necesitas la cuenta de GitHub con este repo.

1. Entra en `vercel.com/new`
2. `Add GitHub Account` si es la primera vez, y elige este repo: `alvarodc093-pixel/NO-PAIN-NO-GAME`
3. En la pantalla de configuración pon esto **tal cual**:
   - `Framework Preset: Other`
   - `Root Directory: web`
   - `Build Command:` vacío (nada)
   - `Output Directory:` vacío (nada)
4. Pulsa `Deploy`. En ~30s te da la URL.

> ¿Por qué `Root Directory: web`? Porque en la raíz del repo hay Python (`requirements.txt`, `src/`) del análisis de datos. Si dejas Root en `./`, Vercel cree que es un backend Python y falla. Apuntando a `web` solo ve la página estática y funciona siempre.

Para actualizar: solo haz `git push origin main`. No hay que tocar nada en Vercel.

---

## 4. Si algo falla al desplegar

| Error | Causa | Solución |
|---|---|---|
| `No python entrypoint found` | Root Directory en `./`, detecta Python | Pon `Root Directory: web`, `Framework: Other` |
| `points to a different repository` | El proyecto Vercel está conectado a otro repo | `Project > Settings > Git > Disconnect` y conecta el repo correcto |
| `could not find branch or commit` | Vercel pide una rama que no existe | `Settings > Git > Production Branch = main`. No re-despliegues commits viejos, haz un push nuevo |

El fichero `vercel.json` de la raíz ya está como respaldo:
```json
{ "framework": null, "buildCommand": null, "outputDirectory": "web" }
```
Pero lo que manda es el `Root Directory: web` del paso 3.

---

## 5. Nuestros datos (en simple)

- **18.099 opiniones públicas de Steam** (14-09-2026) de 6 juegos: Dota 2, TF2, Warframe, Path of Exile, Apex Legends, Fall Guys.
- **16.447 jugadores** etiquetados. El resto no tenía datos suficientes.
- Horas jugadas y nº de juegos salen de la API pública de Steam (`appreviews/{appid}?json=1`, bloque `author`: `playtime_forever`, `playtime_at_review`, `num_games_owned`...). Ver `src/fetch_steam_reviews.py` y `src/build_real_dataset.py`.
- El 91% de Fall Guys **no** es su abandono real, es solo dentro de nuestra muestra de reseñistas. Lo avisamos en la web.

## 6. Para curiosos (técnico)

```bash
pip install -r requirements.txt
python src/fetch_steam_reviews.py    # descarga opiniones
python src/build_real_dataset.py     # crea data/playnova_real.db
python src/train_real.py             # entrena modelos en models/
```

Estructura: `web/` página · `src/` programas · `data/` base de datos · `models/` modelos · `notebooks/` análisis · `docs/` explicaciones.

---
ChurnGuard — NO PAIN NO GAME · 2026 · Datos públicos de Steam.
