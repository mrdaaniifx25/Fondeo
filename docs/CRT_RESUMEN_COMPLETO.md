# El CRT, completo: qué es, qué tiene de verdad, y qué mide

Resumen de todo lo que este proyecto sabe sobre la *Candle Range Theory*.
**45 documentos y 43 guiones** de medición, de julio a octubre de 2026.

---

# PARTE 1 · QUÉ ES EL CRT

## 1.1 · De dónde viene

Lo popularizó **Romeo TP** en YouTube, exalumno de ICT, con un vídeo titulado
*«¿Qué es CRT y por qué todas las demás estrategias son basura?»*. En español lo
difunden varios canales —Alex Ruiz entre ellos— y hay una guía escrita de Rubén
Villahermosa de 35 páginas que es la versión más completa.

**No es una estrategia, es una metodología.** Como dice uno de los vídeos: *«en
vez de operar un cruce de medias específico, CRT sería como operar medias
móviles»*. Eso importa, porque significa que no hay una única regla que refutar
sino una familia — y por eso este proyecto ha medido veinte variantes y no una.

## 1.2 · El patrón base: tres velas

Todo parte de **el rango de una vela**: desde su máximo hasta su mínimo, mecha
incluida.

```
  VELA 1 · RANGO          define el rango de referencia
  VELA 2 · MANIPULACIÓN   barre un extremo del rango y CIERRA de vuelta dentro
  VELA 3 · DISTRIBUCIÓN   el precio va hacia el extremo OPUESTO
```

Las cuatro inferencias canónicas:

| lo que hace la vela 2 | sesgo para la vela 3 |
|---|---|
| **cierra por encima** del rango | continuación alcista |
| **cierra por debajo** del rango | continuación bajista |
| **mecha por encima** sin cerrar fuera | giro bajista |
| **mecha por debajo** sin cerrar fuera | giro alcista |

La guía es explícita sobre el error más común, y lo llama *«Error #1: el mayor
destructor de cuentas»*: **entrar en la vela 2 en vez de esperar a la 3.**

## 1.3 · La fractalidad y la cascada

El mismo patrón existe en todas las temporalidades. Romeo TP propone cuatro
parejas marco-grande / marco-de-ejecución:

```
  mensual   -> ejecutar en 4 horas
  semanal   -> ejecutar en 1 hora
  diario    -> ejecutar en 15 minutos
  4 horas   -> ejecutar en 5 minutos
```

La versión en cascada que enseñan los vídeos españoles añade el **alineamiento**:
el rango diario activado, el de H4 activado, el de H1 activado y el de M15
**confirmado** (barrido *y* cierre de vuelta dentro), todo en la misma dirección.
Sólo entonces se entra.

**«Activado» ≠ «confirmado».** Activado = ya se llevó un extremo. Confirmado =
además cerró de vuelta dentro.

## 1.4 · La capa de sesiones

Sobre lo anterior se superpone el reloj:

```
  rango de Asia      00:00-08:00 hora española
  killzone Londres   08:00-11:00
  killzone NY        13:00-16:00
  almuerzo europeo   11:00-13:00  (se excluye)
```

El barrido que vale es el que ocurre **dentro de una killzone** y **sobre un
nivel de la sesión anterior**.

## 1.5 · Entrada, stop y objetivo

```
  ENTRADA   a mercado al cierre de la vela de confirmación (apertura de la siguiente)
  STOP      detrás de la mecha del barrido (el "turtle soup")
  OBJETIVO  el extremo opuesto del rango — o el 50 % del rango mayor
```

Variantes de objetivo que los propios vídeos mencionan: el extremo opuesto del
rango H4 («como mínimo»), el 50 % del rango diario, y el extremo completo del
rango diario — *«lo cual sería un 25 de rentabilidad riesgo»*.

## 1.6 · Los añadidos habituales

Order blocks · fair value gaps · el «poder de tres» (AMD: acumulación,
manipulación, distribución) · Fibonacci 70,5 % · divergencias SMT entre
instrumentos · confluencia multimarco.

---

# PARTE 2 · QUÉ TIENE DE VERDAD

Esto es importante y suele perderse: **el CRT no es un invento vacío.**

## 2.1 · El patrón existe y la ventaja bruta es real

```
  ventaja BRUTA del CRT, homogénea entre temporalidades:  +0,082 R
  (RESULTADOS_crt_temporalidad.md, siete temporalidades)
```

Eso no es cero. El precio **sí** barre niveles y **sí** se da la vuelta más a
menudo de lo que lo haría una moneda ciega. El patrón está ahí.

## 2.2 · Las correcciones de la guía funcionan en la dirección que dice

Medido en `RESULTADOS_crt_canonico.md`:

