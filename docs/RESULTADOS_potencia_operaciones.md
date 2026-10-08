# Resultado · la potencia del aparato, por operación

Código: `bt/potencia_operaciones.py`. **94.297 operaciones reales**
(EURUSD 44.027, oro 27.828, DAX 22.442): barrido de la vela M15 anterior con
cierre de vuelta dentro, stop tras la mecha, objetivo 2R. Es la forma de
operación más repetida de todo el proyecto.

Cada operación se resuelve **en los dos sentidos** sobre la misma geometría, así
que para cada una se conoce el desenlace si se hubiera comprado y si se hubiera
vendido. Eso permite inyectar «habilidad» de tamaño exacto: un operador con
habilidad *h* elige el lado bueno con probabilidad *h*; *h* = 0,50 es no tener
ninguna ventaja.

Complementa `docs/SUELO_DE_DETECCION.md`, que calcula el suelo en Sharpe sobre
meses. Aquí el suelo se calcula en puntos de acierto sobre operaciones.

---

## 1 · El aparato ve ventajas ridículamente pequeñas... en bruto

```
 habilidad  pp sobre azar  acierto  R/op BRUTA       z   R/op NETA       z
     0,500          0,0pp    33,5%     +0,0058   +1,24     -0,6631  -45,32
     0,505          0,5pp    33,9%     +0,0164   +3,50     -0,6525  -44,54
     0,510          1,0pp    34,2%     +0,0255   +5,42     -0,6434  -43,90
     0,520          2,0pp    34,9%     +0,0467   +9,92     -0,6222  -42,47
     0,540          4,0pp    36,2%     +0,0858  +18,03     -0,5831  -39,75
     0,560          6,0pp    37,6%     +0,1268  +26,37     -0,5421  -36,90
     0,600         10,0pp    40,2%     +0,2061  +42,39     -0,4628  -31,50
```

Con **medio punto porcentual** de habilidad real, el estadístico da **z +3,50**.
Con un punto, +5,42. La recuperación es monótona y lineal.

**Esto cierra la duda de la potencia en intradía.** Si en alguna de las 175.000
operaciones medidas en tres meses hubiera habido medio punto de acierto
direccional de verdad, se habría visto a z +3,5. No es que el aparato esté ciego:
es de los sensibles.

Y fíjese en la primera fila: sin habilidad, bruto +0,0058 con z +1,24. Cero, que
es lo que tiene que salir.

## 2 · Pero en NETO no hay habilidad que valga

La columna de la derecha no cruza el cero **ni con diez puntos de habilidad**. La
búsqueda de la ventaja mínima detectable en neto se salió del techo (0,75) sin
encontrarla.

Interpolando la tabla, que es lineal:

```
  umbral de acierto para no perder, con mi coste:        55,6 %
  acierto sin habilidad (nulo geométrico):               33,3 %
  habilidad necesaria para empatar:        acertar el ~83 % de las direcciones
```

**Con un stop de 6,9 pips hay que acertar el lado cuatro veces de cada cinco
sólo para no perder dinero.** Eso no es un problema de detección: es la
horquilla. Y es exactamente lo que dice la fórmula del proyecto —
`umbral = (1 + coste/riesgo) / (1 + R:R)` — pero verlo así, con un operador
hipotético que acierta el 75 % y aun así pierde, es más elocuente que la
fórmula.

## 3 · Un error mío: he usado un coste dos veces mayor que el de un ECN

```
                    coste/riesgo   R/op NETA       z  umbral de acierto
  el que uso               66,9%     -0,6592  -46,00         55,6%
  ECN realista             31,4%     -0,3041  -38,21         43,8%
  acierto real de la señal: 33,7 %   ·   nulo geométrico: 33,3 %
```

He estado aplicando 1,43 pips en EURUSD, 0,35 $ en oro y 1,6 puntos en DAX. Un
bróker ECN decente cobra **unos 0,70 pips, 0,12 $ y 0,8 puntos** contando
comisión. **Mi coste era 2,1 veces el real.**

Eso corrige a la baja todos los números netos intradía del proyecto, y conviene
decirlo sin rodeos. Lo que **no** cambia es ninguna conclusión:

- La ventaja bruta medida sigue siendo cero: 33,7 % de acierto contra un 33,3 %
  geométrico. **+0,4 puntos.**
- El umbral con coste de ECN sigue siendo **43,8 %**. Hacen falta **+10,5 puntos**
  de acierto y hay +0,4.

Es decir: el coste que usaba era pesimista, y aun con el coste correcto falta un
orden de magnitud de ventaja. Pero el dato queda escrito.

## 4 · El sesgo de empate: pequeño, y del tamaño de lo que medía

Cuando el stop y el objetivo caen **en el mismo minuto**, el motor resuelve
siempre como pérdida. Es una convención pesimista, declarada en
`docs/VALIDACION_motor.md`. Lo que no estaba medido es cuánto pesa:

```
  empates: 1.156 de 188.594 resoluciones = 0,61 %
  R/op con el motor actual (pesimista):  +0,0097
  R/op dando las dudosas por ganadas:    +0,0375
  diferencia:                            +0,0278
```

Un 0,61 % de operaciones ambiguas mueve la R media **+0,028**.

Comparado con el 0,66 de coste es insignificante. Pero comparado con los
resultados pequeños que he ido descartando a lo largo del proyecto —muchos
estaban entre +0,02 y +0,05 de R bruta— **es del mismo tamaño**. Con datos M1 no
se puede saber cuál de los dos pasó primero; haría falta tick.

Así que la lectura honesta es: **todo número bruto intradía de este proyecto
lleva una incertidumbre de ±0,03 R que no estaba declarada.** No cambia ningún
signo de las conclusiones grandes, y sí relativiza las celdas pequeñas.

## Lo que esto establece

Juntando con `VALIDACION_motor.md` y `SUELO_DE_DETECCION.md`, el aparato queda
caracterizado en los tres ejes:

| pregunta | respuesta | dónde |
|---|---|---|
| ¿fabrica ventajas falsas? | no, 32 celdas al azar dan cero | `VALIDACION_motor.md` |
| ¿destruye ventajas reales? | no, las recupera monótonamente | `VALIDACION_motor.md` |
| ¿qué tamaño mínimo ve en intradía? | **0,5 pp de acierto, a z +3,5** | aquí |
| ¿qué tamaño mínimo ve en mensual? | Sharpe 0,54 en 2013-2026 | `SUELO_DE_DETECCION.md` |

En intradía la potencia es enorme y la respuesta es firme: **no hay nada, y lo
sabría si lo hubiera.**

En mensual la potencia es mediocre y la respuesta es honesta: **no he encontrado
nada, y algo con Sharpe 0,2-0,5 se me escaparía.**

Son dos conclusiones de fuerza muy distinta y hasta hoy las estaba diciendo con
el mismo tono.
