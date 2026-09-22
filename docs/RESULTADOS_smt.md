# Resultados · divergencia SMT entre instrumentos

Pre-registro: `docs/PREREGISTRO_smt.md`, subido **antes** de medir.
Código: `bt/smt.py`. EURUSD, DAX y oro en M1, 2023-2026.

## Veredicto

**No aporta nada.** Y es el experimento más limpio de todo el proyecto, porque
los dos brazos son la misma operación con la misma geometría: la diferencia no
depende de que el barrido esté bien valorado.

## El principal declarado · EURUSD, socio DAX, R:R 2

```
  A · con divergencia   n 455   acierto 34,9 %
  B · sin divergencia   n 465   acierto 31,6 %       azar 33,3 %
  DIFERENCIA  +3,3 puntos  [-2,8, +9,4]      neta +0,1104 [-0,0738, +0,2947]
```

El intervalo toca el cero. Con 455 por brazo el error estándar de la diferencia
es de 3,1 puntos: **+3,3 es t = 1,06**, que es ruido.

## La ampliación que declaré antes de medir

El pre-registro decía: *«habría que replicarlo cambiando el instrumento operado
antes de creérselo»*. Es además la única forma de ganar muestra. Las seis
combinaciones:

```
  operado / socio            A  acierto      B  acierto    DIFERENCIA
  EURUSD / DAX            455   34,9 %    465   31,6 %        +3,3
  EURUSD / oro            731   33,7 %    585   32,5 %        +1,2
  DAX    / EURUSD         534   31,8 %    438   32,4 %        -0,6
  DAX    / oro            629   32,0 %    343   32,4 %        -0,4
  oro    / EURUSD         486   30,9 %    661   34,2 %        -3,3
  oro    / DAX            382   36,4 %    413   29,5 %        +6,8   <- "pasa"
  ─────────────────────────────────────────────────────────────────
  LAS SEIS JUNTAS       3.217   33,1 %  2.905   32,3 %        +0,8
```

**Juntas: +0,82 puntos, t = +0,68.** Con 3.217 contra 2.905 operaciones.

Y la fila de arriba es la mejor ilustración que ha dado este proyecto de por qué
una casilla suelta no significa nada: **seis combinaciones de la misma idea,
esparcidas de −3,3 a +6,8**. La que «pasa» (oro/DAX, +6,8 con el intervalo
limpio) es la mejor de seis —que por azar regala +4— y su gemela con el otro
socio da −3,3.

Para resolver una diferencia del tamaño de la medida harían falta unas
**52.000 operaciones por brazo**. Hay 3.217.

## Contra el criterio pre-registrado

| criterio | resultado |
|---|---|
| 1. A − B > 0 con el IC limpio en el principal | **NO.** +3,3 [−2,8, +9,4] |
| 2. mismo signo con el otro socio | +1,2, mismo signo pero un tercio del tamaño |
| 3. mismo signo partido en dos mitades | sí: +2,9 y +3,8, los dos con el cero dentro |

Falla el primero, y la ampliación a las seis combinaciones lo cierra: **+0,8
puntos con t = 0,68.**

## Récord de predicciones

Dos de tres.

| predicción | resultado |
|---|---|
| A y B iguales, diferencia entre −3 y +3 | juntas **+0,8** ✔ |
| 100-300 operaciones por brazo con el DAX | 455 y 465 ✘, más de las esperadas |
| el criterio no se cumplirá | no se cumple ✔ |

## Qué cierra esto

Era la última idea de los tres operadores que quedaba sin medir, y la única que
no era un patrón de un solo gráfico. Con ella queda cerrado **todo** el
contenido técnico de los vídeos:

| idea | dónde está medida |
|---|---|
| barrido de liquidez de sesión | `RESULTADOS_barrido_sesion_v2.md` |
| niveles de sesión vivos de días anteriores | `RESULTADOS_liquidez_sesiones.md` |
| PDH / PDL / PSH / PSL + cadena H4-H1-M5 | `RESULTADOS_liquidez_sesiones_v2.md` |
| FVG y AMD | `CORRECCION_objetivo_rebasado.md` |
| order block, breaker | `RESULTADOS_ob_*.md` |
| 50 % del rango de Asia | `RESULTADOS_asia_*.md` |
| stop diminuto + R:R 1:12 o más | `RESULTADOS_rr_extremo.md` |
| contexto de marcos superiores | `RESULTADOS_techo_filtro.md` |
| **divergencia SMT entre instrumentos** | **este documento** |
