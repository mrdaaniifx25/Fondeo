# Pre-registro · la gestión de riesgo del vídeo de fondeo

Firmado **antes** de correr `bt/gestion_fondeo.py`. Un solo pase.

## El vídeo

Guía de cuentas de fondeo (Alex Ruiz). **Es el mejor material que ha llegado a
este proyecto**, y conviene decirlo antes de criticarlo: casi todo lo que afirma
es correcto y coincide con lo ya medido aquí.

### Lo que dice, y que ya está confirmado en este repositorio

1. *«Lo difícil no es el beneficio, es llegar sin comerte el drawdown.»*
   Es el **teorema de la barrera**, medido en `RESULTADOS_carrera_fondeo.md`.
2. *«Una cuenta de 50.000 con 4 % de DD son 2.000 $. Esa es tu cuenta real. Si
   arriesgas el 1 %, arriesgas el 25 % de tu capital operativo.»* **Correcto**,
   y es la cuenta que casi nadie hace.
3. *«Puedes ser rentable y no fondearte nunca.»* **Correcto**: es la varianza.
4. El embudo de My Forex Funds: 100.000 pagan → 10.000 pasan fase 1 → 2.400 se
   fondean → **72 retiran**.
5. La relación acierto ↔ R:R para el umbral de rentabilidad. Aritmética correcta.
6. *«Lleva un diario para conocer tu win rate real.»* Correcto.

### La tesis central, que es lo que se va a medir

> **A igual rentabilidad, un R:R bajo con acierto alto tiene menos varianza,
> permite arriesgar más y por tanto aprueba más y más rápido que un R:R alto con
> acierto bajo.**

Y sus cuatro conclusiones operativas:

```
  1  diario de trading para conocer el win rate real
  2  win rate < 50 %  ->  arriesgar 0,50 % o menos
  3  win rate > 65 %  ->  subir a 1,5 %
  4  subir el tamaño de forma gradual, 10-20 % cada vez
```

### Y el error que hay en la base

> *«Al beneficio vas a terminar llegando sí o sí, tarde o temprano.»*

**Eso presupone esperanza positiva.** Con esperanza cero o negativa no se llega
nunca, ni tarde ni temprano. Y el propio embudo que él cita lo dice: si la gente
fuera rentable y sólo gestionara mal el riesgo, la tasa de fondeo no sería del
**2,4 %**. Un 2,4 % no es un problema de tamaño de posición: es esperanza
negativa.

*(Declaro también el conflicto de interés que el vídeo declara: recomienda
FundedNext con su enlace de referidos. No invalida la aritmética; se anota.)*

## Lo que se va a simular

Secuencias de operaciones hasta tocar objetivo o drawdown, 200.000 carreras por
celda. Dos formatos:

- **Futuros 50k**: colchón 4 % (2.000 $), objetivo 3.000 $ = **150 % del colchón**.
- **Forex 10k dos fases**: fase 1 +8 %, fase 2 +5 %, DD total 10 %.

Parámetros: acierto `p`, ratio `R:R`, riesgo por operación, coste en R.

## Los tres contrastes, declarados antes de mirar

1. **SU TESIS · a igual esperanza**, ¿aprueba más el R:R bajo con acierto alto?
   Se comparan parejas con **esperanza idéntica** (0,05 R y 0,10 R por operación)
   y R:R de 0,5 / 1 / 2 / 3 / 5.
2. **PRINCIPAL · a esperanza CERO** (lo que mide este proyecto), ¿cuál es el
   riesgo por operación óptimo?
3. **Qué esperanza hace falta** para que su regla del 1,5 % dé un 50 % de
   aprobados.

## Predicción firmada

- **Su tesis saldrá CORRECTA con esperanza positiva.** A igual esperanza, el R:R
  bajo aprobará más. Predigo una diferencia de 10 a 25 puntos porcentuales entre
  R:R 0,5 y R:R 5.
- **Y saldrá AL REVÉS con esperanza cero.** Con ventaja nula el teorema de la
  barrera dice que la probabilidad de tocar antes el objetivo que el drawdown
  **no depende del tamaño**, salvo por el coste: y el coste se paga **por
  operación**, así que arriesgar **menos** significa más operaciones y más coste
  total. Predigo que a esperanza cero **el riesgo grande gana**, que es
  exactamente lo contrario de sus conclusiones 2 y 3.
- La esperanza necesaria para un 50 % de aprobados al 1,5 % estará **entre 0,05
  y 0,15 R por operación**.

## Qué me refutaría

Que a esperanza cero el riesgo pequeño apruebe igual o más que el grande. Eso
significaría que sus conclusiones valen también sin ventaja, y lo diría así.

Una sola pasada. Lo que salga se publica.
