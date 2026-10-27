# Pre-registro · ¿existe ALGUNA combinación?

Escrito y subido ANTES de medir. 22/09/2026.

## Por qué esta prueba y no la número 35

El usuario: *«sesiones + algo más debe funcionar, no sé si día anterior… algo,
debe existir algo»*.

Tiene razón en la queja: llevo tres meses probando de una en una. Sesiones +
barrido. Sesiones + FVG. Sesiones + H4. Sesiones + día previo. Sesiones + SMT.
Eso es un juego infinito — siempre queda un «y si además…».

**Esta prueba cambia el juego.** En vez de una hipótesis más, se le pregunta a
un modelo si existe **cualquier función** de todo lo que él ha mencionado en tres
meses que prediga la dirección. Si la respuesta es que no, no queda una idea
suelta por probar: **queda cerrado el espacio entero.**

Y `RESULTADOS_reloj.md`, de hoy, dice por qué era previsible: el reloj no aporta
dirección por sí mismo. Pero eso no descarta una **interacción** —que algo
funcione en una sesión y no en otra— y eso es justo lo que esto mide.

## Qué se mide

**Población**: todas las velas de **M15** de EURUSD dentro de sus horas
operativas (09-11 y 14-16:30, Madrid), 2021-2026. Sin condición de patrón: toda
vela entra.

**Objetivo**: ¿sube o baja el precio en las **4 horas** siguientes? (secundario:
hasta el cierre de la sesión).

**Variables, todas calculadas con datos cerrados en ese instante** — son las
piezas que él ha ido nombrando en tres meses:

| | |
|---|---|
| 1-3 | sesión, hora del día, minutos desde que abrió la sesión |
| 4 | día de la semana |
| 5-6 | posición dentro del rango de Asia (0 = mínimo, 1 = máximo), y ancho de ese rango en ATR |
| 7-8 | distancia a PDH y a PDL, en ATR |
| 9-10 | distancia a PWH y a PWL, en ATR |
| 11-12 | ¿se ha barrido ya hoy el máximo de Asia? ¿y el mínimo? |
| 13-14 | ¿se ha barrido ya hoy el PDH? ¿y el PDL? |
| 15-17 | momento de 1 h, 4 h y 1 día |
| 18-19 | ATR de M15 y cociente ATR corto / ATR largo |
| 20 | distancia a la apertura del día, en ATR |
| 21 | recorrido del día hasta ahora, sobre el ATR diario |
| 22 | distancia a la EMA 50 de M15, en ATR |

**El modelo**: gradient boosting. Entrenado con el pasado, evaluado sobre el
futuro, en **cinco bloques**. Nunca ve el futuro.

## Las tres cosas que se publican

1. **AUC fuera de muestra.** 0,500 = no sabe nada.
2. **El decil superior**: si el modelo elige el 10 % de momentos donde más
   confía, ¿cuánto acierta?
3. **Qué variables usa**, por importancia. Si el modelo encuentra algo, hay que
   poder mirar qué es.

Y dos controles:

- **Etiquetas barajadas**: el mismo modelo con el objetivo aleatorizado. Tiene
  que dar AUC 0,500. Si da más, hay fuga de información y la prueba no vale.
- **Sólo las variables de sesión** (1-4, 11-14): ¿aportan algo por sí solas?

## Criterio

1. **AUC fuera de muestra > 0,52** de forma estable en los cinco bloques, **y**
2. el decil superior con acierto por encima del umbral del coste, **y**
3. el control barajado en 0,500.

Un AUC de 0,52 es pequeño y sería suficiente: con miles de operaciones, una
ventaja así es real y se puede explotar. **No hace falta que sea grande. Hace
falta que exista.**

## Qué significa cada resultado, dicho antes

- **AUC ≈ 0,50** → no existe ninguna función de estas 22 variables que prediga
  la dirección. No es «no la hemos encontrado»: es que el modelo ha buscado en
  todo el espacio de combinaciones y no hay nada. **Eso cierra las sesiones y
  todo lo que se les pueda sumar.**
- **AUC > 0,52** → existe. Entonces se mira qué variables usa, se replica en oro
  y DAX, y se convierte en regla.

## Predicción

- **AUC entre 0,495 y 0,515.** Es lo que salió en `RESULTADOS_techo_filtro.md`
  (0,4945) con 14 variables sobre las operaciones de Benjamin, y esto es el
  mismo tipo de pregunta con más variables y sin condicionar a un patrón.
- El control barajado dará 0,500 y el decil superior no se separará de la media.
- Las variables «importantes» que salgan serán las de volatilidad, no las de
  dirección: el modelo aprenderá **cuánto** se mueve, no **hacia dónde**.
- Y por tanto el veredicto será que el espacio está cerrado.

Van diecisiete predicciones con errores. Ésta también puede fallar.
