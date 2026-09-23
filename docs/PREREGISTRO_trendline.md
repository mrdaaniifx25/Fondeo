# Preregistro · rotura de línea de tendencia en M5

Escrito antes de correr nada.

## Qué es una línea de tendencia, en código

Una línea de tendencia no es un dibujo: es dos pivotes unidos y prolongados. Se
define así, sin ambigüedad y sin mirar al futuro:

```
PIVOTE ALTO en j   H[j] es el maximo de las w velas de cada lado.
                   Se confirma en j+w, no antes: hasta ahi no se puede usar.
PIVOTE BAJO en j   igual con los minimos.

RESISTENCIA        dos pivotes altos p1 < p2 con H[p1] > H[p2].
                   linea(i) = H[p1] + pendiente*(i - p1),  pendiente < 0
SOPORTE            dos pivotes bajos p1 < p2 con L[p1] < L[p2].

VALIDA si          ningun cierre entre p1 y ahora ha quedado al otro lado,
                   p2 - p1 >= 3 velas, y no han pasado mas de 60 velas desde p2.

ROTURA             el cierre de esta vela cruza la linea y el de la anterior no.
ENTRADA            al cierre de esa vela, en el sentido de la rotura.
```

`w = 2` (fractal de cinco velas), fijo, sin ajustar.

## Diseño

- **Instrumento principal**: EURUSD. Los otros seis solo para comprobar el signo.
- **Velas de M5**, 2020-2026. Resolución en **M1**, que es donde se ve si llegó
  antes el stop o el objetivo.
- **Dos sitios para el stop**, declarados de antemano:
  ```
  A · el extremo de la vela que rompe        (pegado, como opera el)
  B · el ultimo pivote contrario antes de romper   (estructural, mas ancho)
  ```
- **k = 1, 2 y 3.**
- **Dos ventanas**: Londres 08:00-11:30 con corte a las 11:30, y todo el día con
  corte a las 22:00.
- Una posición viva; las roturas que llegan con algo abierto se descartan.
- Coste **1,43 pips** de ida y vuelta.

## Contraste principal

**Doce celdas** (2 stops × 3 k × 2 ventanas) en EURUSD. Bonferroni: hace falta
**|z| > 2,87** en R neta (p < 0,0042), y que el signo aguante en **5 de los 7
instrumentos**.

## Predicción firmada

Escrita sabiendo lo que dice el muro del coste, y por eso mismo:

1. El stop A quedará **entre 4 y 9 pips** y el B **entre 10 y 20**.
2. **Ninguna de las doce celdas pasará el umbral.** Con el stop A el coste será
   el 16-35 % del riesgo y haría falta batir a la geometría por 5-12 puntos;
   ninguna regla de este proyecto ha pasado de +4,1.
3. El acierto de cada celda quedará **a menos de 3 puntos de su geometría**.
4. **El stop B saldrá menos malo que el A** en R neta, por el coste, no por
   acierto: es la misma ley que se midió en `RESULTADOS_regla_stops.md`.
5. La ventana de Londres **no será mejor** que el día entero. Se ha medido tres
   veces en este proyecto y nunca lo ha sido.

Si alguna celda sale con z > +2,87 y el signo aguanta en cinco instrumentos, me
he equivocado y es la primera familia intradía que funciona.

## Declarados de antemano como secundarios

1. Reparto por instrumento.
2. Resistencia contra soporte.
3. Cuántas velas aguanta la línea antes de romperse.
4. Coste de equilibrio de cada celda.

## Qué contaría como hallazgo

**z > +2,87 en R neta** en EURUSD, signo consistente en **≥ 5 de 7**
instrumentos, y **coste de equilibrio al menos el doble** de 1,43. Nada por
debajo cuenta.
