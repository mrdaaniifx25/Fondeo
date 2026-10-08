# Resultados · el pase limpio de la estrategia del 71 %

Preregistrado en `docs/PREREGISTRO_smc71.md`, sellado en el commit `fb27470`
antes de correr nada. Un solo pase.

## Las tres pasan

| | n | acierto | z acierto | R bruta | z | R neta | pos |
|---|---|---|---|---|---|---|---|
| *exploratorio (ya conocido)* | 1.111 | 32,6 % | +2,63 | +0,124 | +2,55 | −0,066 | 6/7 |
| **0 · relleno pesimista** | 1.111 | 32,6 % | +2,63 | **+0,124** | **+2,55** | −0,066 | 6/7 |
| **1 · rango H4 de 10 velas** | 1.164 | 32,8 % | +2,87 | **+0,130** | **+2,75** | −0,060 | 6/7 |
| **1 · rango H4 de 40 velas** | 1.109 | 31,9 % | +2,14 | **+0,099** | **+2,06** | −0,086 | 5/7 |
| **2 · ejecución en M5** | 3.197 | 32,5 % | +4,32 | **+0,120** | **+4,19** | −0,238 | 6/7 |
| **2 · ejecución en M30** | 568 | 32,7 % | +1,97 | **+0,129** | **+1,90** | **+0,005** | 4/7 |

```
  0 · relleno pesimista .......... +0,124 · z +2,55        PASA
  1 · parámetros ................. 4 de 4 positivas        PASA
  2 · temporalidades ............. las dos positivas       PASA
```

### Sobre la prueba 0

Cambió **cero operaciones**. No es que el flag no se aplicara —está verificado en
`bt/smc_71.py:126` y comprobado ejecutando las dos versiones—: es geometría. El
stop queda al 29 % de la pierna por encima de la entrada, y una sola vela de M15
casi nunca abarca eso. Mi supuesto optimista era inofensivo por casualidad.

### Sobre la prueba 1

`VIDA` resultó no ser un parámetro que ate: 48 y 192 horas dan resultados
idénticos porque las operaciones se resuelven mucho antes. La rejilla probó de
verdad dos valores de `H4V`, y los dos salen positivos.

## Y el hallazgo que no buscaba: la escalera de temporalidades

| TF | n | acierto | R bruta | z | **R NETA** | stop | coste/R | neta positiva |
|---|---|---|---|---|---|---|---|---|
| M5 | 3.197 | 32,5 % | +0,120 | +4,19 | −0,238 | 4,6 | 27,8 % | 0/7 |
| M15 | 1.111 | 32,6 % | +0,124 | +2,55 | −0,066 | 8,8 | 14,2 % | 4/7 |
| M30 | 568 | 32,7 % | +0,129 | +1,90 | **+0,005** | 12,6 | 9,4 % | 4/7 |
| **M60** | 246 | **34,6 %** | **+0,191** | +1,83 | **+0,112** | 17,1 | **7,7 %** | 3/5 |

*(M60 es extensión exploratoria posterior al preregistro, no parte del pase)*

**La ventaja bruta es plana entre M5 y M30 —de +0,120 a +0,129— con muestras de
3.197 a 568.** Eso es un mecanismo, no un ajuste: si fuera casualidad de una
temporalidad, no aparecería igual en cuatro.

Y la neta sube monótonamente **por aritmética pura**: al subir de temporalidad el
stop se ensancha, el coste pasa del 27,8 % al 7,7 % del riesgo, y la misma ventaja
empieza a sobrar. **En M30 la R neta agregada de los siete instrumentos es
positiva por primera vez en todo el proyecto.**

Es lo contrario de lo que pasó con el fibo de H1, donde ensanchar el stop mataba
la ventaja. Aquí la ventaja aguanta y el coste se encoge.

## Lo que sigue sin estar establecido

1. **Los costes de los seis no-EURUSD son estimaciones mías.** Si el real fuera el
   doble, M30 vuelve a negativo. Es el mismo dato que llevo cinco días pidiendo.
2. **Las muestras se encogen al subir de temporalidad**: 246 operaciones en M60
   sobre cinco instrumentos. z +1,83 no decide nada por sí solo.
3. **Cero operaciones reales.** Como todo lo demás del proyecto.

## El siguiente paso

Un preregistro nuevo sobre M30/M60 con reserva de verdad —instrumentos que no
hayan participado, o los meses de 2026 que quedan— antes de tratarlo como algo
operable.

## Reproducir

`TF=30 python3 bt/smc_71.py` · pruebas con `PESIM=si`, `H4V=`, `TF=`
