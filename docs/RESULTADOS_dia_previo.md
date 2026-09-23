# Resultados · máximo y mínimo del día previo, disparo en M5/M15

Pre-registro `e77d17e`, subido antes de medir. Código `bt/dia_previo.py`.
EURUSD, oro y DAX. Resolución en M1, barreras por toque, horizonte 24 h.

## Veredicto

**No cumple el criterio.** Ninguna de las 18 celdas.

### EURUSD

| celda | n | acierto | azar | exceso | R:R | riesgo | coste | **neta** |
|---|---|---|---|---|---|---|---|---|
| M5 · nivel opuesto | 1 310 | 5,7 % | 7,4 % | **−1,7** | 17,2 | 3,5 p | **40,9 %** | **−0,823** |
| M5 · 1:1 | 1 310 | 50,3 % | 50,0 % | +0,3 | 1,0 | 3,5 p | 40,9 % | −0,622 |
| M5 · 1:2 | 1 310 | 34,0 % | 33,3 % | +0,7 | 2,0 | 3,5 p | 40,9 % | −0,606 |
| M15 · nivel opuesto | 1 265 | 8,4 % | 11,0 % | **−2,6** | 10,8 | 5,4 p | 26,5 % | −0,658 |
| M15 · 1:1 | 1 266 | 50,9 % | 50,0 % | +0,9 | 1,0 | 5,4 p | 26,5 % | −0,385 |
| **M15 · 1:2** | 1 266 | 36,0 % | 33,3 % | **+2,7** [+0,0, +5,3] | 2,0 | 5,4 p | 26,5 % | −0,321 |

### Oro y DAX

Todas las celdas con exceso entre **−3,5 y −1,2** y neta entre **−0,23 y −0,59**.
La única celda con exceso positivo en EURUSD (M15 · 1:2, +2,7) sale **−1,9 en
oro y −1,9 en DAX**. El criterio de réplica en 2 de 3 no se cumple.

## De qué se muere, y es lo único que hay que llevarse

**Del coste. Y por una razón que no depende de la señal.**

El stop es el extremo de **una vela de 5 minutos**. En EURUSD eso son **3,5
pips**. Con 1,43 pips de coste:

```
coste = 1,43 / 3,5 = 40,9 % del riesgo
```

**Cuatro de cada diez euros arriesgados se los lleva el bróker antes de que el
mercado haga nada.** Mira la celda que mejor sale: exceso +2,7 sobre el azar, y
aun así **neta −0,32**. Aunque la señal tuviera ventaja, a ese tamaño de stop no
llega.

Pasar de M5 a M15 casi dobla el stop (3,5 → 5,4 pips) y el coste baja del 41 %
al 26 %. La neta mejora de −0,62 a −0,38. **Sigue perdiendo, pero la dirección
es la misma de siempre**: cuanto más ancho el stop, menos pesa el coste.

> **La temporalidad del gatillo decide tu stop, y el stop decide tu coste.**
> Esto pasa antes de que la estrategia acierte o falle.

## La variante del nivel opuesto es una trampa de forma

Poner el objetivo en el nivel opuesto del día previo mientras el stop es una
vela de M5 da un **R:R de 17**. Acierta el 5,7 %. Es un décimo, no una
operación: cobras 17 veces el riesgo una vez de cada 18.

## Mi predicción falló otra vez

| predije | salió |
|---|---|
| exceso entre −2 y +2 en las 18 | dos celdas fuera (−2,6 y +2,7) |
| neta peor en M5 que en M15 | **correcto** |
| riesgo 5-10 pips, coste 15-30 % | **riesgo 3,5 p, coste 41 %** · me quedé corto |
| «nivel opuesto» el de mejor acierto (60-70 %) | **el peor: 5,7 %** |
| «si sale algo será en M15 con nivel opuesto» | esa es la peor celda de todas |

Tercera predicción seguida fallada. Las tres esperando algo distinto de lo que
manda el coste.
