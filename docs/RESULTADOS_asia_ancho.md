# Resultado · el filtro de contexto con stops anchos

Ejecutado el 28 de agosto de 2026 según `docs/PREREGISTRO_asia_ancho.md`.
`bt/asia_ancho.py`. Y con una corrección de método que cambia la lectura.

## La predicción firmada pasa

```
2020-2025 · M15 y H1 a favor · horizonte hasta las 22:00
  stop mín        n    días   stop     %TP  sin resolver    R/op   z br   neta/d      z
  natural     1.454   1.219   7,7p   34,9%        1,6%    +0,071  +3,52   -0,104  -2,58
  10 p        1.454   1.219  10,0p   34,5%        2,9%    +0,074  +3,69   +0,017  +0,42
  15 p        1.454   1.219  15,0p   32,4%        8,3%    +0,090  +4,46   +0,081  +2,08
  20 p        1.454   1.219  20,0p   27,0%       19,1%    +0,078  +4,13   +0,081  +2,20
  25 p        1.454   1.219  25,0p   20,4%       31,6%    +0,059  +3,64   +0,066  +1,96
  30 p        1.454   1.219  30,0p   14,2%       43,0%    +0,026  +2,52   +0,030  +0,97
```

El contraste firmado era el de 20 pips y la predicción era «positiva». Sale
**+0,081 con z +2,20**. La secundaria también se cumple: el bruto se mantiene
cerca de +0,08 al ensanchar. En enero-mayo de 2026: +0,216 a 20 pips.

Con horizonte de 3 días la caída del acierto en stops anchos desaparece
(34,4 % a 20 pips en vez de 27,0 %), lo que confirma que era truncamiento por
cerrar a las 22:00, no pérdida de ventaja.

## Y aun así no vale, porque la métrica no era dinero

**`neta/día` en todo el proyecto es la MEDIA de las operaciones de ese día.**
Eso pesa igual un día de una operación que un día de tres. Lo que se cobra es la
SUMA. Y ahí:

```
  operaciones ese día     días    ops     %TP   neta/op   neta del día
  1                        995    995   31,3%    +0,182         +0,182
  2                        213    426   17,6%    -0,363         -0,725
  3 o más                   11     33   18,2%    -0,472         -1,417
```

Los días de varias operaciones son un desastre: la segunda existe porque la
primera falló. Con la media diaria salen +0,081; con la suma, **+0,009**.

En euros, a 150 € de riesgo: **+22 al mes**.

Tomando sólo la primera del día, que es lo natural:

```
  variante                 n    días     %TP     R/op   z br   neta/d      z   €/mes
  natural · mismo día  1.219   1.219   35,4%   +0,081  +1,97   -0,170  -4,06    -433
  15p · mismo día      1.219   1.219   32,9%   +0,101  +2,54   +0,009  +0,22     +22
  20p · mismo día      1.219   1.219   27,2%   +0,084  +2,21   +0,013  +0,34     +32
  15p · 3 días         1.219   1.219   35,9%   +0,086  +2,08   -0,007  -0,17     -18
  20p · 3 días         1.219   1.219   34,3%   +0,050  +1,22   -0,021  -0,52     -53
```

## El filtro de contexto sí aguanta la métrica correcta

Rehecho con sumas diarias en vez de medias:

```
2020-2025                    n    días  ops/día    %TP     R/op  suma/día       z
  M15 y H1 a favor       1.454   1.219     1,19  34,9%   +0,071    -0,208   -4,50
  el resto                 626     538     1,16  21,2%   -0,355    -1,124  -14,06
  DIFERENCIA                                                       +0,916   +9,92
```

El hallazgo del contexto se mantiene entero: z +9,92 con la métrica buena. En
bruto, el grupo a favor da +0,085 de suma diaria (z +1,91) y el resto −0,413
(z −7,24). **El filtro es real.**

## Lo que queda, dicho sin adornos

1. **El contexto de M15 y H1 es el hallazgo firme del proyecto.** Sobrevive al
   preregistro, a las dos muestras y a la corrección de métrica.
2. **La ventaja bruta que deja es de +0,08 a +0,10 R por operación.** Real,
   medida, pequeña.
3. **El coste de 1,43 pips se la come casi entera.** Lo que sobra son 20-30 € al
   mes con 150 € de riesgo. No es un negocio.
4. **Ensanchar el stop funciona en la dirección esperada** pero sólo lleva el
   resultado de claramente negativo a aproximadamente cero.

Para que esto fuese rentable haría falta una de dos: que el coste bajase a la
mitad, o que la ventaja bruta fuese el doble. La primera no depende de él. La
segunda es lo que habría que buscar, y ya no en este espacio de parámetros.

## Corrección de método, para todo lo anterior

`neta/día` como media diaria era una elección defendible para **detectar** si
existe señal, porque no deja que un día de muchas operaciones domine. No sirve
para estimar **cuánto se gana**. En los resultados negativos anteriores no
cambia nada (negativo sigue siendo negativo) y en agosto los euros siempre se
calcularon como suma, así que están bien. Pero de aquí en adelante los dos
números van juntos.
