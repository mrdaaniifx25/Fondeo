# Su regla, tal y como la describe él · en construcción

Documento vivo. Se va llenando con lo que él va contando sobre sus propias
capturas, **antes** de codificar nada. La lista de hipótesis que salga de aquí
es suya, no mía, y ésa es la diferencia con los dos meses anteriores.

Fecha de arranque: 10 de septiembre de 2026.

## La secuencia, en sus palabras

> «rotura del high de Asia, luego hace un retroceso y cuando la vela cierra con
> cuerpo por debajo del último mínimo ejecuto entrada»

```
1. el precio rompe el máximo de Asia            -> se lleva la liquidez
2. sigue y hace un máximo
3. retrocede
4. una vela CIERRA CON CUERPO por debajo del
   último mínimo relevante                      -> rotura de estructura
5. entrada en ese cierre, vendiendo
```

## Los tres ejemplos que ha enseñado

Todos EURUSD M1, ventana de Londres, y **los tres son ventas**.

| # | día | máximo previo | último mínimo = entrada | stop | objetivo | riesgo |
|---|---|---|---|---|---|---|
| 1 | 10 sep | 1,16443 (09:35) | **1,16387** (09:50) | 1,16415 | 1,16330 | 2,8 p |
| 2 | 10 sep | 1,16525 (09:45) | **1,16375** (10:05) | 1,16418 | 1,16310 | 4,3 p |
| 3 | 08 sep | 1,16360 (08:05) | **1,16303** (08:15) | 1,16340 | 1,16229 | 3,7 p |

## Lo que se deduce, pendiente de que él lo confirme

**El «último mínimo» es un mínimo de estructura, no el de la vela anterior.**
Es el suelo desde el que arrancó el último tramo al alza. En el ejemplo 2 son
las 09:30 (1,16375) y el tramo llega hasta 1,16525 quince minutos después.
Descartadas las otras dos lecturas que se le ofrecieron (mínimo de la última M5,
mínimo de la última M1).

**El stop parece ir encima del último máximo menor anterior a la entrada**, no
encima del máximo grande. Encaja en los tres: 1,16415 con máximo grande en
1,16443; 1,16418 con máximo grande en 1,16525; 1,16340 con máximo grande en
1,16360. Sin confirmar.

**La rotura del máximo de Asia puede ocurrir antes de las 08:00.** En el ejemplo
3 el precio ya está por encima de la caja de Asia cuando abre Londres, y la
entrada llega a las 08:15. Así que el barrido no tiene que caer dentro de la
ventana operativa; la entrada sí.

## Lo que hace falta antes de medir

1. **Definir «último mínimo» con un número.** Propuesta: mínimo más bajo que las
   N velas anteriores y las N posteriores. En sus capturas N parece estar entre
   5 y 10 minutos. Se probará un rango y se declarará una celda principal.
2. **Causalidad.** Un mínimo así no queda confirmado hasta N velas después de
   ocurrir. Sólo se usarán los confirmados **antes** de la vela de entrada. Este
   repositorio ya se ha tropezado dos veces con miradas al futuro
   (`CORRECCION_mirada_al_futuro.md`) y no habrá una tercera.
3. **Falta un ejemplo de compra.** Los tres son ventas tras barrer por arriba.
   Sin un caso simétrico no se puede saber si la regla es simétrica o si lo que
   describe es sólo el lado corto.

## Lo que ya se puede anticipar

Los riesgos de los tres ejemplos son **2,8 · 4,3 · 3,7 pips**. Con el coste
medido de 1,43 pips, el peaje es del 51 %, 33 % y 39 % del riesgo. Su regla
real produce stops pequeños, igual que la anterior, así que la aritmética del
coste va a volver a aparecer. Se reportarán por separado la ventaja bruta del
patrón y lo que se lleva el coste.

## Primer intento de codificarla, y lo que enseñó

`bt/regla_suya_v1.py`. Máximo/mínimo de Asia, origen del impulso que lo rompe
(se anda hacia atrás desde la vela de rotura mientras aparezcan mínimos más
bajos, parando tras K velas sin uno nuevo), y entrada cuando una vela cierra con
cuerpo al otro lado. K = 3, pivote del stop P = 2.

Contrastado contra sus 12 días de agosto con datos:

| día | él | la regla codificada |
|---|---|---|
| 04 ago | venta | 10:25 venta ✓ |
| 05 ago | venta + compra | 10:45 venta ✓ |
| 07 ago | compra | 10:46 compra ✓ |
| 18 ago | compra + compra | 09:26 compra ✓ |
| **14 ago** | **compra** | **08:22 venta ✗** |
| **17 ago** | **compra** | **08:09 venta ✗** |
| 03, 06, 10, 11, 19, 20 | operó | no dispara |

**Acierta el lado en 4 de 6 y no dispara en la mitad de los días.** No es su
regla todavía.

Tres fallos identificados:

1. **El 14 y el 17 él compra donde el código vende.** Esos dos días el máximo de
   Asia se rompe a las 08:00 y el precio **continúa** subiendo. Él se sube al
   movimiento en vez de esperar el giro. Es exactamente lo que él mismo avisó:
   *«lo peligroso es que puede ser o rotura y continuación o rotura y rebote»*.
   Si opera las dos, la regla no es «barrido y giro»: es «se rompe un nivel y
   luego la estructura dice hacia dónde».
2. **Sólo coge la primera rotura del día por lado.** Él toma de una a tres
   operaciones diarias; probablemente hay segundos impulsos que rompen niveles
   nuevos más tarde.
3. **Las horas no cuadran.** El 4 de agosto él entra a las 09:30 y el código a
   las 10:25. Mismo lado, distinta operación.

En el 14 de agosto se ve además una figura que no estaba en la conversación:
el precio rompe el máximo de Asia a las 08:00, **vuelve a caer por debajo**
hasta las 08:55, lo **recupera**, y él compra a las 09:40. Rotura fallida y
reconquista. Pendiente de que él confirme si es eso lo que miraba.

## Segundo intento: la carrera entre el origen y el pico

Él confirma que **opera también las continuaciones**, así que la regla se
reescribe simétrica y sin adivinar nada (`bt/regla_suya_v2.py`):

```
se rompe el nivel de Asia -> el impulso deja un origen L y un pico P
    cierre con cuerpo por debajo de L  ->  la rotura falló    ->  VENTA
    cierre con cuerpo por encima de P  ->  la rotura aguantó  ->  COMPRA
gana el primero que ocurra
```

989 entradas en 2020-2026, riesgo mediano 6,5 pips, 342 giros y 647
continuaciones. Contra sus 12 días de agosto: **coincide el lado en 3 de 6 días
en que dispara.** Peor que la v1, que daba 4 de 6.

Y los tres desacuerdos tienen la misma forma: **el código vende y él compra**,
los tres en días en que el máximo de Asia se rompe pronto y el precio sube toda
la mañana (14, 17 y 18 de agosto).

## Los atajos de tendencia tampoco lo explican

Por si la estructura fina no era lo que mandaba, se comprueba si su dirección
coincide simplemente con la del día:

| proxy | coincide con su lado |
|---|---|
| dirección desde el cierre de Asia | 62 % (8 de 13) |
| dirección de la vela de 4h previa | 69 % (9 de 13) |
| por encima/debajo de la mitad del rango de Asia | 62 % (8 de 13) |
| dirección de los 30 min antes de entrar | 62 % (8 de 13) |

Con n = 13, el 69 % no se distingue del azar.

## Dónde queda esto

**Tres intentos de deducir su regla y ninguno converge.** Con 13 operaciones no
se demuestra nada —puede ser ruido—, pero sí queda claro que no va a salir por
deducción, y seguir probando variantes propias es el error de los dos meses
anteriores repetido con otros datos.

La lectura honesta, sin adornos: si sus entradas se reprodujeran con una regla
sencilla, esa regla se habría medido sobre seis años y casi con seguridad habría
salido negativa como todo lo demás. **Que no se reduzcan a una regla es
compatible con que haya algo en su criterio** — no lo demuestra, porque sigue sin
medirse, pero tampoco lo refuta.

Los dos caminos que quedan, y los dos evitan que yo siga adivinando:

1. Que narre **un día entero** paso a paso, en vez de describir la regla en
   abstracto.
2. Dejar de codificar y medir **al lector** directamente:
   `PREREGISTRO_criterio.md` (300 etiquetas a ciegas, escrito y nunca ejecutado)
   o el registro hacia delante.

## Tercer intento: escrito desde sus propias palabras

Se le pidió que narrara el 14 de agosto momento a momento, en un artefacto con
una caja por cada hito. Lo que contestó, literal:

