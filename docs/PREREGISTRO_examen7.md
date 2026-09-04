# Preregistro · bloque 7 · ¿el indicador ayuda o estorba?

Escrito **antes** de que haga una sola sesión. El sorteo de qué sesiones llevan
indicador ya está hecho, con semilla fija, y está guardado en
`data/examen7_ind.json`. Un solo pase.

## Por qué este examen y no otro

Todo lo medido hasta aquí dice lo mismo:

```
  simulador de agosto     el momento lo pongo yo, sin M1     48 ops    29,2 %
  examen de roturas       el momento y el stop los pongo yo  145 ops   +0,511 R sobre lo que dejó
  exámenes 1-5            el momento lo elige él             223 ops   64,8 %
```

**Solo rinde cuando elige él el momento.** Y un indicador es, por definición, una
máquina de ponerle momentos delante: en estas cuarenta sesiones dibuja **14,4
flechas por sesión** de media, y 38 roturas contando las grises. Él toma 1,5.

En el bloque 5 hubo una comparación con y sin indicador —58,3 % contra 65,7 %—
pero **la eligió él**, así que no vale: pudo encenderlo justo en las sesiones
difíciles. Aquí lo sortea la semilla.

## El montaje

Cuarenta mañanas nuevas de EURUSD, 08:00-11:30 hora de Madrid, elegidas con
semilla `20260905` **excluyendo los 174 días ya usados** en los bloques 1 a 6.

Idéntico al bloque 5: H4, M15, M5 y M1 a la vez, avanza minuto a minuto, **elige
él el momento**, **pone él el stop**, objetivo automático a 1:2, riesgo 1 %, y las
reglas de la cuenta de FundingPips.

**En veinte sesiones sorteadas** se dibuja además el indicador tal cual:
el cuerpo de la M5 de referencia, las flechas COMPRA/VENTA de las candidatas que
pasan los tres filtros, los triángulos grises de las que no, y el contador del
día. **En las otras veinte, nada.** No sabe cuál le toca hasta que abre la sesión.

**Garantía de que no hay futuro**, igual que siempre: el fichero se corta en el
minuto 210 y solo lleva M1 de la sesión; M5, M15 y H4 se construyen en el
navegador hasta el cursor. Comprobado: el minuto más alto del fichero es 210.

## Métrica principal, que es la única con potencia de verdad

**Operaciones por sesión, con indicador contra sin indicador.**

No el acierto: el acierto no se puede decidir aquí y lo digo antes de empezar.

```
  20 sesiones por brazo · desviación típica esperada ~1,5 op/sesión
  error típico de la diferencia: 0,47
  detecta una diferencia de 0,93 operaciones por sesión, y nada menor
```

Umbral: **|z| > 1,96**, dos colas. Predicción firmada: **más con indicador**.

## Secundaria con potencia decente

**Coincidencia con las flechas.** De cada entrada suya, si cae a menos de 3
minutos de una candidata que pasa los filtros. En las sesiones SIN indicador se
calcula después, con las mismas candidatas que no llegó a ver: eso da la tasa de
coincidencia natural.

```
  ~30 operaciones por brazo · detecta una diferencia de 25 puntos
```

Umbral: **|z| > 1,96**. Predicción firmada: **más coincidencia con indicador**.

## Secundarias SIN potencia · descriptivas, no deciden nada

Se reportan y no se usan para concluir. Lo declaro ahora para no poder venderlo
como hallazgo después:

- acierto con contra sin (detectaría 25 puntos, y espero como mucho 10)
- R neta con contra sin (detectaría 0,76 R)
- reparto por hora, por stop, por dirección
- cuántas sesiones sin operar en cada brazo
- **cuántas sesiones hace de una sentada**, con la hora de cada decisión

## Comprobación de replicación

Sobre las cuarenta juntas, con y sin: **¿vuelve a salir su 64,8 %?**
Umbral contra el 33,3 % geométrico: z > +1,64. Es la sexta vez que se mide y las
cinco anteriores lo pasaron.

## Las cinco predicciones firmadas

1. Toma **más** operaciones con el indicador: entre **+0,3 y +1,2** por sesión.
2. La coincidencia con las flechas sube: **>60 % con** contra **~35 % sin**.
3. Su acierto **baja** con el indicador, entre 0 y 12 puntos, y **no** llega a
   significativo.
4. El acierto de las cuarenta juntas queda entre **55 % y 68 %**.
5. Hace las cuarenta sesiones en **menos de cuatro sentadas**.

La 3 es la importante: si acierta, el indicador es un estorbo con buena pinta, y
la conclusión práctica es **no ponerlo en el gráfico en real**.

## Qué haría falta para que el indicador se quede

Que la métrica principal salga plana o a favor —que no le multiplique las
operaciones— **y** que la R neta con indicador no sea peor. Si le sube las
operaciones sin subirle el acierto, se retira, porque su ventaja necesita las dos
mitades: elegir bien **y** elegir poco.

## Reproducir

`python3 bt/examen_datos.py 20260905 40 7 …` · `python3 bt/examen7_indicador.py`
