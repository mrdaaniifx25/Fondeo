# Resultado · EUR/USD y DXY, exhaustivo

Pre-registro: `docs/PREREGISTRO_dxy.md`. Un solo pase.
Código: `bt/dxy_eurusd.py` y `bt/dxy_eurusd_addenda.py`.
DXY reconstruido con sus **pesos oficiales** desde las seis series diarias de la
Reserva Federal. **6.944 días, 1999-2026.** Rendimientos futuros **sin solape**.

---

## 1 · La respuesta estructural: no son dos variables, es una

```
  correlación diaria ΔEURUSD vs ΔDXY :  -0,9713
  R²                                 :   0,9434
  correlación de niveles (log)       :  -0,9742
```

**El 94,3 % de la varianza diaria del DXY es EUR/USD.** No es una coincidencia
de mercado: es la definición del índice, donde el euro pesa el 57,6 %.

Y la consecuencia práctica, que es el número que importa:

```
  días en que EURUSD y DXY se mueven en el MISMO sentido:  7,52 %
```

**El filtro «DXY a la baja Y EUR/USD al alza» coincide con «EUR/USD al alza» el
92,5 % de los días.** Sólo cambia algo en 7 de cada 100. Un filtro de confluencia
entre estos dos no añade información: reduce el número de señales y deja la
misma decisión.

## 2 · Cuánta información independiente hay realmente

La pendiente observada es **−0,81**, no el −0,576 del peso del euro. El motivo
es informativo:

```
  correlación ΔEURUSD vs Δcesta no-euro (yen, libra, CAD, SEK, CHF): +0,7664
  R² de la cesta no-euro contra EURUSD: 0,5874
```

**Cuando el euro sube contra el dólar, las otras cinco divisas también suben
contra el dólar.** La parte no-euro del DXY no diversifica: **amplifica**. Por eso
la pendiente es mayor que el peso.

Haciendo la cuenta:

```
  42,4 % de peso no-euro  ×  41 % no explicado por EURUSD  =  17,5 % del DXY
```

**Mirar el DXY junto al EUR/USD aporta, como máximo, un 17,5 % de información
nueva.** Y sobre ese 17,5 % se miden las seis pruebas siguientes.

## 3 · PRINCIPAL · el residuo no-euro prediciendo EUR/USD

```
  plazo      n   rend medio       t    placebo barajado
     1d   6849     -0,0008%   -0,12   -0,0004%
     5d   1378     +0,0214%   +0,61   -0,0019%
    20d    346     +0,2056%   +1,49   +0,0083%
```

**No significativo en los tres plazos.** Y la partición temporal:

```
  1999-2012: n 703  rend +0,0186%  t +0,33
  2013-2026: n 684  rend +0,0241%  t +0,58
```

Consistente entre mitades, sí, pero consistentemente diminuto.

## 4 · Adelanto y retraso: nada en once retardos

```
     k    corr(ΔE[t+k], ΔD[t])        t
    -5                  0,0225      1,9
    -2                  0,0109      0,9
     0                 -0,9713   -340,0
     1                 -0,0044     -0,4
     2                  0,0150      1,2
     5                  0,0269      2,2
```

Simultáneo: t **−340**. A cualquier retardo: |t| < 2,2. El único que pasa de 2 es
k=5 entre once probados, que es exactamente lo esperable.

**El DXY no adelanta al EUR/USD ni el EUR/USD al DXY. Se mueven a la vez porque
son lo mismo.**

## 5 · Momento de la cesta no-euro: ocho celdas, nada

```
  momento  plazo      n   rend medio       t
       1d     5d   1380     +0,0118%   +0,34
       5d    20d    346     +0,1551%   +1,22
      20d     5d   1376     +0,0224%   +0,63
      60d    20d    344     +0,0343%   +0,25
```

Máximo |t| de las ocho: **1,22**.

## 6 · Divergencia SMT: apunta al lado contrario

```
  caso                                      n   rend 5d con signo    t
  euro rompe arriba, DXY NO abajo (div)   117           -0,1184%  -0,97
  euro rompe arriba, DXY SÍ abajo (conf)  735           +0,0494%  +1,07
  euro rompe abajo, DXY NO arriba (div)   119           -0,0977%  -0,88
  euro rompe abajo, DXY SÍ arriba (conf)  701           -0,0087%  -0,18
  TODOS los días (control)               6939           -0,0001%  -0,00
```

