# Pre-registro · filtrar su estrategia por la tendencia actual

Firmado **antes** de correr `bt/tendencia_filtro.py`. Un solo pase.

## La pregunta

Su estrategia toma los dos lados: barrido del máximo de Asia → venta, barrido
del mínimo → compra. **¿Mejora si sólo toma el lado que va a favor de la
tendencia actual?**

Es la única variante de su patrón que no está medida.

## Por qué importa, y por qué es dudosa

`RESULTADOS_su_patron.md` midió que **si se conoce la dirección de la semana**,
el efecto es enorme:

```
  semana >80 pips A FAVOR del lado    acierto 47,9 %   neta +0,3514
  semana EN CONTRA del lado           acierto 31,1 %   neta -0,1653
```

Pero eso es el **oráculo**: mira el futuro. La pregunta es cuánto de eso
sobrevive usando una medida de tendencia **causal**, de las que se pueden leer
en el momento.

Y la evidencia previa dice que poco:

```
  filtro de dirección H4      RESTA: 35,0 % sin él -> 34,3 % con él
  filtro de dirección semanal EMPEORA en los tres instrumentos
```

## Los siete filtros que se prueban

Todos leídos **antes** de la operación, sin mirar un solo minuto del futuro:

```
  1  EMA(20) diaria        cierre de ayer por encima -> sólo compras
  2  EMA(50) diaria
  3  ROC de 5 días
  4  ROC de 20 días
  5  dirección del día anterior   (cierre contra apertura)
  6  dirección de la semana EN CURSO hasta el lunes anterior
  7  EMA(50) de H4
```

Para cada uno: **a favor**, **en contra**, y **sin filtro** como referencia.
Más el **oráculo** (la dirección real de la semana) como techo inalcanzable.

## Contraste PRINCIPAL

**R neta por operación del brazo «a favor»** de cada filtro, contra el sin
filtro (−0,0208 medido).

## Predicción firmada

- **Ningún filtro causal superará al sin filtro por más de 0,03 de R.**
- El **oráculo** sí: predigo que el brazo «a favor» del oráculo dará por encima
  de +0,15, confirmando lo ya medido.
- **La distancia entre el oráculo y el mejor filtro causal será el hallazgo**:
  predigo que se perderá más del 80 % del efecto al cambiar el futuro por el
  pasado.
- Al menos dos de los siete filtros saldrán **peor** que no filtrar.

## Qué me refutaría

Un filtro causal cuyo brazo «a favor» dé R neta positiva con z > +2 y que
mantenga el signo partiendo la muestra en dos mitades. Eso sería una mejora real
de su estrategia y la metería en el plan.

Una sola pasada. Lo que salga se publica.
