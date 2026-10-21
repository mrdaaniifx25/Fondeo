# Resultado · ¿existe un punto óptimo de entrada en el CRT? No.

Pre-registro: `docs/PREREGISTRO_punto_optimo.md`. Código: `bt/punto_optimo.py`
(el CSV de las 220 celdas se regenera corriéndolo).
EURUSD 2021-2026, oro y DAX 2023-2026. Coste ECN. Horizonte 4 horas.
**220 celdas: 11 instantes de entrada × 4 stops × 5 objetivos.**

---

## 0 · La primera pasada le daba la razón, y era un sesgo de anticipación mío

```
  entrada           stop         objetivo    n      acierto  coste   bruta     neta      z
  retroceso 0,750   mecha x2,0   R:R 1,5   18806    47,7%   27,3%  +0,3395  +0,0666  +4,98
  retroceso 0,750   mecha x1,5   R:R 2,0   18806    44,6%   36,4%  +0,4383  +0,0745  +4,35
  retroceso 0,750   mecha        R:R 3,0   18806    40,0%   54,6%  +0,6503  +0,1046  +4,26
```

z +4,98 contra un umbral de selección de 3,00, acierto 47,7 % contra un nulo
geométrico del 40 %, y una lectura perfectamente plausible: *«el punto óptimo es
el retroceso 0,75 con stop ancho»*. Exactamente la hipótesis del usuario.

**El error**: el relleno de las órdenes límite se detectaba a nivel de **vela
M15** y el camino se medía desde la **apertura de esa vela**. En una compra el
límite está por debajo de la apertura, así que se medía el camino desde un
instante **anterior a la propia entrada**. Y con stops minúsculos —lo que produce
un retroceso profundo, pegado a la mecha— el objetivo caía **por debajo de la
apertura** y se daba por alcanzado en el **índice 0**, antes de entrar.

Por eso el efecto estaba concentrado al 100 % en `retroceso 0,750`, el retroceso
con el mayor hueco entre apertura y entrada. Las entradas inmediatas y de espera,
que no tienen ese hueco, salían todas negativas.

Lo delató una fila con **coste del 12.230.920.555 % del riesgo** — una división
por un riesgo que era cero.

**Corrección**: relleno **minuto a minuto** sobre mínimos y máximos acumulados de
120 minutos, camino desde el minuto del relleno, y una guarda que descarta las
celdas donde el coste supera al riesgo.

## 1 · El resultado corregido

```
  mejor |z| de las 220 celdas     : 91,87   (en el lado NEGATIVO)
  UMBRAL de selección (220 celdas):  3,00
  celdas con neta > 0             :  0 de 220
  celdas con z > +2               :  0
  VEREDICTO                       : ESPACIO CERRADO
```

**Ninguna de las 220 celdas es positiva.** La mejor tiene z **−6,61**.

```
  LAS CINCO MEJORES
  entrada          stop         objetivo           n  acierto  coste    bruta     neta      z
  espera 3 velas   mecha x2,0   rango opuesto  15739    50,8%  10,8%  +0,0312  -0,0766  -6,61
  espera 4 velas   mecha x2,0   rango opuesto  14946    48,1%  10,3%  +0,0181  -0,0849  -7,28
  espera 3 velas   mecha x1,5   rango opuesto  15552    47,1%  13,2%  +0,0373  -0,0947  -7,39
  espera 2 velas   mecha x2,0   rango opuesto  16924    52,8%  11,6%  +0,0274  -0,0884  -7,73
  espera 4 velas   mecha x1,5   rango opuesto  14770    44,2%  12,6%  +0,0123  -0,1133  -8,54
```

## 2 · Cuánto falta, en un número

La mejor celda tiene coste del **10,8 %** del riesgo y bruta **+0,0312**.

```
  bruta necesaria para empatar : +0,108
  mejor bruta encontrada       : +0,031
  falta un factor de           :  3,5x
```

