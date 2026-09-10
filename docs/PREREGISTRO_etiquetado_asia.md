# Pre-registro · la baraja ciega del barrido de Asia

**Escrito antes de ver una sola respuesta.** Fecha: 2026-08-27.

## Qué pregunta responde

La prueba mecánica de `bt/asia_londres.py` midió *la regla escrita*, y salió
plana en bruto (−0,007 R) y negativa en neto (−0,252 R). Pero el usuario no
opera una regla escrita: mira el gráfico y decide. Esa diferencia —el criterio—
nunca se ha medido, y es lo único que queda por comprobar de esta familia.

Hay además un problema de origen: en TradingView con plan gratuito no hay
repetición intradía, así que cuando el usuario revisa un día pasado ve todas las
velas a la vez. Lo que encuentra así no es un hallazgo, es una confirmación.
La baraja elimina eso: **el corte lo hago yo, con los datos, y el futuro no está
en el fichero que se publica.**

## Cómo se construye la baraja

`bt/etiquetado_asia.py`, semilla `20260827`.

```
INSTRUMENTO   EURUSD, velas de M5 en hora de Madrid
PERIODO       2020-01-01 a 2025-12-31   (2026 queda reservado)
CANDIDATOS    225 · primer barrido del día con envolvente en 1 o 2 velas
MUESTRA       60 · diez por año, al azar sin reemplazo, orden barajado
CORTE         el cierre de la vela envolvente. Ni un minuto después
SE ENSEÑA     de 00:00 hasta el corte, alto y mínimo de Asia, y nada más
SE GUARDA     el M1 posterior hasta el cierre de Londres, en fichero aparte
```

Reparto: 26 barridos del mínimo, 34 del alto. Cortes entre las 08:05 y las 13:30.

Los 60 se validan uno a uno (`velas[i_barrido]` cierra al otro lado del nivel,
la última vela envuelve por cuerpo a la anterior y va en contra, el gatillo cae
1 o 2 velas después del barrido): 0 incoherencias.

## Lo que el usuario responde

Por cada corte: **Opero** o **Paso**. Si opera: dirección, entrada, stop y
objetivo. Pasar cuenta igual que entrar — es la mitad de la información.

La fecha va tapada, con un botón para descubrirla. Se le pide expresamente que
la mire *después* de responder.

## Lo que se mide, y con qué se compara

Todo con `bt/resuelve_etiquetado.py`, coste 1,2 pips de spread sobre el riesgo.

| # | pregunta | cómo se contesta |
|---|---|---|
| 1 | ¿sus entradas ganan? | R neta media de lo que operó, contra cero |
| 2 | ¿su criterio para **elegir** aporta? | la regla mecánica sobre los que operó **menos** la regla mecánica sobre los que pasó |
| 3 | ¿su criterio para **colocar** aporta? | sus entradas **menos** la regla mecánica sobre esos mismos cortes |
| 4 | ¿hay algo más que geometría? | %TP observado contra `1/(1+R:R)` |

Las tres primeras son diferencias sobre los mismos cortes, así que no dependen
de si el patrón en sí sirve: aíslan lo que aporta él.

## Lo que esta prueba NO puede hacer

Con 60 cortes y una desviación por operación de ~1,2 R, el error típico ronda
**±0,15 R**. Eso significa que la baraja sólo distingue efectos grandes, del
orden de **+0,30 R por operación o más**. Una ventaja pequeña y real —del
tamaño que se ha visto en todo el proyecto, +0,05 a +0,10 R— pasaría por aquí
sin dejar señal.

Dicho claro: **esto no es un veredicto.** Es una calibración. Si sale muy
positivo, hay algo grande que la regla escrita no capturaba y merece una baraja
mayor. Si sale plano, no prueba que no haya nada: prueba que no hay nada
*grande*. Se dice ahora para no reinterpretarlo después.

## Umbrales, fijados ahora

- **Sigue la investigación** si (2) o (3) dan **≥ +0,30 R** con z ≥ 1,64.
  Entonces se genera una segunda baraja de 150 cortes con los años reservados.
- **Se archiva la familia** si (2) y (3) quedan entre −0,15 y +0,15 R.
- **Zona intermedia**: se amplía la baraja antes de concluir nada.

No se cambia ninguno de estos números después de ver las respuestas.

## Ficheros

```
bt/etiquetado_asia.py               construye la baraja
bt/resuelve_etiquetado.py           resuelve las respuestas
docs/etiquetado_asia.html           la página que ve el usuario (sin futuro dentro)
data/etiquetado_asia_setups.json    lo que se enseña
data/etiquetado_asia_verdad.csv     fechas y regla mecánica de cada corte
data/etiquetado_asia_camino.parquet el M1 posterior, 15.791 minutos
```
