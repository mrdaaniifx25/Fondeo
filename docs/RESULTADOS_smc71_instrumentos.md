# SMC-71 · en qué instrumentos está testeada y dónde funciona

Configuración: `TF={15,30,60} FVG=no H4=sí ENTR=0.71`, entrada al 71 %,
stop al 100 %, TP al 0 %  ->  R:R 2,45, azar geométrico 29,0 %.
Reproducible con `TF=30 FVG=no SUF=_tf30 python3 bt/smc_71.py`.

Siete instrumentos: EURUSD, GBPUSD, USDJPY, XAUUSD, GRXEUR (GER40),
NSXUSD (US100), SPXUSD (US500).

## M30, por instrumento

      instr      n   acierto   R bruta       z    R NETA     stop  coste/R
    ----------------------------------------------------------------------
     EURUSD    254     38.2 %    +0.317   +3.01    +0.093     7.2    19.8 %
     GBPUSD    227     33.5 %    +0.154   +1.43    -0.036     9.4    17.0 %
     USDJPY    271     31.7 %    +0.081   +0.84    -0.106    10.1    14.8 %
     XAUUSD    115     27.0 %    -0.070   -0.49    -0.134   384.5     5.2 %
     GRXEUR     72     34.7 %    +0.197   +1.01    +0.123    26.0     5.8 %
     NSXUSD    232     33.2 %    +0.144   +1.35    +0.083    29.7     5.1 %
     SPXUSD    234     30.8 %    +0.061   +0.59    -0.030     6.9     7.3 %

La R bruta es positiva en 6 de 7, en M15, M30 y M60. No es un instrumento
concreto: el mecanismo aparece en casi todos. El único fallo es el ORO, y
falla en BRUTO con un coste de solo el 5,2 % de la R -> no es un problema de
comisiones, ahí la señal no está.

Lo que decide quién sobrevive neto no es el par, es el coste/R.

## Agrupando operaciones (no promediando instrumentos)

          agrupando las 7        sin el oro
           n    bruta      z      n    bruta      z   ·   NETA      z
    -----------------------------------------------------------------
     M15  2536  +0.150  +4.66   2331  +0.166  +4.90   ·  -0.053  -1.58
     M30  1405  +0.136  +3.15   1290  +0.155  +3.42   ·  +0.006  +0.13
     M60   753  +0.112  +1.90    694  +0.156  +2.53   ·  +0.065  +1.06

El edge BRUTO está demostrado (z +4.90 en M15, +3.42 en M30 sin oro).

El edge NETO NO está demostrado en ninguna temporalidad. M30 neta es cero
exacto (z +0.13) y M60 es +0.065 con z +1.06, que no es prueba de nada.
La formulación correcta no es "el neto se vuelve positivo en M30/M60" sino
"el neto pasa de claramente negativo a indistinguible de cero".

Quitar el oro es una decisión a posteriori. Mejora los números pero no
cuenta como validación.

## Por año, M30 sin oro

       2020  n=173  acierto 28.3 %  bruta -0.023  neta -0.184
       2021  n=207          32.9 %        +0.133        -0.067
       2022  n=191          28.3 %        -0.025        -0.131
       2023  n=183          34.4 %        +0.168        +0.022
       2024  n=225          39.6 %        +0.364        +0.210
       2025  n=194          32.0 %        +0.102        -0.022
       2026  n=117          41.0 %        +0.415        +0.266

Dos de siete años son negativos en BRUTO. El resultado global se apoya en
2024 y 2026. Operado en 2020 o 2022 habría perdido el año entero. No es una
ventaja estable mes a mes; es pequeña y aparece de forma desigual.

## Lo que falta

El coste de los índices es una ESTIMACIÓN mía (1.50 pts para US100 y GER40,
0.50 para US500). Los tres únicos instrumentos con R neta positiva en M30
son precisamente los de coste estimado. Hasta tener el spread y la comisión
reales de la cuenta, esos +0.123 / +0.083 no están confirmados.
