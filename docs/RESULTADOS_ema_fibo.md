# Resultado · EMA + Fibonacci en EURUSD

Preregistro sellado en `c654bc7`. Código en `bt/ema_fibo.py`,
`bt/ema_fibo_lado.py`, `bt/ema_fibo_sens.py`, `bt/ema_fibo_control.py`.

675 celdas: M15/H1/H4 x EMA 10/20/50/100/200 x fibo 38,2-78,6 % x R:R 1/2/3,
cada una partida en todo / compras / ventas.

## El resultado

    todo      mejor z  -1,87     0 de 225 celdas con z > 2
    compras   mejor z  -2,31     0 de 225
    ventas    mejor z  -0,42     0 de 225

    cinco nulos (datos barajados, sin ventaja):
      -3,10   ·   +0,69   ·   +0,64   ·   +1,74   ·   +3,64
      el ultimo produjo 5 celdas con z > 2 SIN QUE HUBIERA NADA

    lo real cae en el percentil 20 de lo falso

**EMA+Fibo en EURUSD rinde peor que datos barajados.** Y en bruto, antes de
pagar un solo pip, la mejor de 225 celdas esta en z -0,44. Esto lo separa de
todo lo demas del proyecto: en SMC-71 habia ventaja bruta real (+0,166 R,
z +4,90) que el coste se comia. Aqui no hay nada debajo que comerse.

## Tres fallos mios, encontrados por los controles

### 1 · mirada al futuro dentro de la vela de entrada

La primera version daba **z +12,53** en H4 con EMA 10 y fibo 70,5 %. Era falso.
La vela que ejecuta una orden limitada de compra viene bajando desde arriba,
asi que su maximo es casi siempre ANTERIOR al llenado. Contarlo como objetivo
alcanzado es mirar al futuro. Medido en la celda M15/EMA10/fibo 70,5:

    operaciones cuyo TP se "alcanza" en la MISMA vela de entrada:  50,8 %
    de esas, las que tocan tambien el stop en esa vela:            22,2 %

Con R:R 1, ese regalo sube el acierto del 50 % al 75 % sin que el mercado
haga nada. Se detecto porque **los nulos daban z de +10 y +15 igual que lo
real**: si el ruido puntua como la senal, el fallo esta en el motor.

### 2 · el tratamiento "neutro" del stop, que tambien miraba al futuro

Al corregir lo anterior propuse tres tratamientos y dije que la verdad estaba
"entre el pesimista y el neutro". Falso. En una compra limitada, el minimo de
la vela de entrada es **necesariamente posterior al llenado** -es imposible
que el minimo preceda al primer toque del nivel-. Ignorarlo deja sobrevivir
operaciones ya detenidas. El modo neutro daba z +7,71 bruto por eso.

El tratamiento correcto es unico: **stop en la vela de entrada (obligatorio),
objetivo desde la siguiente (prudente ante la ambiguedad del OHLC).**

### 3 · un control positivo que no podia medir lo que decia medir

Inyecte deriva y la rejilla no la vio. Parecia que el motor estaba ciego.
No: la rejilla agregaba compras y ventas, y una deriva direccional sube unas
y hunde las otras por igual. Se cancelaba. Medido con 8 pips inyectados:

    compras   -0,1236  ->  +0,1150
    ventas    -0,1044  ->  -0,2717
    agregado  -0,1135  ->  -0,0610      <- casi no se mueve

Ademas confundi deriva nominal con neta: "3 pips en el 60 % de los dias" son
**0,6 pips netos**, por debajo del coste de 1,43. Invisible por construccion.

## Las tres predicciones firmadas

    1  mejor celda real con z entre +2 y +4      NO   salio -1,87
    2  mejor z de un nulo entre +2,5 y +3,5      NO   salio -3,01 de media
    3  la real NO batira al mejor nulo           SI   percentil 20

Falle las dos de magnitud porque las escribi con el codigo roto en la cabeza.
Acerte la unica que decidia.

## Lo que este resultado NO puede decir

Sin curva de deteccion, un cero no distingue *"no hay nada"* de *"hay algo mas
pequeno de lo que este montaje ve"*. `bt/ema_fibo_deteccion.py` la mide.
Referencia teorica: con n = 3.000 operaciones y desviacion de R proxima a 1,
z = +2 exige R = +0,036 — cinco veces menor que la ventaja de SMC-71. La
sensibilidad da de sobra; el problema no es que no se vea.
