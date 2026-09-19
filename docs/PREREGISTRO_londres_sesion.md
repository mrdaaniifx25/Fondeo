# Pre-registro · el filtro de sesión sobre el CRT canónico

**Escrito el 2026-09-09, antes de abrir los ficheros de `reservado/`.** Ese es el
punto: la predicción y el criterio quedan fijados mientras los datos siguen
cerrados.

## De dónde sale la hipótesis

De un vídeo de Benjamín (@bilesdealgo), cuya afirmación central es que el barrido
de liquidez **sólo** vale si ocurre dentro de dos ventanas horarias:

```
Londres        09:00 - 11:00  hora de Madrid
Nueva York     14:00 - 16:30  hora de Madrid
```

Y de un hallazgo propio que hasta ahora estaba archivado como control, no como
hipótesis. En `RESULTADOS_crt_9am.md`, el control de detección sobre cinco anclas
horarias de Nueva York dio:

| ancla NY | R bruta | z | positiva en |
|---|---|---|---|
| **03:00** | **+0,0779** | **+3,27** | 5/5 instrumentos · 6/7 años |
| 06:00 | −0,0057 | −0,26 | |
| 09:00 | +0,0146 | +0,61 | |
| 12:00 | +0,0025 | +0,10 | |
| 15:00 | −0,0257 | −1,08 | |

**Las 03:00 de Nueva York son las 09:00 de Madrid**: la apertura de Londres, y
exactamente la ventana que él declara. Coincide además con lo que ya salía en
`RESULTADOS_smc71.md` y en el barrido de Londres: la estructura que existe en
este repositorio está en la apertura de Londres, no en la de Nueva York.

Aquella fila acabó en neta −0,1601 porque el stop mediano eran ~6 pips y el coste
se llevaba el 23,8 % del riesgo. **Nunca se ha probado ese mismo filtro sobre la
maquinaria del CRT canónico**, donde el riesgo mediano va de 8 a 17 pips y el
coste del 7 al 14 %. Eso es lo único nuevo que se mide aquí.

## Lo que NO se está probando

Para que conste, porque son cosas que el vídeo también dice y que ya están
cerradas en este repositorio:

- Rangos dinámicos por sesión (`RESULTADOS_crt_sesion.md`: primaria +0,0003 R,
  z +0,02, y el control de detección puntuó más alto que el modelo).
- Entrar en el desequilibrio/FVG en M1-M5 (toda esa familia pierde en los siete
  instrumentos: Fibonacci z −10,29, estocástico z −6,44, EMA20 z −4,20).
- Que el CRT exista: existe, y está replicado a ciegas (+0,089 R bruta).

## Qué se va a correr, exactamente

La maquinaria canónica sin tocar —`crt_canonico.velas_ref`,
`liquidez_multiple.secuencias/resuelve`, `k = 1`, objetivo el extremo opuesto de
la vela base, stop el extremo barrido, `ancla_ny = 1`— y **una sola línea nueva**:
clasificar cada secuencia por la hora de Madrid en que cierra su vela de
manipulación.

```
LONDRES    09:00 - 11:00   Madrid          (la ventana del vídeo)
NY         14:00 - 16:30   Madrid          (la otra ventana del vídeo)
CTRL_A     04:00 - 06:00   Madrid          (control, 2,0 h, sin razón para funcionar)
CTRL_B     19:00 - 21:30   Madrid          (control, 2,5 h, sin razón para funcionar)
FUERA      el resto
```

Hora de **Madrid**, con cambio de horario incluido —es lo que él dice
literalmente—, resuelto con `tz_convert("Europe/Madrid")`, no con un desfase fijo.

Temporalidades **H1 y H4**, las dos que nombra el vídeo. Instrumentos:
**XAUUSD y GRXEUR, enero-julio de 2026**, los catorce ficheros de `reservado/`,
que no se han abierto nunca. Costes ya declarados en
`PREREGISTRO_h12_ciego.md` y que no se tocan: **35 unidades en oro, 2,0 puntos en
DAX**.

## La celda principal, declarada ahora

```
H1 · ventana LONDRES · R BRUTA
comparada contra
H1 · ventana FUERA   · R BRUTA
```

**Bruta, no neta.** El coste es una división conocida y separada; lo que el filtro
de sesión afirma es que el patrón funciona *mejor* dentro de la ventana. Ésa es la
afirmación, y ésa es la que se mide. La neta se reporta en todas las celdas, pero
no es el criterio.

H1 y no H4 porque a 1,17 instrumento-años H4 deja unas 60 operaciones y no puede
decir nada de nada.

## La potencia, calculada ANTES y no después

Éste es el error que cometí en `PREREGISTRO_h12_ciego.md` —calculé la potencia
suponiendo un efecto mayor del que la propia evidencia sugería— y no lo voy a
repetir sin avisar.

```
operaciones esperadas   H1, dos instrumentos, 7 meses   ~1.600
fracción en LONDRES     ventana de 2 h sobre 24         ~8 %  ->  ~130
desviación típica de R                                  ~1,3
error típico de la DIFERENCIA (130 contra ~1.470)       ~0,12
```

**Diferencia mínima detectable con z = 2: +0,24 R.** El efecto plausible, según
la fila de las 03:00, es de **+0,08 R**. La prueba es, por tanto, entre tres y
cuatro veces demasiado pequeña para confirmar la hipótesis.

Se corre igualmente, y se declara ahora para qué sirve y para qué no:

| resultado | lectura declarada de antemano |
|---|---|
| LONDRES claramente negativa, o por debajo de FUERA | **falsación**. La idea se cierra. |
| un CONTROL por encima de LONDRES | **falsación**. Estamos midiendo la maquinaria, no la sesión. |
| LONDRES por encima, sin significación | **no concluyente**. No es un éxito y no se contará como tal. |
| LONDRES por encima con IC95 que excluye el cero | sorpresa; haría falta un efecto de +0,24 R, tres veces el esperado. Se reporta con esa advertencia. |

## Las predicciones

1. **La bruta de LONDRES en H1 será mayor que la de FUERA.** Es la hipótesis.
2. **Ningún control (A ni B) superará a LONDRES.** Es la que más me juego: si un
   control gana, la sesión no es la explicación y el asunto se cierra ahí mismo.
3. **NY no superará a LONDRES.** El vídeo dice que las dos ventanas valen; este
   repositorio dice que la de Nueva York no (ancla 15:00, la peor de las cinco).
   Si NY gana, mi lectura del mecanismo está mal.
4. **El riesgo mediano dentro de LONDRES no diferirá del de FUERA en más de un
   20 %.** Comprobación de mecanismo: si el filtro cambia sobre todo el tamaño del
   stop, lo que se esté midiendo es geometría, no sesión.
5. **La neta será negativa en H1 en las cinco ventanas**, controles incluidos. El
   coste en H1 se lleva del 7 al 14 % del riesgo y la bruta no llega a eso.

## Qué se hace con el resultado

Una sola pasada. Se publica entera, salgan las cinco ventanas como salgan, y se
reporta según la tabla de lecturas de arriba, sin renegociar el criterio.

Si sobrevive —es decir, si no se falsa—, **no se opera nada**. Lo que
correspondería es una segunda prueba con potencia suficiente: hacen falta unos
**9 instrumento-años en la ventana de Londres**, o sea unos catorce
instrumento-años de datos, sobre instrumentos que tampoco hayan participado.

Los cinco instrumentos originales no sirven para eso: el ancla de las 03:00 se
encontró ahí.
