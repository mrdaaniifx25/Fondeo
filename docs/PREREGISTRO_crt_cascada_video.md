# Pre-registro · la cascada CRT D1 -> H4 -> H1 -> M15 del curso en vídeo

Firmado **antes** de correr `bt/crt_video.py`. Un solo pase.

Vídeo aportado por el usuario: curso gratuito de CRT (Candle Range Theory),
canal de Alex Ruiz. El vídeo da **cinco pasos numerados y mecánicos**, cosa
rara: casi todo lo que se ha medido en este proyecto venía descrito con
palabras, no con reglas. Éstas se pueden programar tal cual.

## La regla, literal

1. Marcar el rango de la vela **diaria anterior ya cerrada** (máximo a mínimo).
2. Esperar a que el día en curso **active** un extremo: si barre el mínimo, el
   sesgo es alcista; si barre el máximo, bajista. *(«activado» ≠ «confirmado»:
   confirmado exige además cerrar de vuelta dentro.)*
3. Bajar a **H4**: el rango de la vela H4 anterior tiene que estar activado
   **en la misma dirección**.
4. Bajar a **H1**: lo mismo.
5. Bajar a **M15**: el rango M15 anterior tiene que estar **confirmado** —
   barrido *y* cierre de vuelta dentro, sin romper el extremo opuesto.
   -> Entrada **a mercado en la apertura de la vela M15 siguiente**.
   -> Stop **detrás de la mecha del barrido** («por debajo de los mínimos
      anteriores»).
   -> Objetivo **el extremo opuesto del rango H4** («como mínimo»).

Variantes de objetivo que el propio vídeo menciona: el 50 % del rango diario,
y el extremo completo del rango diario («un 25 de rentabilidad-riesgo»).

## Qué tiene esto de distinto respecto a lo ya medido

Hay veinte documentos de CRT en este repositorio. Lo que **no** está medido con
esta forma exacta:

- `RESULTADOS_crt_cascada.md` encadenaba rangos hacia el **objetivo semanal**.
  Aquí el objetivo lo pone **H4**, que es mucho más cerca y cambia el R:R entero.
- `RESULTADOS_cascada_h4_m1.md` usaba H4 como filtro de dirección, no como
  eslabón de una cadena de cuatro.
- Nadie ha exigido las cuatro a la vez con la mezcla **activado / activado /
  activado / confirmado** que pide el vídeo.

Así que se corre. No porque la respuesta sea dudosa, sino porque la regla es
distinta y el usuario tiene derecho a un número suyo, no a un documento vecino.

## Datos

EURUSD (2021-2026), oro (2023-2026), DAX (2023-2026), M1 -> rejillas M15/H1/H4/D1
en hora de Nueva York. Costes del repositorio: 1,43 pips / 0,35 $ / 1,6 puntos.

## Contraste PRINCIPAL, declarado antes de mirar

**R neta media por operación** de la celda completa (las cuatro temporalidades
alineadas, objetivo al extremo opuesto de H4), una operación por día como máximo,
agrupando los tres instrumentos. z con error estándar agrupado por
instrumento-día.

## Predicción firmada

Escribo lo que espero, para que se me pueda pillar:

- **R bruta**: entre −0,05 y +0,05. Indistinguible de cero.
- **R neta**: negativa, entre −0,10 y −0,40, con z < −3.
- **La cascada no será monótona**: exigir 3 temporalidades alineadas no dará
  mejor resultado que exigir 0. Si la fractalidad informara, tendría que crecer.
- **El placebo de dirección empatará**: invertir el lado de cada entrada dará
  aproximadamente el mismo resultado bruto.

## Qué me refutaría

R **neta** positiva con z > +2 en la celda principal, y placebo de dirección
claramente por debajo. Eso sería una ventaja real y lo diría así.

## Controles obligatorios

1. **Placebo de dirección**: mismas entradas, mismos instantes, lado invertido.
2. **Monotonía de la cascada**: 0 / 1 / 2 / 3 temporalidades alineadas.
3. **Nulo geométrico**: acierto esperado = riesgo/(riesgo+recorrido) con el R:R
   realmente observado, no el 50 % ingenuo.
4. **Bruta y neta por separado**, con el coste declarado.

Una sola pasada. Lo que salga se publica.
