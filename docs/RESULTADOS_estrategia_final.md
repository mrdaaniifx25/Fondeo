# Resultado · la estrategia ensamblada

Pre-registro: `docs/PREREGISTRO_estrategia_final.md`. Un solo pase.
Código: `bt/estrategia_final.py` y `bt/estrategia_final_diagnostico.py`.
25 series diarias, 1971-2026, 660 meses.

---

## La estrategia, especificada entera

Es lo que hay que hacer, sin ambigüedad. **Una vez al mes**, el primer día hábil:

**Universo operable (14):** EUR, GBP, JPY, CHF, CAD, AUD, NZD, SEK, NOK, DKK
(todas contra el dólar), WTI, Brent, gas natural, S&P 500.

**Para cada instrumento, tres bloques, a peso igual:**

- **A · momento** — signo del rendimiento a 21, 63, 126 y 252 días. Se promedian
  los cuatro signos. Va de −1 a +1.
- **B · tendencia** — signo de (MM20 − MM100), Donchian 55 (largo si rompió el
  máximo de 55 días, corto si el mínimo), y canal ATR (largo sobre EMA20+2·ATR20,
  corto bajo EMA20−2·ATR20). Se promedian los tres.
- **C · carry** — sólo divisas: diferencial de inflación frente a EE.UU. Largo el
  tercio con más inflación, corto el tercio con menos.

**Posición = media de los tres bloques.** Tamaño inverso a la volatilidad de
36 días. Se fija el día 1 y **no se toca hasta el mes siguiente.**

Rotación real: **9,1 cambios por instrumento y año.** Unas 130 operaciones al
año en total. Nada de pantallas.

---

## El resultado, con el tramo que decide primero

```
                                 meses   efecto      t  Sharpe   +meses    caída   peor12
  2013-2026  <-- EL NUMERO         165  -0,0219  -0,18   -0,05      48%   -21,99   -11,09
  muestra completa                 660  +0,3464  +4,74   +0,64      56%   -21,99   -11,09
    1971-1999                      339  +0,5990  +5,17   +0,97      62%    -8,32    -5,53
    2000-2012                      156  +0,1872  +1,62   +0,45      53%   -11,60    -9,56
    2013-2026                      165  -0,0219  -0,18   -0,05      48%   -21,99   -11,09
    2020-2026                       81  -0,1177  -0,62   -0,24      47%   -20,05   -11,09
```

Sobre 55 años: **Sharpe +0,64, t +4,74.** Un sistema de verdad.

Sobre los trece últimos, en lo que él puede operar: **Sharpe −0,05.** Cero.

## No está roto: coge los años buenos. No bastan.

```
  2014  +12,31     2018   -3,65     2022   +6,54
  2015   +4,28     2019   -5,85     2023   -3,67
  2016   +1,69     2020   +5,47     2024   -5,72
  2017   -2,13     2021   -3,18     2025   -1,44
                                    2026   -7,55
```

**2022 sale +6,54** — el año del dólar y la energía, el año que todos los
seguidores de tendencia presumen. El sistema lo ve. También ve 2014 (+12,3) y
2020 (+5,5).

Lo que pasa es que entremedias hay ocho años perdiendo. Así es como funciona
esto: pocas rachas grandes, muchos meses pequeños en contra. Durante 1971-1999
las rachas grandes compensaban. Desde 2013 ya no.

Y 2026 va **−7,55**, el peor del tramo.

## Los tres bloques: dos son el mismo

```
                              meses   efecto      t  Sharpe
  A momento · completa          657  +0,5163  +5,01   +0,68
    A momento · 2013-2026       165  -0,0700  -0,43   -0,12
  B tendencia · completa        660  +0,4757  +4,38   +0,59
    B tendencia · 2013-2026     165  -0,0632  -0,33   -0,09
  C carry · completa            660  +0,0690  +1,14   +0,15
    C carry · 2013-2026         165  +0,0632  +0,70   +0,19
```

Correlación entre los rendimientos mensuales:

```
                 A momento   B tendencia   C carry
  A momento           1,00          0,87      0,10
  B tendencia         0,87          1,00      0,10
  C carry             0,10          0,10      1,00
```

**A y B están al 0,87: son la misma apuesta.** Momento con ROC y tendencia con
medias/Donchian/ATR miden lo mismo. Sumarlos no diversifica nada.

**Carry está al 0,10: ése sí es distinto.** Y es **el único bloque que sigue en
positivo en 2013-2026** (Sharpe +0,19). No es significativo —t +0,70, haría
falta mucho más tiempo— pero es el único que no se ha ido a cero, y tiene
sentido: es lo único que no mira el precio.

## Y no se arregla con más mercados

La duda razonable era ésta: las gestoras de tendencia operan 100-200 mercados y
yo tengo 14. ¿Es un problema de tamaño del universo? Sorteando carteras
aleatorias de distinto tamaño:

```
  instrumentos    Sharpe 2013-2026      Sharpe 1971-2026
        5              +0,14                 +0,39
       10              +0,27                 +0,89
       14              +0,26                 +0,95
       20              +0,28                 +1,04
       25              +0,28                 +1,08
```

**La diversificación satura a los diez.** De 14 a 25 no gana nada. Y tiene el
mismo motivo que todo lo anterior: como todas las señales de tendencia son una
sola apuesta, añadir mercados no añade apuestas independientes, sólo repite la
misma con más nombres.

Así que no: con 100 mercados tampoco. Ése no es el cuello de botella.

## Los controles

```
  comprar y mantener             660  +0,0828  +0,55   +0,07   caída -106,01
  placebo (azar, misma rotación) 660  -0,0516  -0,68   -0,09   caída  -73,47
```

El sistema bate a los dos en muestra completa, con la décima parte de la caída
de comprar y mantener. Eso confirma que en 55 años es real. No cambia el tramo
reciente.

## En dinero

Escalado para que la mayor caída histórica sea exactamente el 10 %, su límite:

```
  muestra completa   Sharpe +0,64   vol 2,96 %/año   +1,89 %/año
                     10k: +16 €/mes   50k: +79 €/mes   100k: +158 €/mes
  2013-2026          Sharpe -0,05   vol 2,51 %/año   -0,12 %/año
                     10k:  -1 €/mes   50k:  -5 €/mes   100k:  -10 €/mes
```

Ni siquiera al ritmo de 55 años da los 300 €. Al ritmo de los trece últimos,
pierde.

## Las cinco predicciones firmadas

| firmé | salió | |
|---|---|---|
| completa operable: Sharpe +0,5 a +0,8, t > +4 | +0,64, t +4,74 | ✔ |
| **2013-2026: Sharpe −0,1 a +0,3, t < +1,5** | **−0,05, t −0,18** | ✔ |
| carry el único que aguanta en el tramo reciente | A −0,12 · B −0,09 · **C +0,19** | ✔ |
| A y B correlados por encima de 0,7 | 0,87 | ✔ |
| menos de 100 €/mes sobre 10.000 € | −1 €/mes | ✔ |

Las cinco. Después de fallar dos en `RESULTADOS_indicadores.md` y una en
`RESULTADOS_crt_cascada_video.md`, aquí el modelo del mundo aguantó entero. Lo
apunto porque cuando falla lo apunto igual.

## Veredicto

Esto es lo mejor que se puede ensamblar con todo lo medido en tres meses. Está
construido sin elegir nada: pesos iguales, parámetros de libro, un solo pase.

**Sobre 55 años es un sistema real.** Sharpe +0,64, bate a comprar y mantener
con una décima parte de la caída, y los controles lo respaldan.

**Sobre los trece últimos, en mercados que él pueda operar, no existe.**

No lo publico como página para operar, y ésa es la decisión importante de este
documento: presentar con buen diseño un sistema que mide Sharpe −0,05 sería
exactamente lo que hacen los vídeos que llevamos dos semanas desmontando.
