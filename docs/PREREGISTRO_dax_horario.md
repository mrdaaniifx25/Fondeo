# Pre-registro · el CRT en DAX, dentro del horario del usuario

Escrito y subido ANTES de medir. 21/09/2026.

## De dónde sale

Objetivos fijados con el usuario:

| | |
|---|---|
| capital | **cuenta fondeada** |
| riesgo | **0,25 %** por operación (único que sobrevive al −10 %) |
| horario | **08:00-12:00** y **13:00-16:00** de Madrid |
| plazo | sin fecha → se pueden usar marcos grandes |

Y dos hallazgos de hoy:

1. El CRT en H12 que salía positivo (+0,072) lo sostenían **los índices
   americanos**: SPX500 +0,158 frente a EURUSD +0,016 y GBPUSD −0,002.
2. En divisas, partido por horario, **el tramo que el usuario puede operar es
   el peor**: neta −0,067 en su ventana contra −0,031 de madrugada.

El DAX es el único índice que cotiza **dentro de sus dos ventanas** (08:00 a
22:00 de Madrid), así que es donde el objetivo y la evidencia apuntan a la vez.

## Qué se mide

CRT desnudo, **exactamente el mismo código** que `bt/crt_por_temporalidad.py`
(`velas_ref` anclado a la 01:00 de Nueva York, `secuencias` con liquidez
simple, `resuelve` en M1). Sin reimplementar nada, para que no haya una
definición nueva que ajuste el resultado.

- Marcos: H1, H2, H4, H6, H8, H12, D1.
- Coste DAX: **1,6 puntos** (1,2 de horquilla + comisión).
- Partición: entrada **dentro** de 08:00-12:00 o 13:00-16:00 de Madrid, frente
  a **fuera**.

## La limitación, por delante

El DAX sólo está de **2023 a 2026** (3,7 años) frente a los 6,6 de los demás.
En H12 eso son del orden de **200-400 operaciones**, no las 3.108 del estudio
original. Con esa muestra, el intervalo será ancho y lo más probable es que no
se pueda concluir. **Eso también es un resultado.**

## Criterio

1. neta > 0 **dentro del horario**, con el IC95 sin tocar el cero, **y**
2. la neta dentro del horario no peor que fuera, **y**
3. coherencia entre marcos vecinos (no un pico aislado rodeado de vecinos
   negativos, que es la firma del ruido).

## Predicción

- Bruta positiva y pequeña en varios marcos, como en todos los instrumentos.
- **Neta negativa en H1-H4** por el coste, y cruzando a cero en H8-D1.
- **Intervalos demasiado anchos para cumplir el criterio 1.** Espero acabar en
  «hace falta el histórico 2010-2022 del DAX».
- Sin diferencia clara entre dentro y fuera del horario: el DAX cotiza casi
  sólo en horario europeo, así que casi todo caerá dentro.
