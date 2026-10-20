# Resultado · filtrar su estrategia por la tendencia actual

Pre-registro: `docs/PREREGISTRO_tendencia_filtro.md`. Código:
`bt/tendencia_filtro.py`. EUR/USD, 1.281 operaciones, coste ECN.

---

## La tabla que lo dice todo

```
  filtro                         n   acierto      NETA  vs sin filtro
  ORÁCULO (futuro)             579     41,5%   +0,1515        +0,1723
  ─────────────────────────────────────────────────────────────────
  ROC 20 días                  625     36,5%   -0,0003        +0,0205
  EMA(20) diaria               637     36,3%   -0,0074        +0,0134
  semana anterior              627     35,9%   -0,0175        +0,0033
  SIN FILTRO                  1281     35,8%   -0,0208        +0,0000
  día anterior                 669     35,4%   -0,0334        -0,0126
  EMA(50) de H4                617     35,2%   -0,0368        -0,0160
  ROC 5 días                   672     34,7%   -0,0490        -0,0282
  EMA(50) diaria               624     34,6%   -0,0550        -0,0342
```

**La dirección vale muchísimo. Nadie puede medirla.**

## El oráculo: si supiera la dirección de la semana

```
                        n   acierto    bruta     NETA      z
    a favor           579     41,5%  +0,2556  +0,1515   +2,48
    en contra         702     31,2%  -0,0584  -0,1629   -3,11
    diferencia               +10,3pp  +0,3140  +0,3145
```

**+0,1515 de R neta con z +2,48.** Eso es una estrategia rentable de verdad:
41,5 % de acierto con R:R 2 contra un nulo del 33,3 %.

**Y es la primera vez que algo de este proyecto sale significativo en neto.**
Sólo que para conseguirlo hay que saber el viernes lo que va a pasar el viernes.

## Las siete medidas reales: cero

La mejor —ROC de 20 días— da **−0,0003**, que es exactamente nada, y mejora al
sin filtro en **0,0205**.

```
  lo que vale saber la dirección:            +0,1723
  lo que captura la mejor medida causal:     +0,0205
  ──────────────────────────────────────────────────
  se pierde el 88 % al cambiar futuro por pasado
```

Y **cuatro de las siete salen PEOR que no filtrar**. Poner un filtro de
tendencia al azar tiene más probabilidad de estropearlo que de ayudarlo.

## Un patrón dentro del ruido

Ordenando los filtros por velocidad:

```
  ROC 20 días        lento    -0,0003
  EMA(20) diaria     lento    -0,0074
  semana anterior    medio    -0,0175
  día anterior       rápido   -0,0334
  ROC 5 días         rápido   -0,0490
```

**Las medidas lentas rozan el cero; las rápidas restan.** Coincide con todo lo
demás del proyecto: la tendencia a plazo largo tiene algo (poquísimo), la
tendencia a plazo corto es ruido con nombre.

## Mis cuatro predicciones

| firmé | salió | |
|---|---|---|
| ningún filtro causal mejorará por más de 0,03 R | el mejor, +0,0205 | ✔ |
| el oráculo dará por encima de +0,15 | +0,1515 | ✔ |
| se perderá más del 80 % al cambiar futuro por pasado | **88 %** | ✔ |
| al menos dos de siete saldrán peor que no filtrar | **cuatro** | ✔ |

Las cuatro.

## Qué significa para su estrategia

**No añada ningún filtro de tendencia.** El mejor no mejora nada y cuatro de
siete empeoran. Siga tomando los dos lados.

Y lo que esta tabla enseña de verdad, que va más allá de su estrategia:

**La geometría de su operación está bien.** Con la dirección correcta da +0,15
de R neta y z +2,48 — sería rentable. Lo que falta no es el stop, ni el
objetivo, ni la hora, ni el nivel.

**Lo único que falta es saber hacia dónde va el precio.** Y eso es exactamente
lo que llevo tres meses sin poder medir en ningún sitio: ni en el CRT, ni en las
sesiones, ni en los indicadores, ni en el DXY, ni en 14.166 estrategias
generadas por fuerza bruta.

Esta tabla es la misma conclusión de siempre, pero por fin con los dos números
juntos: **lo que valdría saberlo, y lo que se consigue intentando saberlo.**
