# Resultados · buscar donde el coste permite que exista algo

Preregistrado en `docs/PREREGISTRO_escala_diaria.md`. Una sola pasada, nueve
celdas, siete instrumentos, 8.341 operaciones.

```
bt/muro_del_coste.py    la cuenta que explica los dos meses
bt/escala_diaria.py     el contraste principal
bt/escala_diaria2.py    los secundarios declarados
```

## El contraste principal

| regla | k | n | acierto | geom | dif | stop | c/s | R neta | z | signo | c\* |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A barrido diario | 1 | 1444 | 47,5 % | 50,0 % | **−2,5 pt** | 64 | 2,9 % | −0,083 | **−3,17** | 6/7 | −2,44 |
| A | 2 | 1281 | 30,7 % | 33,3 % | −2,7 pt | 65 | 2,9 % | −0,104 | −2,68 | 6/7 | −3,48 |
| A | 3 | 1157 | 22,5 % | 25,0 % | −2,5 pt | 66 | 2,9 % | −0,100 | −2,04 | 5/7 | −3,45 |
| **B Donchian 20** | **1** | **422** | **53,9 %** | 50,0 % | **+3,9 pt** | 352 | **0,5 %** | **+0,063** | **+1,68** | 5/7 | **22,01** |
| B | 2 | 398 | 13,2 % | 33,3 % | −20,2 pt | 343 | 0,5 % | +0,011 | +0,26 | 4/7 | 4,96 |
| B | 3 | 398 | 5,7 % | 25,0 % | −19,3 pt | 343 | 0,5 % | +0,018 | +0,40 | 4/7 | 7,04 |
| C ruptura de ayer | 1 | 1366 | 51,9 % | 50,0 % | +1,9 pt | 148 | 1,3 % | +0,022 | +0,84 | 6/7 | 4,17 |
| C | 2 | 1001 | 29,4 % | 33,3 % | −3,9 pt | 146 | 1,3 % | −0,036 | −0,87 | 5/7 | −2,76 |
| C | 3 | 874 | 18,2 % | 25,0 % | −6,8 pt | 146 | 1,3 % | −0,008 | −0,17 | 4/7 | 0,47 |

Hacía falta |z| > 2,77 y signo en 5 de 7. **Ninguna celda lo pasa en positivo.**

## Lo que sí cambió, y es lo importante

Los nueve z están entre **−3,17 y +1,68**. Todo lo anterior del proyecto salía
entre −6 y −13. Es exactamente lo que firmé en la predicción 4: *fallará, pero
fallará por poco, y ese cambio de magnitud es en sí el hallazgo*.

Y mírese la columna `c*`, el coste al que cada celda llegaría a cero:

```
todo lo medido a escala de M5   coste de equilibrio 0,4 - 1,5 p   (el real es 1,43)
B Donchian 20 con k = 1         coste de equilibrio 22,0 p        (el real es ~1,4)
```

**Por primera vez en el proyecto hay una regla con quince veces de margen sobre
el coste.** El muro era el problema, no las ideas.

## Regla A: su CRT, a escala de día, pierde de forma significativa

Barrer el extremo del día anterior y cerrar dentro de su cuerpo, y entrar en
contra: **−2,5 puntos por debajo de la geometría, con el mismo signo en k = 1, 2
y 3 y en 6 de los 7 instrumentos.** z = −3,17.

Mi predicción 1 decía que saldría en la geometría. **Estaba equivocada**: sale
por debajo, y de forma consistente.

Eso significa que ir **a favor** del barrido gana en bruto. Pero no se puede
cobrar:

```
A k=1 tal cual      R neta -0,083   z -3,17
A k=1 invertida     R neta +0,020   z +0,76   NO pasa
```

Invertir no devuelve el signo cambiado, porque el coste se resta en las dos
direcciones. La asimetría es 2·c/s = 0,063 R, y se come casi todo lo que había.
**Es información, no una operación.**

## Regla B: el candidato, con dos problemas

