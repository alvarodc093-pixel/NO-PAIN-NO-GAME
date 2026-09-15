# ChurnGuard — que ningún jugador se vaya sin avisar

**En una frase:** ayudamos a los equipos de videojuegos gratuitos (F2P) de PC a detectar a tiempo qué jugadores necesitan atención, por qué y qué hacer.

Somos **NO PAIN NO GAME**, una startup que usa datos para que los juegos gratuitos de PC retengan a sus jugadores. Nuestro cliente piloto es **PlayNova Games**, una empresa de juegos gratuitos para PC en Steam.

---

## El problema, con un ejemplo

Imagina que alguien descarga un juego, juega unas horas, se atasca en el tutorial… y un día deja de entrar. No se queja, no avisa. Simplemente desaparece.

Eso les pasa a miles de jugadores cada semana. Y cada jugador que se va es dinero perdido: conseguirlo costó entre 3 y 8 dólares, y nunca llegó a quedarse.

**La pregunta que nos hicimos:** ¿y si pudiéramos ver las primeras señales y actuar antes de que se vayan?

## Qué hace ChurnGuard

Cada lunes, el equipo del juego abriría una lista clara:

| Jugador | Riesgo | Motivo | Qué hacer |
|---|---|---|---|
| r88210 | 83% | Jugó muy pocas horas al principio | Ayuda con el tutorial + evento diario |
| r55201 | 44% | No recomienda el juego | Soporte y oferta para que siga |
| r77340 | 9% | Todo bien | No hacer nada |

Nada de magia: convertimos **señales → prioridad + motivo + acción**. Y también señalamos qué perfiles se parecen a los jugadores más valiosos, para cuidar mejor el presupuesto.

## Nuestros datos: reales, no inventados

- Analizamos **18.099 opiniones públicas de Steam** (con fecha 14-09-2026) de 6 juegos gratuitos conocidos: Dota 2, Team Fortress 2, Warframe, Path of Exile, Apex Legends y Fall Guys.
- De ahí estudiamos **16.447 jugadores** (el resto no tenía información suficiente y lo dejamos fuera).
- Todo se puede comprobar: decimos de dónde sale cada dato y qué limitaciones tiene.

## Qué descubrimos (en palabras simples)

1. **Las primeras horas deciden.** Los que juegan poquísimo al principio se van mucho más (35,7%) que los que juegan mucho (13,2%).
2. **Que te guste el juego no basta.** Los que lo recomiendan se van casi igual (26,5%) que los que no (29,6%). La nota no lo es todo: importa el hábito.
3. **Cada juego vive su momento.** Dota 2 recibe 3.000 opiniones en 3 días; Fall Guys tarda 470. Cada juego necesita su propia estrategia.

Y algo importante: ese famoso “91% de Fall Guys” **no** significa que el 91% de sus jugadores lo haya dejado. Es solo el porcentaje dentro de las personas que escribieron una opinión en nuestra muestra. Lo explicamos así de claro en la web.

## La web: qué vas a ver

Abre `web/index.html` (o sírvela con `python -m http.server 8321` dentro de la carpeta `web` y entra en `http://localhost:8321`):

- **El problema**, contado con 3 tarjetas muy visuales.
- **Los datos**, con la tabla de los 6 juegos y 3 gráficos que **se amplían al pincharlos** (ideal para presentar).
- **La solución**: dos puntuaciones explicadas sin tecnicismos.
- **La demo**: mueve los controles (horas, juegos, antigüedad, título) y mira cómo cambian la prioridad, el motivo y la acción. Incluye una calculadora de ejemplo (es una estimación, no una promesa de ingresos).
- **El piloto de 4 semanas** (2.500 €): cómo lo probaríamos con datos reales del cliente.
- **Idiomas**: arriba a la derecha puedes cambiar entre 🇪🇸 español, 🇬🇧 inglés, 🇫🇷 francés y 🇩🇪 alemán. Toda la página se traduce al momento.

## Queremos ser honestos

- **No adivinamos el futuro.** Ayudamos a decidir dónde actuar antes.
- **La demo es una ilustración**, no el modelo final. El modelo real se probaría con los datos del cliente.
- **No sabemos quién va a gastar dinero** (Steam no publica eso). Usamos una aproximación transparente y lo decimos en todas partes.
- **Mostramos lo que no sabemos**: la muestra son personas que escribieron opiniones, no todos los jugadores.

## Si tienes curiosidad técnica (opcional)

<details>
<summary>Cómo se construyó, paso a paso</summary>

```bash
pip install -r requirements.txt
python src/fetch_steam_reviews.py    # descarga las 18k opiniones (~5 min)
python src/build_real_dataset.py    # ordena y etiqueta los datos
python src/train_real.py            # entrena los dos modelos
python notebooks/02_eda_real.py     # crea los 3 gráficos
python src/eval_per_title.py        # comprueba que funciona juego por juego
cd web
python -m http.server 8321          # abre la web en http://localhost:8321
```

- Modelos: Churn (acierta ~8 de cada 10 que marca) y Alto valor (precisión 0,77, detecta el 93% de los valiosos). Detalles en `models/real_metrics.json`.
- Estructura: `docs/` (explicaciones día a día), `web/` (la página), `src/` (programas), `data/` (base de datos), `models/` (modelos), `notebooks/` (análisis).

</details>

---

ChurnGuard — NO PAIN NO GAME · 2026 · Cliente piloto: PlayNova Games · Datos públicos de Steam.