El signo de cada fila es **el que la teoría SMT predice**. Los dos casos de
divergencia salen **negativos**: la señal apunta al lado equivocado, aunque no
significativamente. Coincide con `RESULTADOS_smt.md`, que midió lo mismo en
intradía y dio +3,3 puntos con t 1,06.

## 7 · Reversión del diferencial: no es monótona

```
  z del residuo acumulado      n   rend 5d de EURUSD       t
             z < -1,5        213            +0,0928%   +1,06
          -1,5 a -0,5        292            +0,1305%   +1,81
          -0,5 a +0,5        300            -0,1128%   -1,49
          +0,5 a +1,5        340            -0,0286%   -0,42
             z > +1,5        233            +0,0761%   +0,80
```

Si el diferencial revirtiera, esto tendría que bajar de arriba abajo de forma
monótona. Sale +0,09 / +0,13 / −0,11 / −0,03 / +0,08. **Es ruido con forma.**

## 8 · Lo único con forma de señal, y es diminuto

Los días raros en que **los dos se mueven en el mismo sentido** (7,52 % del
total):

```
  caso                        n   rend EURUSD 5d       t
  los dos al alza            53         +0,2467%   +1,41
  los dos a la baja          52         -0,2354%   -1,68
  normal (euro ↑, DXY ↓)    626         +0,0158%   +0,29
  TODOS (control)          1388         -0,0008%   -0,02
```

Simétrico, consistente, y **de continuación, no de reversión** — justo al
contrario de lo que predice la divergencia SMT. Pero son **52 y 53
observaciones** y t de 1,4 y 1,7.

Y la referencia que lo coloca: he medido unas **36 celdas** en este documento.

```
  mejor |t| de las 36:                          1,81
  E[máximo de 36 celdas de puro ruido] (|t|):   2,39
```

**La mejor celda de las treinta y seis queda por debajo de lo que produce el
azar eligiendo la mejor de treinta y seis.** La rejilla entera es compatible con
cero.

## 9 · Aquí el coste no es la excusa, y conviene subrayarlo

```
  muro de coste en EURUSD diario: 0,0226 en unidades de ruido diario
  desviación diaria de EURUSD: 0,574 %
  -> el coste equivale a 0,0130 % por operación
```

El efecto del residuo a 20 días es **+0,2056 %**: quince veces el coste. **Si
fuera real, se cobraría de sobra.** Es la primera prueba del proyecto donde el
coste es irrelevante y la respuesta sigue siendo cero.

Eso es un dato: el problema de esta idea no es la horquilla, es que no hay señal.

## 10 · Mis seis predicciones firmadas

| firmé | salió | |
|---|---|---|
| correlación entre −0,93 y −0,99; R² > 0,88 | −0,9713; R² 0,9434 | ✔ |
| **PRINCIPAL: t entre −2 y +2** | **+0,61** | ✔ |
| todos los retardos \|t\| < 2 | máximo 2,2 en 1 de 11 | ✔ (al borde) |
| la cesta no-euro no predice, \|t\| < 2 | máximo 1,22 de 8 | ✔ |
| la divergencia no supera su control | apunta al revés | ✔ |
| el diferencial no revierte lo que cuesta | no monótono | ✔ |

Las seis. Después de fallar tres en `RESULTADOS_timing_crt.md`, aquí el modelo
del mundo aguantó entero.

## Veredicto

**La confluencia EUR/USD–DXY no es una idea que falle: es una idea que no
existe.** Con r = −0,971 no son dos instrumentos, son uno con el signo cambiado.
El filtro coincide con mirar sólo EUR/USD el 92,5 % de los días, y la
información genuinamente nueva es el 17,5 % del índice.

Sobre ese 17,5 % se han medido 36 celdas —residuo a tres plazos, momento de la
cesta a cuatro plazos por dos horizontes, divergencia en cuatro casos, reversión
en cinco tramos, once retardos— y la mejor sale a |t| 1,81 cuando la selección
sola da 2,39.

**Casilla 3 cerrada.** Y cerrada en el sitio bueno: en diario, donde el coste es
quince veces menor que el efecto que habría que encontrar.