| momento | lo que dijo |
|---|---|
| 08:00 · rompe Asia | «la vela que rompe deja mecha durante 2 velas consecutivas… la siguiente ya es bajista y espero a ver cómo reacciona el precio, **aquí no haría entrada**» |
| 08:26 · 3,7 p por debajo | «aquí ya empezaría a pensar en **compras** en el momento que el movimiento alcista [rompa] el **último alto** que hay entre las 8 y las 8:30» |
| 08:45 · recupera el nivel | «cierra por encima pero con **poco cuerpo**… esperaría a que el precio cerrase con alguna **vela alcista con cuerpo** por encima del nivel» |
| 09:40 · compra | «rompe el **último alto del movimiento alcista** entre las 9 y 9:30» |

Tres cosas que no estaban en ninguna versión anterior del código:

1. **Distingue romper con mecha de romper con cuerpo**, y aun con cuerpo espera
   si la vela siguiente va en contra.
2. **En el momento 2, con el precio por debajo del nivel, ya está pensando en
   COMPRAS.** Justo donde el código v2 vendía.
3. **El nivel de Asia no dispara nada.** Sólo enciende la alarma. El disparo es
   siempre una vela con cuerpo que rompe **el último pivote de la estructura
   reciente**.

`bt/regla_suya_v3.py` codifica exactamente eso: la rotura de Asia arma la
vigilancia, se siguen los pivotes causales de 3 velas a cada lado, y entra la
primera vela cuyo cuerpo (≥ 40 % del rango) cierra más allá del último pivote,
en la dirección de esa rotura.

Dispara los 12 días. **Coincide el lado en 6 de 12.**

## El resultado de los cuatro intentos

| intento | de dónde salía | acierta el lado |
|---|---|---|
| v1 · origen del impulso | de sus capturas | 4 de 6 (67 %) |
| v2 · carrera origen/pico | de «también hago continuaciones» | 3 de 6 (50 %) |
| dirección según el extremo de Asia roto | hipótesis propia | 7 de 13 (54 %) |
| v3 · rotura con cuerpo del último pivote | **de sus propias palabras** | 6 de 12 (50 %) |

Cuatro formulaciones independientes, una de ellas escrita directamente desde su
narración paso a paso de una operación concreta, y **ninguna supera al azar en
acertar su dirección**.

## Lo que eso dice, y lo que no

**No dice que opere mal.** Dice que la descripción **no determina la decisión**.
Las palabras que usa —«rompe el último alto con cuerpo»— describen *cómo* entra,
pero no *qué* pivote mira ni *cuándo* decide que ése es el bueno. En cualquier
mañana hay varios pivotes y varias roturas con cuerpo; la regla, tal como se
puede escribir, no elige entre ellas. Lo que elige es él, y eso no está en la
descripción.

Es lo normal en cualquier oficio: el criterio experto casi nunca es accesible a
la introspección. Él cree que sigue esas reglas, y las sigue — pero las reglas
dejan grados de libertad que rellena con algo que no sabe nombrar.

**Y aquí está lo importante, que va justo al revés de como suena:** si su
descripción fuera completa, se habría codificado, se habría medido sobre seis
años y —visto todo lo demás de este repositorio— habría salido negativa. Que sus
decisiones contengan algo que la descripción no captura es **el único sitio
donde puede vivir una ventaja**.

**Consecuencia operativa, y es firme:** esa ventaja no se puede medir
codificando la regla. Cuatro intentos bastan para darlo por establecido. Sólo se
puede medir midiéndole a él — `PREREGISTRO_criterio.md` (300 etiquetas a ciegas,
escrito en agosto y nunca ejecutado) o el registro hacia delante.

Aviso de tamaño: son 12-13 operaciones. Pequeño. Pero cuatro formulaciones
distintas cayendo todas en el 50 % convence más que cualquiera de ellas sola.

## Herramientas hechas para esto

- `docs/agosto_m1.html` — los quince días con datos, en M1, con los niveles de
  Asia y sus entradas. Se toca una vela y da su precio exacto; se pueden marcar
  niveles para señalar en el gráfico lo que se quiere explicar. Nace de que su
  TradingView gratuito no llega en M1 a agosto.
- `bt/grafico_dia.py` — genera el PNG de un día suelto.

## Diferencia con lo medido hasta ahora

`bt/su_regla_instrumentos.py` mide otra cosa: el cuerpo de la última M5 cerrada
roto por el cierre de una M1, que dispara 49,5 veces al día. Lo que él describe
aquí es un barrido de liquidez más una rotura de estructura, y aparece muchísimo
menos.

**Los 31,3 % de acierto y las 85.453 señales de todos los documentos anteriores
miden esa otra regla, no ésta.**
