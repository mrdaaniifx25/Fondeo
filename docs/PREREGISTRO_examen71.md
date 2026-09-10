# Preregistro · bloque 8 · ¿su criterio le suma o le resta a una estrategia que ya funciona?

Sellado **antes** de construir la página y antes de que vea un solo caso.

## Por qué este examen y no otro

La estrategia del 71 % **ya es mecánica**: seis reglas, todas numéricas, cero
decisiones humanas. Un examen donde él solo aprieta «sí» a todo no mediría nada.

Lo que nunca se ha probado es otra cosa: **¿su criterio mejora o empeora una regla
que ya tiene ventaja?**

Todo lo medido hasta ahora dice que su selección vale **+0,511 R (z +3,27)** sobre
las roturas de su propia regla. Pero eso era EURUSD, en Londres, con su horario y
sus cuatro temporalidades. Aquí no: M30, instrumento oculto, sin fecha ni hora, en
una estrategia que no es la suya.

Y contra eso está el AUC de 0,502: su criterio no está en los números.

## El material

**240 señales** de la estrategia del 71 % en M30, cuarenta de cada uno de seis
instrumentos, sorteadas con semilla `20260905` y barajadas. No verá cuál es el
instrumento, ni la fecha, ni la hora.

De cada una ve **exactamente lo que se ve en el momento en que dispara**: las
velas de M30 desde 60 antes del barrido hasta el cierre de la ruptura, el nivel
barrido, el rango de H4 con su premium/discount, y la entrada, el stop y el
objetivo ya calculados. Ni una vela más.

**La regla a ciegas, sobre estas 240:**

```
  acierto 35,4 %   ·   R bruta +0,222   ·   R NETA +0,083
```

*(Es mejor que la población completa —32,7 % y +0,005— porque el muestreo coge 40
de cada instrumento sin importar cuántas genere cada uno, y eso pesa más los
índices, que son los baratos. El listón de este examen es +0,083, no +0,005.)*

## Métrica principal

**R neta de lo que TOMA contra R neta de lo que DEJA.**

Umbral: **|z| > 1,96**, dos colas. Predicción firmada: **positiva**, o sea que
suma.

```
  potencia: si toma la mitad, 120 contra 120, con desviación típica ~1,3
  error típico de la diferencia: 0,17
  detecta una diferencia de 0,33 R y nada menor
```

**Lo digo antes: no tiene potencia para detectar una mejora pequeña.** Si sale
+0,15 no se podrá decir ni que sí ni que no.

## Secundaria

**¿Bate a la regla a ciegas?** R neta de lo que toma contra el +0,083 de las 240.

## Las cuatro predicciones firmadas

1. Toma entre el **40 % y el 70 %** de los casos.
2. La diferencia tomadas−dejadas queda entre **−0,10 y +0,25 R**, y **no** llega
   a significativa.
3. Su acierto sobre lo que toma queda entre el **33 % y el 45 %**.
4. Le costará más que el examen de roturas y lo dirá: el material le es ajeno.

La 2 es la importante. **Predigo que su criterio NO transfiere** a una estrategia
que no es la suya, en una temporalidad que no usa y en instrumentos que no
reconoce. Si me equivoco y suma, es el mejor resultado del proyecto: significaría
que su ojo vale sobre material que no ha visto nunca.

## Qué se hace con cada resultado

- **Suma y significativo** → operar la estrategia con su filtro encima.
- **Plano** → operarla mecánica y no mirar. Menos trabajo, mismo resultado.
- **Resta** → operarla mecánica y **no dejarle decidir**. Es un resultado útil,
  no un fracaso.

Un solo pase. Se reporta salga lo que salga.