```
  entrada en la Vela 2 (el "error #1")   n   122   bruto -0,0895   PF neto 0,791
  entrada en la Vela 3 (lo correcto)     n   559   bruto +0,0248   PF neto 0,884
```

**Corregir el error que la guía señala mueve el resultado de negativo a cero.**
La guía tiene razón sobre su propio error. También acierta el anclaje de la
rejilla H4 (01:00 hora Nueva York, no 00:00): corregirlo mejora el resultado a
menos de la mitad de malo.

## 2.3 · El timing importa, y eso está medido

De `RESULTADOS_timing_crt.md`, con la dirección dada por buena:

```
  entrar en cada vela H4 (ciego)   exceso sobre el nulo  +4,2 pp
  esperar al rango alineado (CRT)  exceso                +6,2 pp
  permutación dentro de semana:  z +6,35,  p < 0,0001
```

**La afirmación «de nada sirve tener el bias bien si compras cuando no toca» es
correcta.** Esperar vale dos o tres puntos de acierto. Eso es real.

## 2.4 · Y la ventana horaria parece tener algo

De `RESULTADOS_su_patron.md`, sobre sus propias reglas:

```
  Londres 08:00-11:00, patrón completo   bruta +0,0835   z +2,12
  Londres 08:00-11:00, entrada ciega     bruta +0,0347   z +1,92
  Nueva York 13:00-16:00                 bruta -0,0464   z -2,60
```

La bruta de la ventana de Londres es positiva. La de Nueva York es negativa.

---

# PARTE 3 · POR QUÉ NO SE COBRA

## 3.1 · La ecuación que lo gobierna todo

```
  neta = ventaja × (1 + R:R) − coste/riesgo
  umbral de equilibrio = (1 + coste/riesgo) / (1 + R:R)
```

El R:R **multiplica** la ventaja. El stop **divide** el coste. Y el CRT pone el
stop detrás de la mecha, que son 3-7 pips.

```
  stop en la mecha del barrido (M15, EURUSD):  riesgo 5,2 pips -> coste 19,7 % del riesgo
  stop en 1,5 x ATR(14):                       riesgo 7,1 pips -> coste 10,4 %
  la cascada del vídeo (stop 3 pips, objetivo H4):           coste 66,8 %
  la misma, en DAX:                                          coste 115,9 %
```

**En el DAX la horquilla es más ancha que la distancia al stop.** Esa operación
pierde en el instante de abrirse.

## 3.2 · El resultado central

```
  ventaja bruta        +0,082 R
  coste típico         0,10 a 0,20 R
  ------------------------------------
  neta                 negativa, siempre
```

**El CRT no falla por la dirección. Falla porque su geometría maximiza el coste.**
Pone el stop lo más cerca posible —que es lo que lo hace atractivo en pantalla,
porque da R:R enormes— y eso es exactamente lo que convierte una ventaja real de
+0,08 en una pérdida.

## 3.3 · El muro, por horizonte

La ventaja mínima necesaria para empatar, en unidades del ruido de cada
horizonte (`RESULTADOS_muro_horizonte.md`):

```
  horizonte   EURUSD     oro      DAX
  1 hora      0,1076   0,0353   0,0156
  1 día       0,0226   0,0070   0,0032
  1 mes       0,0053   0,0019   0,0007
```

De una hora a un mes el muro cae **veinte veces**. Por eso el seguimiento de
tendencia en futuros es un negocio con historiales auditados y esto no: **no son
estrategias enfrentadas, es el mismo muro a dos alturas.**

---

# PARTE 4 · TODO LO MEDIDO, UNA TABLA

