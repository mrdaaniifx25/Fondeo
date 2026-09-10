# Preregistro · la misma señal, ocho stops distintos

Escrito antes de correr `bt/regla_stops.py`. Un solo pase.

## Por qué

`RESULTADOS_asia_nivel.md` ya corrió **su regla**, y él acaba de confirmar la
pieza que faltaba: **entra al cierre de la vela de M5**. Coincide. Así que la
señal está bien modelada y su veredicto —30,8 % de acierto contra 33,3 %
geométrico— se sostiene.

Pero aquel pase puso el stop en **el extremo de la vela de M5 anterior**, y salió
un riesgo mediano de **7,0 pips**. Los suyos reales son de **2,8 a 5**, porque no
lo pone sobre M5: lo pone sobre la estructura de **M1**. Esa diferencia nunca se
ha medido, y es justo lo que él sostiene que falla: *«creo que el problema está
en los ajustes del SL y del TP»*.

## Qué se hace

Las **mismas señales** de `bt/asia_nivel.py`, sin tocar una coma: niveles de Asia
00:00-08:00 hora de Madrid, ventana 08:00-11:30, gatillos A y B, armado y
rearme a 10 pips, entrada al cierre de la vela de M5.

Lo único que cambia es **dónde va el stop**. Ocho variantes:

| | stop |
|---|---|
| `M5 anterior` | extremo de la vela M5 anterior a la entrada — el del pase original |
| `M5 señal` | extremo de la propia vela que dispara |
| `M1 ×1` | extremo de la última vela M1 cerrada |
| `M1 ×3` | extremo de las tres últimas M1 cerradas — **lo que él hace** |
| `fijo 3p` · `fijo 5p` · `fijo 8p` · `fijo 20p` | distancia fija |

Objetivo siempre **1:2 desde la entrada**. Coste **1,43 pips**. Resolución en M1
hasta las 22:00 del mismo día.

## La lectura principal

Para cada variante, el **acierto bruto contra el 33,3 % de la geometría**.

Es la única comparación que aísla lo que aporta la entrada. Un stop más estrecho
tiene por fuerza más R y menos acierto: eso es aritmética, no ventaja. Lo que
importa es si el acierto se desvía de lo que la geometría predice:

- **Igual al 33,3 % en todas las anchuras** → la entrada no aporta información, y
  entonces la neta es simplemente `geometría − coste/riesgo`, que mejora al
  ensanchar el stop y nunca cruza el cero.
- **Por debajo del 33,3 % en los estrechos** → el precio se va en contra antes de
  ir a favor, y el stop pegado hace daño **más allá** del coste.
- **Por encima del 33,3 % en los estrechos** → su momento de entrada tiene
  información de verdad, y ahí sí habría algo que perseguir.

Métrica secundaria: R neta por operación y su z, con umbral Bonferroni para ocho
variantes: **|z| > 2,73**.

## Predicción firmada

1. La **R neta sube de forma monótona al ensanchar el stop**, y ninguna anchura
   la pone en positivo.
2. `M1 ×3` —el suyo— será **la peor de las ocho**.
3. El acierto quedará **en o por debajo del 33,3 %** en todas, sin que ninguna lo
   supere de forma significativa.
4. El coste sobre el riesgo pasará del 40 % en `M1 ×1` y `M1 ×3`.

Si aparece un máximo en el medio, o si los estrechos baten al 33,3 %, la
predicción está mal y eso es el hallazgo.
