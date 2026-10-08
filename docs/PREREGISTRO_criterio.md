# Pre-registro · ¿aporta algo el criterio humano?

Escrito **antes** de ver ninguna etiqueta.

## Qué se pregunta

Todo lo medido esta semana son reglas mecánicas, y todas se quedan cerca del
coste sin pasarlo. La objeción de las fuentes siempre es la misma: *la clave está
en leer el contexto y saber cuándo el setup se ve bien.* Eso no se puede refutar
midiendo reglas. Se refuta o se confirma midiendo **al lector**.

## La muestra

300 setups de **liquidez simple en H4** —la única celda con ventaja bruta real
medida: +0,085 R sobre 9.197 casos— repartidos 150 EURUSD y 150 NAS100,
sorteados al azar del histórico 2020-2026 con semilla 20260825.

Verificado antes de publicar:
- ningún campo de resultado viaja al fichero de la página
- el gráfico termina **exactamente** en la vela de entrada, sin una sola vela posterior
- las 300 estructuras comprobadas una a una: el barrido existe, el cierre queda
  dentro del rango, el stop es el extremo del barrido, el objetivo el extremo
  opuesto de la vela base
- orden barajado, identificadores opacos

**Tasa base oculta: 49,0 % de acierto, R media +0,103, desviación típica 1,422.**

## Las etiquetas

Tres: *lo operaría*, *no lo operaría*, *no lo veo claro*. Las dudas quedan fuera
del contraste principal.

## El criterio, fijado ahora

Se compara la R media de los marcados **sí** contra los marcados **no**.

Con 150 contra 150, el error típico de la diferencia es **0,164 R**. Con reparto
desigual empeora. Así que:

| separación real | z esperado con 150/150 |
|---|---|
| +0,50 R | 3,0 |
| +0,42 R | 2,6 |
| +0,30 R | 1,8 |
| +0,10 R | 0,6 |

**Se considera que el criterio aporta si la diferencia supera z = 2,58**, es
decir, una separación de al menos **+0,42 R**. Un solo contraste, declarado aquí.

Y esto hay que decirlo por delante: la prueba **solo puede detectar un efecto
grande**. Si el criterio humano aporta +0,10 R, saldrá indistinguible de cero y
no se podrá concluir nada. Es una limitación de tamaño, no del criterio.

## Lo secundario, que no decide nada

Si el contraste principal sale, se mira además:
- qué variables mecánicas de las 54 predicen la etiqueta (o sea, qué está
  mirando el lector sin saberlo)
- si el criterio aporta en los dos instrumentos o solo en uno
- si los marcados **sí** cruzan el coste en neto, que es lo único que importa
  para operar

## Lo que invalidaría la prueba

Si casi todo queda marcado igual —90 % que sí o 90 % que no— no hay contraste
que hacer y se dice así, sin buscarle otra lectura.

Página: https://claude.ai/code/artifact/93a3ca6b-603e-4085-9792-73e005046555

---

## Reapertura · 16 de septiembre de 2026

La prueba se selló el 25 de agosto y nunca se ejecutó. Se reabre **sin tocar
una sola línea de lo anterior**: misma muestra, mismas 300, misma semilla, mismo
contraste único y mismo umbral z = 2,58.

Lo único que cambia es la mecánica de guardado. La página original guardaba en
el navegador y obligaba a copiar y pegar el avance; ahora guarda en la nube, así
que el etiquetado puede hacerse en varias sesiones y desde distintos aparatos sin
riesgo de perderlo.

Página nueva: https://claude.ai/artifact/GjVK8EFGDXmfw2pvhoihEy

La tasa base sigue oculta en `data/etiquetas_verdad.csv` y no se abre hasta que
las etiquetas estén cerradas.

### Lo que se ve en cada caso, ampliado el 16 de septiembre

Petición suya: *"deberíamos ver H4 y H1, necesito que el rango esté bien marcado
en ambas temporalidades y la entrada en M5"*. Tiene razón en que una prueba que
le enseña menos de lo que él mira en real no podría concluir nada si sale nula:
diría, con motivo, que no le enseñé el contexto con el que decide.

Así que cada caso pasa de un gráfico a tres:

| marco | velas | para qué |
|---|---|---|
| H4 | 18 | el rango, el barrido y los niveles del día anterior |
| H1 | 44 | el mismo rango marcado de cerca |
| M5 | 60 | la entrada |

El rango de la vela base se pinta como banda en los tres, con el mismo color.

**Esto cambia lo que se MUESTRA, no lo que se mide.** Los 300 casos son los
mismos, con los mismos identificadores, el mismo orden barajado y la misma
semilla 20260825. La muestra, el contraste único, el umbral z = 2,58 y la tasa
base sellada no se tocan. `data/etiquetas_verdad.csv` no se ha abierto.

Código en `bt/amplia_etiquetas.py`, que audita caso por caso lo único que podría
invalidar la prueba: **que los tres marcos cierren exactamente en el precio de
entrada**. Si alguno arrastrase una sola vela posterior, ese cierre no
coincidiría. Los 300 pasan.