| variante | muestra | resultado |
|---|---|---|
| **CRT canónico**, entrada Vela 3 | 559 ops, 5 instr. | bruto **+0,0248**, p 0,717, PF neto 0,884 |
| **CRT por temporalidad** | 7 marcos | bruta **+0,082** homogénea; neta negativa en todas |
| **CRT invertido** (operar al revés) | 1.232 ops | 41,6 % · **−0,075** R/op · PF 0,77 · −262 €/mes |
| **Cascada D1→H4→H1→M15** (el vídeo) | 8.175 señales | bruta **−0,045** (z −0,66) · neta **−0,713** |
| ↳ con 3 marcos alineados | 2.606 | **la PEOR celda** de las cuatro |
| **Cascada hacia objetivo semanal** | 6.422 | cubo de 3 alineadas **+0,029** (z +0,20), no monótono |
| **H4 como filtro de dirección** | 3.964 | **resta**: 35,0 % sin él, 34,3 % con él |
| **CRT + Asia + M1** | 1.953 | neta **−0,611** (z −18,68) |
| **CRT por sesión** | 59.852 filas | sin separación útil |
| **CRT + Fibonacci** | — | ningún nivel se separa del resto |
| **CRT + confluencias de la guía** | — | **ninguna de las dos funciona** |
| **CRT a las 9:00** | — | **+0,0146** bruto (z +0,61), neta −0,21 |
| **¿Qué diferencia al ganador?** (ML) | — | acierto 42,2 %, R neta **−0,0815** |
| **Objetivo superior pendiente** (su idea) | — | apuntaba bien, pero **p ≈ 0,2** y se invierte al subir de marco |
| **La solución ensamblada** | 12 formas | **pierde en las doce** fuera de muestra |
| **Sistema CRT final** | 24 celdas | **las 24 negativas fuera de muestra** |
| **Timing: esperar el retroceso** | 13.627 | +6,2 pp — pero un **retroceso genérico da +7,3** |
| ↳ CRT alineado SIN retroceso real | 2.874 | **+4,3 pp = idéntico al ciego (+4,2)** |
| **Punto óptimo de entrada** | **220 celdas** | **0 positivas**, mejor z **−6,61**, falta **×3,5** |
| **Su patrón de demo, Londres** | 1.281 | bruta +0,0835 — pero el **ciego da +0,0347**, dif. z +0,86 |

---

# PARTE 5 · LOS CUATRO INTENTOS DE ARREGLARLO

Todos cerrados, y cada uno cierra una clase entera de propuestas.

**1 · Subir de temporalidad.** Si el problema es el coste y el coste es
`fijo/riesgo`, un stop más ancho lo arregla. Medido: la mecha del barrido
**no escala con la temporalidad** (M5 da 4,5 pips, M15 da 5,2). La microestructura
del barrido la fija, no el tamaño de la vela.

**2 · Añadir confluencias.** Order blocks, FVG, Fibonacci, SMT, contexto diario,
confluencia multimarco. Medidos uno a uno y todos juntos con *gradient boosting*
sobre 22 variables y 25.453 velas M15: **AUC 0,4984** fuera de muestra.

**3 · Filtrar por sesión o por hora.** 34 guiones de sesiones. El control que lo
cerró (`RESULTADOS_reloj.md`): cada sesión captura **exactamente su parte
proporcional** de la deriva del instrumento. No hay nada debajo que condicionar.

**4 · Buscar el punto óptimo de entrada.** 220 celdas (11 instantes × 4 stops ×
5 objetivos). **Cero positivas.** Y un hallazgo que vale por sí mismo: exigir un
retroceso para entrar mejor **empeora de forma monótona** (0,25 → −0,28;
0,75 → −0,42), por **selección adversa en el relleno** — su orden límite sólo se
ejecuta si el precio siguió en su contra, así que el relleno es en sí una señal
negativa.

---

# PARTE 6 · MIS PROPIOS ERRORES MIDIENDO ESTO

Tres resultados espectaculares produje yo en una semana, y los tres eran bugs.
Van aquí porque explican mejor que nada por qué tanta gente cree que funciona.

| qué medí | qué salió | la causa |
|---|---|---|
| sistema EUR/USD intradía | acierto **69,3 %**, PF **2,61**, **+4.523 €/mes** | un signo: cada stop de un corto contaba como +1R |
| carry en divisas | **t +2,95** con recargo de bróker | el recargo entraba como ingreso en las cortas |
| punto óptimo de entrada | **z +4,98** sobre un umbral de 3,00 | el camino se medía desde antes de la entrada |

**Cero resultados espectaculares han sobrevivido a la revisión.** Y los números
de la primera fila —70 % de acierto, PF 2,6— son exactamente los que se anuncian.

El motor sí está calibrado en las dos direcciones (`VALIDACION_motor.md`): con
128.000 entradas al azar las 32 celdas dan cero, y con una ventaja inyectada la
recupera de forma monótona. **No es que el backtest sea pesimista. Es que
comprobar bien es dificilísimo.**

---

# PARTE 7 · LO QUE SE LLEVA EN LIMPIO

### Lo que es verdad

- El patrón existe y tiene **+0,082 R de ventaja bruta**.
- La guía acierta en su propio «error nº1»: entrar en la vela 3, no en la 2.
- **Esperar el momento vale 2-3 puntos de acierto** con la dirección dada.
- La ventana de **Londres 08:00-11:00** tiene bruta positiva; la de NY, negativa.

### Lo que es falso

- Que la **cascada multimarco** aporte: con 3 marcos alineados sale la peor celda.
- Que el **rango alineado** sea lo que funciona: sin retroceso real da lo mismo
  que entrar a ciegas (+4,3 contra +4,2).
