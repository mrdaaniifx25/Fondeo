# Pre-registro · doble barrido anidado + envolvente de entrada

**Escrito el 2026-09-15, antes de medir nada.** Idea suya, con sus palabras:

> «el tema del liquidity sweep, con vela envolvente en M15 o M5, tipo mirar que
> exista un liquidity sweep en 12h y en 4h, en 4H y 2H, en 8h y 4H o así»

## Qué hay ya medido que toca esto, y que no lo cierra

**La cascada** (`RESULTADOS_crt_cascada.md`) midió D1/H4/H1 alineadas hacia el
objetivo semanal. El cubo de «2 alineadas» dio +0,5230 con z +2,65 y neta
+0,2565 — la única celda positiva —, pero los cubos de 0, 1 y 3 salieron
negativos o planos. Que destaque el 2 y no el 3 es la firma del ruido, no la de
una señal, y así se reportó.

**La envolvente** (`RESULTADOS_crt_que_diferencia.md`) se midió como una de 30
características sobre 19.553 CRT en H4, y fue **la peor de las treinta**:
−0,0542 de diferencia entre quintiles, con el quintil que la tiene rindiendo
peor que el que no.

Ninguna de las dos cierra esto: él propone pares **anidados** concretos y la
envolvente como **disparador de entrada** en M15/M5, no como característica del
setup. Es una combinación que no está probada.

## La especificación, cerrada antes de mirar

**Barrido de liquidez en una temporalidad** — la definición canónica que usa todo
el repositorio, sin cambios: la vela en curso se lleva un extremo de la vela
anterior ya cerrada y cierra de vuelta dentro de su rango. Un solo lado; si se
lleva los dos, se descarta.

**Doble barrido anidado** — las dos temporalidades del par tienen barrido activo
**del mismo lado** en el momento de evaluar. Pares:

```
12h + 4h      ·      8h + 4h      ·      4h + 2h
```

**Disparador** — la primera vela de M15 (o M5) que sea **envolvente** a favor del
giro: su cuerpo contiene por completo el cuerpo de la vela anterior y va en
dirección contraria al barrido (barrido del máximo → envolvente bajista).

**Entrada** al cierre de esa envolvente. **Dirección** contraria al barrido.

**Stop**: el extremo de la envolvente. **Objetivo**: 1:2.

**Ventana de validez**: la envolvente tiene que aparecer dentro de la vela de la
temporalidad menor del par en la que se detecta el doble barrido. Si no aparece,
no hay operación.

**Coste**: el medido por instrumento — EURUSD 1,43 · GBPUSD 1,60 · USDJPY 1,50 ·
NAS100 1,50 · SPX500 0,60 pips.

**Datos**: cinco instrumentos, 2020 a julio de 2026. Sin datos nuevos: la web de
HistData no le funciona y para esto no hacen falta.

## Celda principal, declarada ahora

```
par 12h + 4h   ·   envolvente en M15   ·   stop en la envolvente   ·   objetivo 1:2
```

Se elige el par de 12h+4h porque da los stops más anchos de los tres, y el ancho
del stop es lo único que este proyecto ha demostrado que decide algo. No se elige
por resultado: no se ha mirado ninguno.

Las otras 5 celdas (3 pares × 2 temporalidades de entrada) se reportan enteras.

## Qué cuenta como éxito

**R NETA positiva en la celda principal, con el intervalo del 95 % excluyendo el
cero por arriba**, usando error estándar agrupado por instrumento-día.

Son 6 celdas. Para cualquier celda que no sea la principal hace falta
**|z| > 2,64** (Bonferroni para 6). La principal se juzga por su intervalo.

## Qué cuenta como fracaso

Que el intervalo de la principal incluya el cero. En ese caso la idea se cierra
y no se renegocia el criterio.

## Lo que se predice, y por qué

Se escribe la predicción para que quede el contraste:

1. **La bruta será positiva pero pequeña**, del orden de +0,05 a +0,15 R. Es el
   mismo patrón de barrido que ya está medido en +0,082 y replicado a ciegas.
2. **El coste se llevará más del 20 % del riesgo**, porque una envolvente de M15
   deja un stop estrecho. Con eso la neta sería negativa.
3. **La neta será negativa en las 6 celdas.**

Si sale al revés, es un hallazgo de verdad. Si sale como se predice, al menos el
«no» estará hecho con el criterio escrito de antemano y no será otra vez una
impresión.

## Potencia

Se calcula **antes**, que es el error que ya se cometió una vez en este
repositorio. Se estimará el número de disparos en la primera pasada y se
reportará qué efecto mínimo puede detectar esa n. Si el efecto detectable es
mayor que el esperado (+0,05), se dirá explícitamente que la prueba sólo puede
falsar, no confirmar.