**Hace falta tres veces y media la mejor ventaja bruta que aparece en 220
celdas.** No un ajuste fino: un orden de magnitud distinto.

## 3 · El hallazgo real: esperar un retroceso mejor PEOR, y tiene mecanismo

```
  entrada            z mediana   neta mediana   n medio
  espera 6 velas       -16,56      -0,1462       17030
  inmediata            -16,57      -0,1790       19838
  espera 3 velas       -16,73      -0,1543       17374
  espera 2 velas       -17,79      -0,1752       17696
  retroceso 0,250      -27,14      -0,2821       18784
  retroceso 0,382      -30,15      -0,3155       18047
  retroceso 0,500      -34,08      -0,3291       17287
  retroceso 0,618      -34,46      -0,3672       16406
  retroceso 0,750      -37,93      -0,4215       15286
```

**Monótono: cuanto más profundo el retroceso exigido, peor el resultado.** Y la
razón no es el azar, es **selección adversa en el relleno**:

> Su orden límite sólo se ejecuta si el precio siguió yendo en su contra. El
> propio hecho de que le entre la orden es una señal **negativa** sobre esa
> operación.

Esto contradice una de las creencias más extendidas del trading minorista
—«espera un precio mejor»— y lo hace con mecanismo, no con estadística. Un
precio de entrada mejor no es gratis: **se paga con la composición de la muestra
que llega a ejecutarse.**

Firmé que los retrocesos profundos darían «neto cero». Dan **−0,42**. Fallé.

## 4 · Las otras dos dimensiones

```
  stop               z mediana   neta mediana        objetivo        z mediana   neta mediana
  mecha x2,0           -20,52      -0,1761           rango opuesto     -15,11      -0,1867
  mecha x1,5           -22,71      -0,2116           R:R 1,5           -20,82      -0,1816
  mecha                -25,26      -0,2284           R:R 2,0           -21,29      -0,1923
  rango opuesto        -31,04      -0,2948           R:R 3,0           -25,37      -0,2552
                                                     R:R 1,0           -25,47      -0,1833
```

**Los stops anchos sí ayudan**, de forma monótona: mecha ×2,0 da −0,176 y la
mecha pelada −0,228. Es el coste bajando del 17,6 % al 10,8 % del riesgo. Firmé
que daría «el mismo neto»; da mejor neto, sólo que no llega a cero.

Y el objetivo al extremo opuesto del rango bate a los R:R fijos, que es lo mismo
que salió en `RESULTADOS_timing_crt.md`.

## 5 · Mis cuatro predicciones firmadas

| firmé | salió | |
|---|---|---|
| **la mejor celda quedará por debajo del umbral de selección** | 0 de 220 por encima de +2 | ✔ |
| ninguna celda con n > 500 pasará de z +2,5 | ninguna pasa de +2 | ✔ |
| los stops anchos darán el mismo neto | dan mejor neto (−0,176 vs −0,228) | ✘ |
| los retrocesos profundos darán neto cero | dan −0,42, y monótono | ✘ |

## Lo que esto cierra, y lo que no

**Cierra la afirmación de espacio.** «Hay que encontrar el punto óptimo de
entrada» ya no es una conjetura abierta sobre el CRT en M15: se han recorrido los
once instantes razonables cruzados con los cuatro stops y los cinco objetivos, y
el mejor de 220 está a 3,5 veces de distancia del empate. No es que no se haya
encontrado: es que **el espacio se ha medido entero y no está dentro**.

**No cierra** el CRT en temporalidades mayores con horizontes de días —casilla 1
de `docs/QUE_MANDAR.md`, aún abierta— ni dice nada sobre instrumentos que no sean
estos tres.

**Y deja un hallazgo que vale por sí mismo**, independiente del CRT: *esperar un
retroceso para entrar mejor empeora el resultado de forma monótona, por selección
adversa en el relleno.* Eso aplica a cualquier estrategia que use órdenes límite
y no estaba medido en ningún sitio de este proyecto.
