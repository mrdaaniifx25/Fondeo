# Resultado · el mix de CRT y sesiones

Ejecutado el 29 de agosto de 2026 según `docs/PREREGISTRO_mixto.md`.
`bt/mixto.py`. Una sola pasada.

## El contraste principal no llega

```
LOS SIETE AGRUPADOS · H4 · 9.818 operaciones
  acierto 31,8 %  ·  R/op +0,0215  ·  bruta/día +0,0215  ·  z +1,53
```

La predicción firmada era positiva y sale positiva, pero **z +1,53 no cruza el
1,96**. El contraste falla.

## Pero el régimen por fin es el correcto

Por primera vez en todo el proyecto los stops escalan:

```
              stop mediano          c*        coste típico de mercado
  EURUSD        14,0 pips      0,19 pips           1,43 pips
  GBPUSD        17,2 pips     -0,81 pips           1,80 pips
  USDJPY        23,1 pips      1,31 pips           1,20 pips     cabe
  XAUUSD       679,7 cent     43,05 cent          25,00 cent     cabe
  DAX           34,0 pts       0,69 pts            1,50 pts
  NAS100        49,5 pts       0,93 pts            2,00 pts
  SP500         11,8 pts       0,04 pts            0,80 pts
```

En M5 el stop era de 5 pips y el coste se llevaba el 29 % del riesgo. Aquí son
14-50 unidades y el coste ronda el 3-8 %. **La aritmética por fin permite que
una ventaja pequeña sobreviva.**

En H1 el efecto desaparece: stops de 7-12 pips y c* de 0,13. Confirma que lo que
manda es la escala del stop, no la temporalidad por sí misma.

## El secundario declarado que sí sale

Londres, agrupando los siete, era uno de los cortes declarados de antemano:

```
  por sesión operada          n     %TP     R/op       z
    Asia                  7.490   32,0%   +0,004    +0,25
    Londres               2.010   31,7%   +0,087    +2,83
    NY                      318   27,4%   +0,020    +0,27
```

**No lo sostiene un solo instrumento.** Quitando cada uno por turno:

```
  quitando        n     %TP     R/op       z
  nada        2.010   31,7%   +0,087    +2,83
  GBPUSD      1.745   33,4%   +0,127    +3,81
  SP500       1.617   31,5%   +0,093    +2,71
  XAUUSD      1.875   31,6%   +0,084    +2,64
  DAX         1.721   32,1%   +0,087    +2,58
  USDJPY      1.796   31,6%   +0,081    +2,48
  EURUSD      1.729   31,6%   +0,076    +2,30
  NAS100      1.577   30,2%   +0,061    +1,76
```

Seis de siete siguen por encima de +2,3 al quitar cualquiera. Sólo cae por
debajo al quitar NAS100, y aun así se queda en +1,76 positivo.

Y partido por periodo:

```
  2020-2025      1.893 operaciones   31,7%   +0,085   z +2,67
  2026 ene-jul     117 operaciones   32,5%   +0,125   z +0,97
```

En 2026 va en la misma dirección y algo mejor, con cuatro de cinco instrumentos
en positivo. Son 117 operaciones, así que no demuestra nada por sí solo, pero no
contradice.

Prueba de signos sobre los siete instrumentos (todas las sesiones): **6 de 7 con
R media positiva, p = 0,062**.

## Qué se puede decir y qué no

**No se puede decir** que esto sea rentable. El contraste principal falla, el
corte de Londres es un secundario, y todo son datos ya vistos.

**Sí se puede decir**, y es la primera vez en el proyecto:

1. El efecto va en la misma dirección en 6 de 7 instrumentos.
2. Sobrevive a quitar cualquiera de ellos.
3. Va en la misma dirección en 2026, que no se había mirado aparte.
4. Y sobre todo: **el coste de equilibrio supera al coste típico de mercado en
   cinco de los siete**, cosa que no había pasado nunca.

## Lo que falta

Una prueba limpia. Ya se ha mirado todo el histórico disponible, así que la
única muestra virgen que queda es **el futuro**: fijar la especificación
—barrido de nivel de sesión en H4, sólo en la sesión de Londres, stop a un punto
de la mecha, objetivo 2R, una por día— y medirla hacia delante.
