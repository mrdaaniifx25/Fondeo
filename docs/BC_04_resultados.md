# BC · Resultados · **DESCARTADA**

> ⚠️ **Los números de este documento están obsoletos.** Ver
> [`BC_07_correcciones.md`](BC_07_correcciones.md): el motor tenía dos fallos y la
> máquina de estados no influía en nada de lo medido aquí. El veredicto —0 de 12
> celdas, doce medias recortadas en negativo— **se mantiene con el motor
> corregido**, pero la tabla de la sección 3 no es la buena.

Especificación `BC_02`, criterios `BC_03`. Una pasada, como estaba comprometido.

---

# 1 · La calibración no discriminó

Fase 1 (`BC_03` §3): fijar los parámetros libres contra **su relato**, sin mirar
resultados. Solo dos de sus operaciones caen dentro de los datos (terminan el
31-07-2026) y una de ellas sin dirección declarada.

| combinación | S&P 22-07 | NASDAQ 30-07 | aciertos |
|---|---|---|---|
| UTC · lectura A | no | **sí** | 1 |
| NY · lectura B | **sí** | no | 1 |
| las otras diez | no | no | 0 |

Máximo 1 de 2, con dos combinaciones empatadas **que reproducen casos
distintos**. Eso no es una calibración: es una moneda al aire con dos
lanzamientos. Se declara fallida.

Por tanto, según `BC_02` §11 fase 2, **se reporta la rejilla entera** y se dice
cuántas celdas se han probado: **doce**. Umbral honesto por Bonferroni,
|z| > 2,87.

## 1.1 · Un fallo propio, corregido

La primera versión comprobaba si el rango **nacía** ese día. Mi propio criterio
decía «existe un rango **activo**». Ellos son explícitos: «identificamos la
activación… lo que nos permitió **anticipar** el movimiento» — el contexto es
anterior. Corregido antes de seguir. Con la versión mala salían 0 de 12 y habría
declarado que la especificación no es su método, que habría sido falso.

# 2 · Guarda de ejecutabilidad, añadida al ver el riesgo

El primer barrido daba **R:R mediano 16,6, p90 77 y máximo 1198**, con riesgos
de 1,9 unidades. Un stop de 1,9 pips con 1,2 de coste no se puede operar, y esos
casos envenenan la media.

Se exige **stop ≥ 3× el coste**, aplicado igual a las doce celdas. Se declara
que se añadió después de ver la distribución de riesgo: es una corrección de
**validez**, no de rendimiento, y elimina operaciones tanto ganadoras como
perdedoras.

# 3 · La rejilla · desarrollo 2020-2023

| huso | lectura | n | ops/año | aciertos | R bruta | **R neta** | z | **neta recortada al 1 %** |
|---|---|---|---|---|---|---|---|---|
| UTC | A | 1.602 | 400 | 11,8 % | +0,280 | **+0,133** | +1,11 | **−0,008** |
| Broker | A | 1.605 | 401 | 11,8 % | +0,181 | +0,032 | +0,32 | −0,033 |
| Madrid | A | 1.584 | 396 | 11,6 % | +0,158 | +0,010 | +0,10 | −0,054 |
| Broker | B | 7.773 | 1.943 | 13,8 % | +0,084 | −0,054 | −1,47 | −0,117 |
| Madrid | B | 7.894 | 1.974 | 13,8 % | +0,079 | −0,059 | −1,60 | −0,119 |
| NY | A | 1.753 | 438 | 11,0 % | +0,082 | −0,066 | −0,68 | −0,171 |
| UTC | B | 7.597 | 1.899 | 14,2 % | +0,059 | −0,077 | −2,15 | −0,132 |
| NY | B | 7.834 | 1.958 | 13,5 % | +0,046 | −0,090 | −2,48 | −0,151 |
| NY | C | 377 | 94 | 9,5 % | +0,008 | −0,138 | −0,62 | −0,242 |
| Broker | C | 314 | 78 | 9,6 % | −0,063 | −0,211 | −0,97 | −0,308 |
| UTC | C | 405 | 101 | 9,9 % | −0,093 | −0,239 | −1,36 | −0,336 |
| Madrid | C | 326 | 82 | 9,5 % | −0,163 | −0,307 | −1,67 | −0,382 |

**Cero celdas de doce superan |z| > 2,87.** Ninguna supera siquiera el 1,96 sin
corregir. Las doce tienen n ≥ 100, así que la prueba está **adecuadamente
potenciada** (`BC_03` §4.1): no es que no se pueda ver, es que no hay.

## 3.1 · La columna que decide

**Recortando el 1 % superior, las doce celdas quedan negativas**, incluida la
mejor: +0,133 → **−0,008**.