- Que exista un **punto óptimo de entrada**: 0 de 220 celdas.
- Que haya una **confluencia** que lo rescate: AUC 0,4984.

### Y lo accionable, si va a operarlo igualmente

1. **Ensanche el stop.** De la mecha a 1,5×ATR(14): el neto pasa de −0,124 a
   −0,021. **Seis veces mejor sin acertar una operación más.**
2. **Londres sí, Nueva York no.**
3. **Entre en la vela 3**, nunca en la 2.
4. **Objetivos cercanos**, no el extremo del rango diario: ir a por el «25 de
   R:R» acierta 17,5 % donde la geometría pura da 22,9 % (z −5,48). Los
   objetivos lejanos se alcanzan **menos** que por azar.
5. **No espere retrocesos profundos para entrar mejor.** Empeora, y es mecánico.

### Y lo que ninguna de esas cinco arregla

La mejor configuración medida del CRT, con todo corregido, es **−0,021 R por
operación con z −0,53**: indistinguible de cero, no por encima.

El CRT es una descripción correcta de algo que el mercado hace, envuelta en una
geometría de ejecución que garantiza que no se pueda cobrar.

---

# PARTE 8 · LAS FUENTES, Y LO QUE AÚN NO ESTÁ MEDIDO

## 8.1 · De dónde sale todo lo anterior

| fuente | qué aportó | dónde |
|---|---|---|
| **Romeo TP** (YouTube) | el origen y el patrón de tres velas | `CRT_resumen.md` |
| **Guía de Rubén Villahermosa** (35 pág.) | la versión canónica, killzones, el «error nº1» | `RESULTADOS_crt_canonico.md` |
| **@bctrades__** (32 publicaciones de Instagram) + **@trader.derivados** | el modelo completo y ejecutable | `CRT_ampliacion.md`, 25-ago-2026 |
| **SmartRisk** (4º vídeo) | rango dinámico por sesión | `RESULTADOS_crt_sesion.md` |
| **Alex Ruiz** · curso gratuito de CRT | la cascada D1→H4→H1→M15 | `RESULTADOS_crt_cascada_video.md` |
| **Alex Ruiz** · review semanal | el timing con la dirección dada | `RESULTADOS_timing_crt.md` |
| **Brad Gould** | dos reglas de entrada y stop | `RESULTADOS_crt_9am.md` |
| **«CRT Turtle Soup»** (dos `.ex4` de una formación) | verificación de los binarios | `EX4_crt_turtle_soup.md` |
| **Sus propias respuestas** | cómo opera él, preguntado y contestado | `CRT_H4_especificacion.md` |
| **Sus capturas de demo** (oct-2026) | su patrón real de Londres | `RESULTADOS_su_patron.md` |

## 8.2 · Lo que está transcrito pero NUNCA se ha medido

De `CRT_ampliacion.md` §3, el material de `@bctrades__`. Son **seis piezas
documentadas y sin medir**, y dos de ellas tocan la única dimensión que no se ha
explorado en todo el proyecto: **la gestión de la posición.**

| pieza | por qué sigue abierta |
|---|---|
| **Cierre dentro del CUERPO, no del rango** | cambia la definición de confirmación: es una regla distinta, no un filtro |
| **Liquidez doble y triple** | barridos de dos o tres niveles a la vez; nunca se ha condicionado por eso |
| **Rango reiniciado / descartado** | cuándo un rango deja de valer. Es la regla que hace al CRT irrefutable si se usa a posteriori — medirla la congelaría |
| **Temporalidad 2H** | **sin usar nunca**. Está entre H1 y H4, las dos medidas |
| **Dos objetivos escalonados** (TP1 en 2H, TP2 en 4H) | **no es una variante del motor: es gestión.** Nunca se ha salido en dos tramos |
| **PO3 con dos entradas** | lo mismo: dos entradas en vez de una |

**Esto es una laguna real de este resumen y del proyecto.** Las 220 celdas de
`RESULTADOS_punto_optimo.md` recorrieron el instante de entrada, el ancho del
stop y la distancia del objetivo — pero **siempre con una entrada y una salida**.
Salir en dos tramos o entrar en dos no está medido en ningún sitio.

No cambia lo que ya está medido: con bruta +0,082 y coste 0,10-0,20, repartir la
salida no crea ventaja donde no la hay. Pero **sí puede cambiar la varianza**, y
eso en una cuenta de fondeo con límite de caída no es irrelevante.

## 8.3 · Una fuente que no aparece

**No hay ni una mención a «Cluty» en los 310 documentos ni en los 339 guiones
del repositorio.** Si ese material llegó a pasarse, no quedó registrado y por
tanto **no está medido**. Si existe, hay que volver a traerlo.
