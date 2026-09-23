# Preregistro · buscar donde el coste permite que exista algo

Escrito antes de tocar los datos.

## Por qué aquí y no donde llevamos dos meses

Para un 1:k fijo, la geometría pura da P(TP) = 1/(1+k) sea cual sea el stop. El
equilibrio con coste es p\* = (1 + c/s)/(1+k). La diferencia es la **ventaja que
hay que sacarle a la geometría**:

```
ventaja necesaria = (c/s)/(1+k)
```

| stop | coste/riesgo | ventaja necesaria a 1:2 | horizonte |
|---|---|---|---|
| 3 p | 47,7 % | **+15,9 pt** | minutos |
| 6 p | 23,8 % | **+7,9 pt** | media hora |
| 10 p | 14,3 % | +4,8 pt | una hora |
| 25 p | 5,7 % | +1,9 pt | media sesión |
| 60 p | 2,4 % | **+0,8 pt** | un día |
| 200 p | 0,7 % | **+0,2 pt** | una semana |

Y esto es lo que ha conseguido cada regla mecánica del proyecto, en puntos sobre
su propia geometría:

```
rotura del nivel de Asia (M5)      -2,5 pt
cascada H4/M15/M5/M1, 90 celdas    -1 a +1 pt
rechazo del nivel de Asia (M5)     +1,4 pt
CRT en H4 con stop en la mecha     +2,9 pt
modelo de 16 variables (M5)        +4,1 pt   <- el mejor de todo el proyecto
```

**Dos meses operando con stops de 3 a 10 pips, donde el muro pide entre 5 y 16
puntos, y el mejor resultado del proyecto es +4,1.** No es que las reglas fueran
malas. Es que el muro estaba demasiado alto para ese tamaño de stop.

Con stops de sesión o de día, el muro baja a **menos de un punto**. Es la única
región del espacio donde una ventaja pequeña y real puede sobrevivir al coste, y
es la única que este proyecto no ha tocado.

## Diseño

**Instrumentos**: los siete con historia completa —EURUSD, GBPUSD, USDJPY,
XAUUSD, NSXUSD, SPXUSD, GRXEUR—. Se agrupa en R, que no tiene unidades.

**Velas diarias** en Europe/Madrid. Entrada al cierre del día. Resolución en M1,
con tope de 20 días hábiles; lo que quede vivo se cierra a mercado.

**Tres reglas, definidas de antemano y sin parámetros ajustados:**

```
A · BARRIDO DIARIO  (el CRT suyo, a escala de día)
    El día D barre el extremo del día D-1 y CIERRA DENTRO DE SU CUERPO.
    Entrada al cierre de D, en contra del barrido.
    Stop en la mecha del barrido. Objetivo 1:k.

B · DONCHIAN 20     (la regla de tendencia canónica, con sus valores clásicos)
    El cierre supera el máximo de los 20 días anteriores -o pierde el mínimo-.
    Entrada al cierre. Stop en el extremo contrario de los últimos 10 días.
    Objetivo 1:k.

C · RUPTURA DEL DÍA ANTERIOR
    El cierre queda fuera del rango del día D-1.
    Entrada al cierre, a favor de la rotura.
    Stop en el extremo contrario del día D-1. Objetivo 1:k.
```

**k = 1, 2 y 3.** Una posición viva por instrumento; las señales que llegan con
una posición abierta se descartan.

**Coste**: estimado por instrumento (EURUSD 1,43 p medido; el resto, spread
típico minorista de ida y vuelta). Como a esta escala el coste es el 1-3 % del
riesgo, el valor exacto casi no mueve el resultado — que es justo el argumento.
Se reporta además el **coste de equilibrio** de cada celda.

## Contraste principal

**Nueve celdas** (3 reglas × 3 k), agrupando los siete instrumentos.
Bonferroni: hace falta **|z| > 2,77** en R neta (p < 0,0056).

Y además, para que cuente: **el signo tiene que aguantar en al menos cinco de los
siete instrumentos**. Una celda que salga de un solo instrumento no cuenta.

## Declarados de antemano como secundarios

1. Reparto por instrumento.
2. Días que se tarda en resolver, y peor racha en R.
3. Barrido de anchura de stop dentro de cada regla.
4. Lo mismo con salida por tiempo en vez de por objetivo.

## Predicción firmada

1. **A (el barrido diario) saldrá en la geometría**, sin separarse. La reversión
   después de un barrido diario en divisas es folclore; si existiera con esta
   fuerza se habría arbitrado.
2. **B (Donchian 20) será la mejor de las tres**, y con k = 1 será la única con
   opciones reales de pasar el umbral. Es la regla con más literatura a favor.
3. **C (ruptura del día anterior) saldrá negativa**, entre −0,05 y −0,20 R.
4. **Ninguna de las nueve celdas llegará a z > 2,77.** Predigo que esto también
   falla, pero que **fallará por poco** —entre −1 y +2 de z— en vez de por los
   −6 a −13 de todo lo anterior. Ese cambio de magnitud sería en sí el hallazgo:
   confirmaría que el problema era el muro y no la idea.
5. El acierto de cada celda quedará **a menos de 2 puntos de su geometría**.

Si B con k = 1 sale con z > 2,77 y el signo aguanta en cinco instrumentos, es la
primera cosa mecanizable del proyecto y se pasa a validarla en serio.

## Qué contaría como hallazgo

Una celda con **z > 2,77 en R neta agrupada**, signo consistente en **≥ 5 de 7
instrumentos**, y **coste de equilibrio al menos el doble** del coste estimado.
Nada por debajo cuenta, y si no llega se escribe que no llegó.
