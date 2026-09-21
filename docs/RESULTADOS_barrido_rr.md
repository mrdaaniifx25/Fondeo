# Resultados · barrer el R:R, el término que multiplica

Código `bt/barrido_rr.py`. EURUSD, oro y DAX juntos. Nace de la fórmula que
salió de las etiquetas de las operaciones de Benjamín
(`docs/VERIFICACION_benjamin_real.md`):

```
neta = ventaja × (1 + R:R) − coste/riesgo
```

El proyecto lleva dos meses bajando el término que **resta** (stops anchos) y no
había barrido nunca el que **multiplica**.

## CRT en H4 · 4.280 operaciones

| R:R | acierto | azar | **exceso** | ventaja×(1+R:R) | **NETA** |
|---|---|---|---|---|---|
| 0,5 | 67,9 % | 66,7 % | +1,2 [−0,2, +2,6] | +0,018 | −0,097 |
| **1,0** | 53,1 % | 50,0 % | **+3,1 [+1,6, +4,6]** | +0,061 | −0,054 |
| **1,5** | 43,3 % | 40,0 % | **+3,3 [+1,8, +4,8]** | +0,083 | −0,032 |
| **2,0** | 36,8 % | 33,3 % | **+3,5 [+2,0, +4,9]** | **+0,105** | **−0,010 [−0,054, +0,033]** |
| **3,0** | 27,4 % | 25,0 % | **+2,4 [+1,0, +3,7]** | +0,094 | −0,021 |
| **4,0** | 21,6 % | 20,0 % | **+1,6 [+0,4, +2,8]** | +0,081 | −0,034 |
| 6,0 | 15,0 % | 14,3 % | +0,8 [−0,3, +1,8] | +0,053 | −0,062 |
| 8,0 | 10,6 % | 11,1 % | −0,5 [−1,4, +0,4] | −0,043 | −0,158 |

**Cinco valores de R:R consecutivos con el IC95 del exceso entero por encima de
cero**, formando una **curva suave con máximo en R:R 2,0**. Eso no es la firma
del ruido: el ruido da picos aislados con vecinos malos, que es lo que se ha
descartado cinco veces esta semana.

## El desglose del pico

```
ventaja bruta        +0,105 R
coste medio          −0,115 R
                     ─────────
neta                 −0,010 R
```

Y el dato que abre la siguiente prueba: **el coste mediano es 7,4 % pero el
medio es 11,5 %.** Esa diferencia son las operaciones con el stop diminuto,
cuya `1/riesgo` arrastra la media. Quitarlas baja el término que resta sin
tocar la señal.

## Dos correcciones a lo que se venía diciendo

**1 · H4, no H12.** Se llevaba tres días empujando hacia marcos grandes. H12
(n=1.061) y D1 (n=732) salen **peor**: exceso en cero o negativo, y en D1 se
hunde a −7,8 con R:R alto. El sitio con señal es **H4**.

**2 · El R:R tiene un óptimo, no crece.** Recién descubierto que multiplica, la
tentación era subirlo. A R:R 8 el exceso es **negativo** en los tres marcos. El
máximo está en 2,0.

## Lo que no se reclama

Son 8 R:R × 3 marcos = 24 celdas y se está señalando una fila. Lo que la
sostiene es la **forma de la curva**, no el número suelto — pero eso no es una
demostración.

La prueba limpia que sale de aquí, y que se preregistra aparte: **filtrar por
stop mínimo** para bajar el coste medio. Una sola decisión, declarada antes, con
un criterio único. Si cruza el cero, hay algo que medir en serio; si no, el
proyecto tiene su respuesta y es limpia.
