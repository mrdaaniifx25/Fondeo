# Preregistro · el barrido de liquidez

Escrito el 28 de agosto de 2026, antes de ejecutar. Una sola pasada.
Con el arreglo de `docs/CORRECCION_mirada_al_futuro.md` ya dentro.

## Por qué esto no estaba probado

Todo el proyecto ha probado **continuación**: una vela que cierra con el cuerpo
por fuera del nivel, y se compra la ruptura. El usuario lleva desde el principio
hablando de **liquidez**, que es lo contrario: el precio pincha el nivel con la
mecha, barre los stops que hay al otro lado, y se da la vuelta.

Son dos operaciones distintas y sólo se ha medido una.

## Definición del barrido

Vela de 5 minutos, en la ventana de las **08:00 a las 11:30** hora de Madrid, que
cumple las dos cosas:

- **Pincha**: su máximo supera el nivel (o su mínimo lo perfora).
- **Vuelve**: su cierre queda otra vez dentro del rango, del lado de dentro.

Entrada **a la contra** al cierre de esa vela: si barrió el alto se vende, si
barrió el mínimo se compra.

- **Stop**: 1 pip más allá del extremo de la mecha que hizo el barrido.
- **Objetivo**: 2 veces el riesgo.
- **Una por día**: la primera que aparezca, y se acabó.
- **Horizonte**: hasta las 22:00. **Coste**: 1,43 pips.

## Niveles

**Principal — Asia**: máximo y mínimo de 00:00 a 08:00 del mismo día.

**Secundario — Londres del día anterior**: máximo y mínimo de 09:00 a 17:30 del
día hábil anterior.

## Contrastes: dos, y ya está

1. Suma neta por día del barrido de Asia, 2020-2025.
2. Lo mismo con el nivel de Londres del día anterior.

**Predicción firmada: las dos serán positivas.**

Con dos contrastes, Bonferroni pide |z| >= 2,24.

**Muestra secundaria**: enero-julio de 2026.

**Se informa también** el barrido con stop mínimo de 10 pips, porque ya sabemos
que con 1,43 de coste un stop de 3 pips no puede ganar. Eso va marcado como
descriptivo, no como parte del contraste.

## Lo que espero, dicho antes de mirarlo

El barrido con mecha deja stops muy pequeños por definición: el riesgo es del
tamaño de la mecha. Con un coste de 1,43 pips, eso pinta mal. Si sale algo, lo
más probable es que sea bruto y no neto, como todo lo demás.

Si sale al revés o sin fuerza, se dice y se cierra la familia entera.
