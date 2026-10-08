# Horarios de reversión y continuación del EURUSD

Aportación del usuario, en hora de España:

```
reversión      09:00 – 15:00
continuación   12:00 – 17:00       (se solapan de 12 a 15)
```

Es una hipótesis buena porque es **condicional**: dice que el mismo patrón se
comporta distinto según la hora. Si fuera cierta explicaría por qué la prueba
fundacional (`RESULTADOS_cierres.md`) salió plana — estaría mezclando dos
regímenes opuestos y anulándose entre sí.

## Cómo se mide

Se toma la clasificación fundacional —barre y **cierra dentro** → debería
girarse; barre y **cierra fuera** con cuerpo → debería continuar— y se parte por
banda horaria. Lo que exige el marco es que **dentro de cada banda las dos
celdas se separen**. EURUSD, 2020-2026.

## Resultado

Diferencia entre las dos celdas dentro de cada banda:

| banda (hora de España) | H1 | M15 |
|---|---|---|
| madrugada 00-09 | z +0,06 | z +2,53 |
| **solo reversión 09-12** | **z −0,13** | **z +2,42** |
| **solapan 12-15** | **z −0,50** | **z +1,43** |
| **solo continuación 15-17** | **z −1,46** | **z +1,57** |
| tarde 17-24 | **z +4,94** | **z +4,36** |

**En las tres bandas que ellos declaran, las celdas no se separan.** En H1 la
diferencia va incluso con el signo contrario al que pide el marco. En M15 los z
rondan 1,4-2,4, por debajo del umbral que corresponde: se han probado diez
bandas por dos temporalidades, así que hace falta |z| > 3,0.

## Lo que sí aparece, y no es lo que dicen

La única banda donde las dos celdas se separan con claridad, y en las **dos**
temporalidades, es **17:00 a 24:00** — que no es ninguna de las suyas.

Y conviene mirar de qué está hecha esa separación:

```
17-24 en H1     reversión   +0,0131      continuación  −0,0372
17-24 en M15    reversión   −0,0087      continuación  −0,0347
```

La separación **no viene de que la reversión funcione**: viene de que la
continuación falla más fuerte. Por la tarde-noche, después de que el precio se
lleve un extremo y cierre con cuerpo por fuera, lo que sigue es lo contrario de
lo que predice el marco.

Es el mismo hecho que ya había salido por otros dos caminos —el cribado de 54
variables y la prueba fundacional—: **al horizonte corto hay reversión, no
continuación**. Aquí aparece por tercera vez, ahora concentrada en las horas de
menos liquidez, que es justo donde uno esperaría encontrarla.

## Salvedad

Ese +4,94 es un hallazgo **por inspección**, no una hipótesis previa: he mirado
diez bandas y he señalado la que destaca. Sobrevive a la corrección por
contrastes múltiples, pero no es lo mismo que haberlo predicho. Y el tamaño
—0,05 unidades de ATR, unas 0,3 pips— sigue muy por debajo del coste.

## Conclusión

La hipótesis de los horarios **no se sostiene tal como está formulada**. No
rescata la premisa fundacional: dentro de las ventanas que señalan, las dos
celdas siguen sin separarse.

## Reproducir

`bt/horarios_eurusd.py`
