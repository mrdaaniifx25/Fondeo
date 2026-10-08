# Corrección · entradas con el objetivo ya rebasado

**19/09/2026. Esta corrección tumba el resultado de AMD+FVG.** Lo que estaba
publicado como el mejor hallazgo del proyecto no bate al azar.

## Qué estaba mal

En `bt/amd_fvg.py`, la distancia del precio de entrada al objetivo se calculaba
con valor absoluto:

```python
rgo = abs(stop - P); rec = abs(obj - P)
```

El objetivo es el borde opuesto de la caja. Entre la finta y la vela que deja
el FVG pueden pasar hasta 5 velas de H1, y en ese tramo el precio a veces
**atraviesa entero el objetivo**. Cuando eso pasa, en el momento de entrar el
objetivo ya está detrás del precio. Con `abs()` la operación se daba por buena:
`rec` salía positivo, y al resolver, la primera vela siguiente ya cumplía
`l[k] <= obj`, así que se anotaba **ganada**.

Nadie pone esa operación. Si mandas una venta con el objetivo por encima del
precio al que entras, el bróker te la cierra en el acto. Esas filas no son
operaciones: son ruido que se cuenta como acierto.

## Cuánto pesaba

| | EURUSD | oro | DAX |
|---|---|---|---|
| operaciones publicadas | 587 | 383 | 361 |
| con el objetivo ya rebasado | **222 (38 %)** | 100 (26 %) | 112 (31 %) |
| acierto de esas | **97,3 %** | — | — |
| acierto de las de verdad | **63,8 %** | 63,3 % | 63,5 % |

El 76,5 % que te di era 63,8 % de operaciones reales mezclado con un 38 % de
filas que ganaban solas.

## Los números corregidos

EURUSD H1, n = 367. Las dos barreras por toque, coste 1,43 pips.

| | antes (mal) | ahora |
|---|---|---|
| operaciones | 587 | 367 |
| acierto | 76,5 % | **63,8 %** |
| su precio justo (azar) | 70,3 % | **64,2 %** |
| exceso sobre el azar | +6,2 | **−0,4** |
| R:R mediano | 0,4 | 0,6 |
| bruta | +0,1048 [+0,0412, +0,1684] | **+0,0247 [−0,0740, +0,1235]** |
| neta | +0,0390 | **−0,0567** |

Y en los otros dos instrumentos, exactamente lo mismo:

| | exceso antes | exceso ahora | bruta ahora |
|---|---|---|---|
| EURUSD | +6,2 | −0,4 | +0,025 [−0,074, +0,124] |
| oro | +3,7 | −0,6 | +0,000 [−0,102, +0,102] |
| DAX | +3,7 | −1,7 | −0,050 [−0,152, +0,052] |

El intervalo de confianza de los tres contiene el cero. **El exceso entero que
tenía AMD+FVG era esto.** También se cae lo de «13 de 13 años-instrumento en
positivo»: corregido, la mayoría de años están en negativo.

## Qué sigue en pie

- El acierto del 63,8 % sigue siendo cierto. Lo que ya no es cierto es que sea
  *bueno*: su precio justo por geometría es 64,2 %. Se acierta mucho porque el
  objetivo está cerca y el stop lejos, no porque la regla vea nada.
- El teorema de la barrera vuelve a salir intacto, y ahora también aquí.
- La comparación «con FVG mucho mejor que sin FVG» sigue en pie en la forma
  (−11,6 sin FVG frente a −0,4 con FVG) pero cambia de significado: el FVG no
  te hace ganar, te evita entrar con un stop pegado al precio.

## Lo que hay que hacer con esto

1. `pine/amd_fvg.pine` marca operaciones que no hay que tomar. Hasta arreglarlo
   y volver a medirlo, **no se usa**.
2. `docs/amd_fvg_ejemplos.html` está regenerado: 6 de los 24 ejemplos que se
   enseñaron eran de los rebasados, y los 6 «ganaban».
3. `docs/RESULTADOS_amd_fvg.md` lleva aviso arriba.

## Cómo se encontró

Midiendo otra cosa. Al montar `bt/m5_timing.py` para ver si M5 o M15 afinaban
la entrada, hubo que añadir la comprobación de que el objetivo estuviera por
delante — y al añadirla, la muestra base cayó de 587 a 367. De ahí salió el
resto.

Es el tercer error del mismo tipo en el proyecto: **un resultado bueno que era
un detalle de cómo se medía**. Los otros dos están en
`docs/CORRECCION_instante_entrada.md` y en las barreras asimétricas.
