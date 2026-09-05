# `pine/londres_operativa.pine` · qué hace y qué no

## Qué no hace

**No da señales de entrada.** Y no es por pereza: se midió. El modelo que
reproduce dónde entra —AUC 0,800, ocho veces la base— puesto a operar solo saca
**37,4 % en 1.449 operaciones sobre 1.032 días nuevos**, y el equilibrio con el
coste real está en el 41,3 %. La selección de la vela es suya y no se automatiza.

Lo que sí está medido, y es lo que el indicador automatiza:

| lo que dibuja | de dónde sale |
|---|---|
| alto y bajo de Asia (00:00-08:00) | los niveles que la página le pintaba |
| **alto y bajo que lleva Londres** | el 36,7 % de sus entradas están pegadas ahí, y aciertan el 73,5 % |
| el stop | el extremo de los últimos 10 minutos: mediana 5,9 p contra sus 6,0 p, error mediano 1,3 p |
| el objetivo | 1:2 sobre ese stop |
| los lotes | riesgo elegido ÷ (pips de stop × valor del pip) |
| aviso de rotura | cuerpo cerrado fuera del nivel de Asia: su peor caja, 33,3 % |
| ventana buena | los primeros 90 minutos; su mediana de entrada es 08:40 |
| **el cuerpo de la vela de M5** | lo único que en 150 operaciones separa sus ganadoras de sus perdedoras: cuerpo ≥ 60 % del rango, 50,0 %; por debajo, 78,0 % (p = 0,0006, y se repite en los cuatro bloques) |
| el veredicto de las cuatro cajas | cuerpo × nivel de Asia: 42 % / 65 % / 68 % / 82 % |
| el estado del CRT en H4 y M15 | apagado por defecto: se midió y **no separa nada** |

## El cuerpo de la vela: lo que decide

La fila **CUERPO de esta vela** enseña, en vivo, qué porcentaje del rango de la
vela de M5 en curso ocupa el cuerpo. Se arma desde el gráfico, así que en M1 se
ve formarse minuto a minuto y se cierra en el minuto en que él entraría.

| lo que ve | de sus 150 operaciones |
|---|---|
| cuerpo lleno, lejos del nivel de Asia | 42 % de acierto · 42 operaciones |
| cuerpo lleno, tocando el nivel | 65 % · 22 |
| cuerpo normal, tocando el nivel | 68 % · 23 |
| cuerpo normal, lejos del nivel | 82 % · 63 |

**Cuidado con leer esos porcentajes al revés.** Son el acierto de las operaciones
que él tomó estando en cada caja, no la probabilidad de que la vela suba. Que una
vela caiga en la caja del 82 % no es una señal de entrada: en una mañana hay
decenas de velas ahí. Es el filtro que se aplica *después* de que él vea algo.

## El CRT: está, pero no funciona

Se midieron ocho contrastes sobre sus 150 —CRT en la H4 cerrada, en la H4 viva,
en la última M15, en la M15 viva, y cada uno a favor o en contra de su
dirección— y **ninguno llega al umbral**. El mejor se queda en p = 0,05 y apunta
en su contra: cuando el CRT de M15 va en su dirección, aparece en el 7,4 % de sus
ganadoras y el 18,8 % de sus perdedoras.

El 71,3 % de sus entradas no tiene CRT ni en H4 ni en M15. Está en el indicador
porque él lo mira, apagado por defecto, y con la advertencia al lado.

## Cómo se pone

1. TradingView → Editor Pine → pegar el fichero entero → **Añadir al gráfico**.
2. Gráfico de **M1 o M5**. Por encima de M5 el stop pierde sentido y la tabla lo
   avisa.
3. En los ajustes: capital, y **riesgo 0,5 %** para las primeras 20 operaciones
   en directo.

## Cómo se lee la tabla