| instrumento | n | acierto | stop | c/s | R neta | z |
|---|---|---|---|---|---|---|
| NSXUSD | 68 | 64,7 % | 953 | 0,2 % | +0,194 | +2,05 |
| USDJPY | 65 | 64,7 % | 339 | 0,4 % | +0,164 | +1,69 |
| XAUUSD | 40 | 60,9 % | 1447 | 0,3 % | +0,078 | +0,60 |
| SPXUSD | 70 | 48,4 % | 231 | 0,3 % | +0,060 | +0,66 |
| EURUSD | 71 | 45,2 % | 239 | 0,6 % | +0,019 | +0,21 |
| GBPUSD | 71 | 43,8 % | 315 | 0,6 % | −0,047 | −0,52 |
| GRXEUR | 37 | 47,4 % | 832 | 0,2 % | −0,066 | −0,50 |

**Problema 1 · el tope de 20 días es mío y aprieta.** El 51,7 % de las
operaciones de B mueren de viejas en vez de resolverse. El acierto del 53,9 % es
sobre el 48 % que sí resuelve. El Donchian clásico no lleva tope de tiempo: lleva
salida por seguimiento. Lo que se ha medido no es exactamente la regla que la
literatura respalda.

**Problema 2 · va demasiado despacio para lo que él necesita.**

```
65 operaciones al año en los siete instrumentos juntos
+0,063 R por operacion  ->  +4,1 R al ano

  al 0,5 % de riesgo:  +2,1 % al ano   ·  peor caida  5,7 %
  al 1,0 % de riesgo:  +4,1 % al ano   ·  peor caida 11,4 %
  al 2,0 % de riesgo:  +8,2 % al ano   ·  peor caida 22,8 %
```

El reto pide **+8 %** con un tope de pérdida del **10 %**. Al riesgo que permite
sobrevivir a la peor caída, la regla renta la cuarta parte de lo que hace falta.
Y al riesgo que llega al objetivo, la peor caída histórica revienta la cuenta dos
veces.

**Problema 3 · demostrarlo llevaría décadas.** De z = +1,68 a z = +2,77 hacen
falta 2,7 veces la muestra: unos diecisiete años de los siete instrumentos, o
tres veces más instrumentos.

## Las cinco predicciones

| | | |
|---|---|---|
| 1 · A saldrá en la geometría | **falla**: sale −2,5 pt, z −3,17 | ✗ |
| 2 · B será la mejor y k=1 la única con opciones | acierta | ✓ |
| 3 · C saldrá negativa entre −0,05 y −0,20 | **falla**: C k=1 sale +0,022 | ✗ |
| 4 · ninguna celda llegará a z > 2,77, pero fallará por poco | acierta las dos partes | ✓ |
| 5 · todas a menos de 2 pt de su geometría | **falla**: B +3,9, A −2,5 | ✗ |

Tres de cinco fallidas. La que importaba —la 4— acierta entera.

## Lo que esto deja escrito

1. **El muro del coste explica los dos meses.** Con stops de 3 a 10 pips hacían
   falta entre 5 y 16 puntos sobre la geometría y el mejor resultado del proyecto
   fue +4,1. No era falta de ideas.
2. **A escala diaria el muro casi desaparece** (0,2-2,9 % del riesgo) y aparece
   por primera vez una regla con margen real sobre el coste.
3. **Pero lo que hay ahí es pequeño y lento.** +0,063 R por operación y 65
   operaciones al año no financian un reto del 8 %.
4. **Lo único medido en este proyecto que es lo bastante grande sigue siendo él**:
   +0,731 R por operación en 150 operaciones, con el intervalo de confianza
   entero por encima del equilibrio.

La conclusión incómoda es que la búsqueda de una regla mecánica ha sido honesta y
exhaustiva —más de cien celdas, cinco familias, dos escalas de tiempo, siete
instrumentos— y lo que ha encontrado no da de comer. Lo que da de comer, si
sobrevive al directo, es lo que hace él.
