# Resultados · la base de Benjamín, con las tres vueltas

Pre-registro `8f281ba`, subido antes de medir. Código `bt/benjamin_v3.py`.
EURUSD 5,7 años. Se conservan sus niveles, sus horarios y su disparo; se
cambian la temporalidad de entrada, el stop y el objetivo.

## Veredicto

**Las doce celdas siguen en negativo.** La mejor es **−0,049**, todavía lejos
del **+0,05** que necesita su plan.

| celda | n | acierto | azar | exceso | R:R | riesgo | coste | bruta | **NETA** |
|---|---|---|---|---|---|---|---|---|---|
| M15 · barrido · 1:2 | 19 095 | 33,0 | 33,3 | −0,3 | 2,00 | 16,5 p | 8,7 % | −0,009 | −0,109 |
| **M15 · barrido · opuesto** | 19 075 | 79,2 | 78,2 | **+1,0** | 0,19 | 16,5 p | 8,7 % | +0,007 | −0,094 |
| M15 · atr1 · opuesto | 19 075 | 79,4 | 78,4 | **+1,0** | 0,19 | 16,5 p | 8,7 % | +0,009 | −0,089 |
| **M15 · atr1,5 · opuesto** | 19 075 | 80,0 | 79,0 | **+1,0** | 0,19 | 16,9 p | 8,5 % | +0,009 | −0,084 |
| H1 · barrido · 1:2 | 5 574 | 25,0 | 33,3 | **−8,4** | 2,00 | 29,3 p | 4,9 % | −0,251 | −0,309 |
| H1 · atr1 · opuesto | 5 513 | 84,6 | 84,4 | +0,2 | 0,11 | 29,1 p | 4,9 % | +0,002 | −0,053 |
| **H1 · atr1,5 · opuesto** | 5 513 | 85,4 | 85,2 | +0,3 | 0,11 | 29,8 p | 4,8 % | +0,002 | **−0,049** |

## Lo que sí aparece

**Con el objetivo en el nivel opuesto hay exceso positivo y significativo en
M15: +1,0 punto** [+0,5, +1,5], sobre 19.075 operaciones. Es pequeño pero no es
cero, y sobrevive a las tres variantes de stop.

**El objetivo de 1:2 fijo es lo que mata la regla.** En H1 da **−8,4** de
exceso: ocho puntos **por debajo** del azar. Apuntar a un múltiplo arbitrario
en vez de a un nivel real no es neutro, es activamente malo.

## Y por qué el +1,0 no salva nada

Con el objetivo en el nivel opuesto más cercano, el **R:R cae a 0,11-0,19**. Se
acierta el 80-85 %, pero se gana una miseria cada vez.

```
coste sobre el RIESGO     4,8 %
coste sobre el PREMIO     4,8 / 11 = 44 %
```

Casi la mitad de lo que intentas ganar se lo lleva el coste. Por eso un exceso
de +1,0 punto no llega: **el premio es demasiado pequeño para pagar el peaje.**

## Sus horarios: aportan, y poco

| | n | exceso | riesgo | **neta** |
|---|---|---|---|---|
| M15 · sus horarios | 19 075 | +1,0 | 16,9 p | **−0,084** |
| M15 · todo el día | 42 504 | +0,6 | 11,2 p | −0,134 |
| H1 · sus horarios | 5 513 | +0,3 | 29,8 p | **−0,049** |
| H1 · todo el día | 23 935 | +0,3 | 25,7 p | −0,054 |

En M15 sus horas mejoran de −0,134 a −0,084 — **pero otra vez por el stop**
(16,9 pips contra 11,2), no por el exceso. En H1, donde el stop ya es ancho,
la diferencia **desaparece** (−0,049 contra −0,054).

**Su filtro horario es un sustituto pobre de ensanchar el stop.** Cuando el
stop ya es ancho, no aporta nada.

## Mi predicción: 3 de 5

| predije | salió |
|---|---|
| bruta +0,05 a +0,12 con objetivo opuesto | ❌ **+0,000 a +0,009**, diez veces menos |
| bruta en cero con 1:2 | ✅ en M15 · ❌ en H1 (−0,25) |
| el stop por ATR mejorará la neta | ✅ poco, pero sí |
| neta entre −0,05 y +0,06 en las mejores | ✅ la mejor es −0,049 |
| sus horarios no mejorarán | ❌ **sí mejoran**, vía el stop |

## Lo que cierra y lo que abre

**Cierra**: la estrategia de Benjamín, en sus catorce celdas originales y en
estas doce modificadas. Veintiséis celdas, 5,7 años. No hay versión de ella que
cruce.

**Abre**: el objetivo en el nivel opuesto **sí tiene exceso medible** (+1,0 en
M15). Lo que falta no es acierto, es **premio**. Un objetivo más lejano con el
mismo exceso sí cruzaría. Es lo que hace el CRT desnudo, que apunta al extremo
opuesto del rango barrido y da R:R ~1,0-1,4 con bruta +0,087.

**La dirección sigue siendo la misma de siempre: stop ancho y objetivo lejos.**