```
LONDRES        09:14      136 min      <- reloj y lo que queda de ventana
ventana        BUENA      +74 min      <- BUENA los primeros 90 minutos
alto de Asia   1.16542    +8.3 p
bajo de Asia   1.16301   -15.8 p
alto Londres   1.16498    +3.9 p       <- pegado a esto es su mejor caja
bajo Londres   1.16352   -10.6 p
stop compra    1.16401     5.8 p
objetivo       1.16575     2.0 R
stop venta     1.16512     6.3 p
objetivo       1.16333     2.0 R
0.5 % de 10000  0.17 lotes  0.16 lotes
pegado al alto de Londres · tu mejor caja
dos pérdidas y paras · 1:2 siempre
```

Los triángulos marcan el rechazo del nivel de Asia y la equis la rotura. **Son
contexto, no órdenes**: el rechazo mecánico sale 34,7 % y la rotura 33,3 %.

## Las reglas que no están en el código

```
ventana   08:00-11:30, y vive en la primera hora y media
NUNCA     la rotura del nivel de Asia. Es su peor caja: 33 %
parada    dos pérdidas, o las 11:30
riesgo    0,5 % las primeras 20 operaciones · 1 % si el acierto aguanta
          por encima del 55 % · nunca 2 %
```

## Por qué 0,5 % al principio

Las primeras veinte operaciones en directo son la medición que falta: separar
«lee algo que no sé medir» de «el simulador le favorece». A 0,5 % cada R son
50 $, el límite total son 20 R y su peor día en 150 operaciones fueron dos
pérdidas. Veinte operaciones a ese riesgo no pueden reventar la cuenta ni en el
peor escenario razonable, y el examen de FundingPips **no tiene límite de
tiempo**, así que medir no cuesta nada.

| si en directo acierta | operaciones para saberlo | sesiones |
|---|---|---|
| 66 % (lo medido) | 24 | ~18 |
| 60 % | 43 | ~33 |
| 55 % | 80 | ~62 |

Por encima del 55 % a las veinte, sube a 1 % y va a por el 8 %. Por debajo del
45 %, para: era el simulador.

---

# `pine/londres_roturas.pine` · el que dice compra y vende

Pidió un indicador que diga compra o vende. Este lo dice —con dirección, stop,
objetivo y lotaje— pero hay que entender qué es y qué no.

## Lo que detecta

**Su regla, exactamente**: el cuerpo de la última vela de M5 cerrada, roto por el
cierre de una vela de M1. Cubre el **83 %** de sus 223 entradas, z +4,88 contra
los minutos de control.

## Lo que hay que saber antes de usarlo

**La flecha sola pierde dinero.** Medido:

| | n | acierto | R neta |
|---|---|---|---|
| la primera rotura del día | 164 | 37,9 % | −0,255 |
| las tres primeras | 478 | 33,0 % | −0,348 |
| todas | 930 | 30,8 % | −0,346 |
| **sus 223 elegidas** | 223 | **64,8 %** | **+0,682** |

La diferencia es **su elección**, medida a ciegas en el examen de las roturas:
+16,1 puntos, z +2,65, p = 0,004.

**Por eso no es un sistema de señales, es un detector de candidatas.** La flecha
dice dónde mirar. Quien decide sigue siendo él.

## Los tres filtros, todos medidos

```
1 · el cuerpo de la vela de M5 por debajo del 80 % del rango
    (>= 80 % da 38,9 % en 37 operaciones suyas, contra 70,1 % del resto,
     Fisher p = 0,00054 sobre cinco bloques)
2 · stop entre 4 y 10 pips
    (entre 5 y 8 su eleccion separo 50,0 % contra 13,0 %)
3 · dentro de su ventana; entre las 09:00 y las 10:00 separo 46,2 % contra 17,9 %
```

Las roturas que no pasan un filtro se pintan en gris, para que vea lo que se está
saltando y por qué.

## El contador, que es la otra mitad

La tabla lleva la cuenta de candidatas del día y avisa a partir de la segunda.
No es prudencia: en el examen de las roturas aceptó **145 de 250** y perdió
dinero **aun eligiendo bien**. Operando de verdad toma **una de cada 28**.

**Elegir poco está medido como parte de lo que le hace ganar.**
