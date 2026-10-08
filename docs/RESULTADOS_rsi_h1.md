# Resultados · RSI + soporte/resistencia + vela de giro, en H1

Pre-registro: `docs/PREREGISTRO_rsi_h1.md`, subido **antes** de medir.
Código: `bt/rsi_h1.py`. EURUSD 2021-2026, oro y DAX 2023-2026.

## Primero, un error mío en el pre-registro

Escribí que en H1 el stop típico sería de **32 pips** y el listón de **+1,5
puntos**, y con eso argumenté que ésta era «la primera de las cuatro con una
posibilidad aritmética».

**Medido, el stop es de 9,8 pips.** El stop va al extremo de las tres velas
previas, y en una vela de giro de H1 eso queda muy cerca de la entrada. Así que:

```
  lo que supuse    stop 32,0 p   coste  4,5 %   umbral 34,8 %   listón +1,5
  lo que sale      stop  9,8 p   coste 17,0 %   umbral 39,0 %   listón +5,7
```

**Adiviné el ancho del stop en vez de medirlo.** El argumento que motivaba la
prueba era falso: esta geometría está donde las otras tres, no por debajo.

## El principal declarado

```
  EURUSD · RSI 30/70 · nivel a menos de 0,5 ATR · objetivo 2R
  n 139   riesgo 9,8 p   coste 17,0 %
  acierto 33,1 %    azar 33,3 %    umbral 39,0 %
  NETA -0,1771 [-0,4125, +0,0584]
```

**33,1 % contra un azar de 33,3 %.** Clavado en el precio justo.

## Los tres controles, que son lo que cierra esto

```
  la señal completa                        n   139   acierto 33,1 %   NETA -0,1771
  placebo · lados barajados                n   139   acierto 33,8 %   NETA -0,1490
  sin el filtro de NIVEL (sólo RSI + vela) n   421   acierto 33,7 %   NETA -0,1460
  sin el filtro de RSI (sólo nivel + vela) n 5.631   acierto 33,4 %   NETA -0,1405
```

Las cuatro filas en **33,1 · 33,8 · 33,7 · 33,4**. El azar es 33,3.

- **Barajar la dirección al azar acierta MÁS** que la señal completa.
- **Quitar el soporte/resistencia no empeora nada.**
- **Quitar el RSI tampoco.**

Los tres ingredientes del vídeo —RSI, nivel y vela de giro— no aportan nada por
separado ni juntos. Y la última fila tiene **5.631 operaciones**: ahí ya no hay
duda de muestra.

## Las 18 celdas

```
  RSI 30/70 · 0,25 ATR · 1R   n  96  45,8 %  (azar 50,0)  NETA -0,2430
  RSI 30/70 · 0,5  ATR · 2R   n 139  33,1 %  (azar 33,3)  NETA -0,1771
  RSI 30/70 · 1,0  ATR · 2R   n 228  36,0 %  (azar 33,3)  NETA -0,0817
  RSI 30/70 · 1,0  ATR · 3R   n 228  30,3 %  (azar 25,0)  NETA +0,0499 [-0,1886, +0,2883]
  RSI 20/80 · todas           n 7-12  (insuficiente)
```

Una sola celda con neta positiva, con el cero bien dentro. Y con 20/80 apenas
salen siete operaciones en seis años: el umbral estricto del vídeo deja la
estrategia sin muestra.

## Réplica en oro y DAX

```
  oro   n 103   acierto 29,1 %   umbral 35,7 %   NETA -0,1973 [-0,4618, +0,0673]
  DAX   n  79   acierto 46,8 %   umbral 35,6 %   NETA +0,3358 [+0,0029, +0,6687]  CRUZA
```

El DAX cruza. **Y no cuenta**: es el mejor de tres instrumentos —lo que por azar
regala unos +4,5 puntos—, con **79 operaciones**, y los otros dos salen
negativos. El criterio pedía el mismo signo en los dos, y sale +0,34 contra
−0,20.

## Contra el criterio pre-registrado

| criterio | resultado |
|---|---|
| 1. el principal con neta > 0 y el IC limpio | **NO.** −0,1771 |
| 2. por encima del sesgo de selección | no aplica |
| 3. los controles de ingredientes **peores** que la señal | **NO: son mejores** |
| 4. mismo signo en oro y DAX | **NO.** −0,20 y +0,34 |

## Récord de predicciones

Cuatro de cinco.

| predicción | resultado |
|---|---|
| saldrá plano | 33,1 % contra 33,3 % de azar ✔ |
| el control sin nivel rendirá casi igual | 33,7 % ✔ |
| el control sin RSI también | 33,4 % ✔ |
| 150-400 operaciones en EURUSD | **139** ✘, justo por debajo |
| el criterio no se cumplirá | no se cumple ✔ |

Y la predicción que **no** estaba en la lista y falló: el listón. Dije +1,5 y
son +5,7, por suponer el ancho del stop en vez de medirlo.

## Lo que él mismo dice en el vídeo

> *«una estrategia de trading como ésta no es suficiente… si te limitas a
> intentar repetirla, no serás rentable»*

Tiene razón, y el aviso es honesto. Lo que no dice es que el hueco no se tapa
con gestión: la regla acierta **exactamente lo que da el azar** y el coste se
lleva 17 céntimos de cada euro arriesgado.
