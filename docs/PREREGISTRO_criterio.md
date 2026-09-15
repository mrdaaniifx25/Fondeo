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
