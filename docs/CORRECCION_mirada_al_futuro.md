# Corrección · el filtro de contexto leía el futuro

Encontrado el 28 de agosto de 2026, al revisar por qué un resultado salía
demasiado bueno. Afecta a todo lo publicado sobre H1 y M15.

## El fallo

```python
# lo que hacía (mal)
idx = serie.index.searchsorted(ts, side="left") - 1
```

El índice de las series de H1 y M15 son horas de **apertura**. Para una decisión
a las 09:20, esa línea devolvía la vela de H1 que **empieza** a las 09:00 — una
vela que no cierra hasta las 10:00. Leía su cierre, es decir, **40 minutos de
futuro**. Hasta 59 en H1 y 14 en M15.

```python
# lo correcto
idx = serie.index.searchsorted(ts - duración_de_la_vela, side="right") - 1
```

Arreglado en `bt/asia_contexto.py` y en `bt/simulador_resuelve.py`.

## Qué cambia · el filtro de contexto

**Lo que publiqué:**

```
2020-2025            n      %TP     neta/d       z
  M15 y H1 a favor  1.454   34,9%   -0,104
  el resto            626   21,2%   -1,014
  DIFERENCIA                        +0,910   +11,19
```

**Lo que sale al arreglarlo:**

```
2020-2025            n      %TP     neta/d       z
  M15 y H1 a favor    938   32,2%   -0,273
  el resto          1.142   29,7%   -0,484
  DIFERENCIA                        +0,211    +2,97
```

**El 18,6 % contra 34,8 % de H1 era el error, no el mercado.** Con el arreglo,
H1 a favor acierta el 30,8 % y H1 en contra el 30,8 %: exactamente lo mismo.

El contraste preregistrado **sobrevive, pero pequeño**: el combinado da z +2,97
contra el umbral de 2,39 de Bonferroni, y H1 por su cuenta se queda en +2,32, o
sea que ya no pasa. Y la diferencia que queda no viene del acierto sino del
tamaño del riesgo. En enero-mayo de 2026 (118 disparos) sigue saliendo: +2,80.

## Qué cambia · el invertido

Lo que parecía el mejor hallazgo del proyecto:

```
  con el error:  626 disparos · 51,3 % de acierto · suma neta/día +0,450 · z +6,47
  arreglado:   1.142 disparos · 36,1 % de acierto · suma neta/día -0,056 · z -1,03
```

**Muerto.** El 50 % de acierto era enteramente la mirada al futuro. La mejor
celda de las doce probadas se queda en −0,007 de suma neta por día, z −0,14.

El contraste preregistrado de `bt/asia_invertido.py` había fallado ya con el
error dentro (z −1,10); ahora falla igual y sin ambigüedad.

## Qué cambia · el simulador

El corte por contexto de sus 49 decisiones también estaba mal:

```
  publicado:   a favor 23 entradas · 35 % · el resto 25 · 24 %
  corregido:   a favor 17 entradas · 35 % · el resto 31 · 26 %
```

El resultado principal **no cambia**: 14 TP de 48, acierto 29,2 %, p = 0,776.
Eso se resolvía con datos M1 y no tocaba la función rota.

El corte post hoc de «las dos reglas» pasa de 14 entradas (43 %, +0,179) a
**9 entradas (56 %, +0,524)**. Con nueve operaciones eso no es nada.

## Qué queda en pie

- El coste real de 1,43 pips, y que se come la ventaja de cualquier operación
  con stops de 3-8 pips. Nada de esto dependía de H1.
- Que la regla mecánica no tiene ventaja: 30,8 % sobre 2.080 disparos.
- Que su agosto no se sostiene como prueba, y que en el simulador a ciegas
  acertó el 29,2 % en 48 entradas.
- El filtro de contexto, **pero como un efecto pequeño**: z +2,97, sin diferencia
  de acierto en 2020-2025.

## Lo que hay que rehacer

- `docs/RESULTADOS_asia_contexto.md`: los números están mal.
- `docs/RESULTADOS_asia_ancho.md`: partía del conjunto filtrado con el error.
- `paginas/protocolo_manana.html`: dice «a favor de H1 acierta el 34,8 %, en
  contra el 18,6 %». Falso.