Ese único punto positivo de toda la rejilla lo sostienen enteramente los veinte
mejores resultados de mil seiscientas operaciones. Con objetivos estructurales a
R:R mediano de 13, la media es una medida frágil: basta un puñado de
desplazamientos grandes para teñirla de positivo sin que haya ventaja.

# 4 · Controles  (`BC_03` §7)

**Dirección invertida**, resimulada de verdad —espejo del stop y del objetivo
alrededor de la misma entrada— sobre EURUSD, celda UTC+A, 246 operaciones:

```
tal cual     -0,247        invertida    -0,254
suma         -0,501        2x coste     -0,364
```

Las dos direcciones pierden y la suma es aproximadamente menos dos veces el
coste. Es exactamente lo que da una moneda al aire.

*Nota: la primera versión de este control daba +21,402 porque suponía que
invertir un perdedor lo convierte en ganador al mismo R:R. Al invertir, objetivo
y stop intercambian distancias. Corregido.*

**Sensibilidad al coste** (mejor celda): +0,280 sin coste, +0,133 al supuesto,
−0,015 al doble. Cruza el cero entre 1× y 2×.

**Año a año** (mejor celda): 2020 +0,681 · 2021 +0,336 · 2022 +0,055 · 2023
−0,019. Decae de forma monótona hasta apagarse.

# 5 · Lo secundario  (`BC_03` §6)

## 5.1 · El gradiente de liquidez: no existe

Su afirmación —doble y triple liquidez suben la probabilidad— resumida **por
celda**, que es como hay que hacerlo:

```
diferencia triple menos simple:  media +0,006 R   sd entre celdas 0,348
z tratando cada celda como una observacion:  +0,06
celdas con la diferencia positiva:  7 de 12
```

**Nada.** Y hay una lección de método aquí: agregando las 39.064 operaciones de
las doce celdas salía **+0,156 R con z = +3,74**, que parece un hallazgo. Pero
las celdas son **las mismas operaciones repetidas** con rejillas distintas. Ese
z estaba inflado por repeticiones no independientes. Es el segundo error de este
tipo que cometo esta semana; lo detecté porque el número era demasiado bonito.

## 5.2 · Las tres zonas de R:R: tampoco

Su gradiente —mejor R:R, mejor oportunidad— no aparece:

```
R:R 3-5    -0,074      R:R 10-25   -0,066
R:R 5-10   -0,043      R:R >25     -0,060
```

Plano y negativo en las cuatro bandas.

# 6 · Veredicto

El criterio principal de `BC_03` §4 exigía que el intervalo de confianza de la R
neta excluyera el cero por arriba. **Ninguna de las doce celdas lo cumple.**

**Descartada.** No se abre el conjunto de confirmación 2024-2026, que sigue
cerrado.

# 7 · Qué dice esto y qué NO dice

**Dice** que esta especificación —doce variantes de ella— no tiene ventaja neta
en cinco instrumentos entre 2020 y 2023, con muestra suficiente para verlo.

**No dice** que el método de bctrades no funcione. Y hay tres razones concretas,
no diplomacia:

1. **La calibración falló.** No pude confirmar que mi rejilla temporal sea la
   suya. Con solo dos operaciones fechadas y utilizables, no había con qué.
2. **Faltan piezas que ellos no publican**: cuándo no operan, el tamaño de
   posición, y las temporalidades de 8H y 2H que sí usan.

   **Actualización posterior a esta medición.** La regla de uso del reinicio,
   que aquí figuraba como no publicada, la mandaron por privado y está transcrita
   en `BC_01` §20. Cambia el disparo de entrada: no se entra cuando la
   temporalidad de ejecución **ya** coincide con las mayores, sino cuando pasa
   **de estar en contra a coincidir** — un disparo de transición, no de estado.
   Mi motor solo miraba el estado. Esta medición, por tanto, contrastó una
   especificación incompleta. No se rehace aquí: el pre-registro comprometía una
   sola pasada y reabrirlo sería reajustar. La regla nueva necesita su propio
   pre-registro.
3. **Toda la parte discrecional queda fuera**, por definición.

De lo que sí se puede responder: la rejilla temporal la puse yo entre cuatro
opciones, el stop es lectura del usuario, y el objetivo más cercano entre varios
alineados fue decisión mía —la conservadora—. Si algo de eso está mal, el
resultado mide otra cosa.

Lo que queda medido sin ambigüedad, porque no depende de ninguna de esas
elecciones, es lo del punto 5: **las dos afirmaciones con gradiente que ellos
hacen —doble/triple liquidez y las tres zonas de R:R— no aparecen en ninguna de
las doce rejillas.**

# 8 · Reproducir

`bc/nucleo.py`, `bc/motor.py`, `bc/calibra.py`, `bc/run_rejilla.py`.
