# Reversión a la media · reglas cerradas

Medición: `docs/RESULTADOS_mr_reglas.md`. Código: `bt/mr_reglas.py`,
`bt/mr_tope_dia.py`. EUR/USD, 2021-2026, salidas minuto a minuto.

---

## 1 · EJECUCIÓN

```
  INSTRUMENTO   EUR/USD
  GRÁFICO       15 minutos
  INDICADORES   EMA 20
                Bollinger: longitud 20, desviación 1,5
                RSI: longitud 14
                (los tres vienen de serie en TradingView; no hace falta script)
  HORARIO       todo el día. No hay filtro de sesión: lo probé y no aporta.
```

**COMPRA** — las cuatro condiciones en la MISMA vela de 15 minutos:

```
  1  el mínimo de la vela perfora la banda de Bollinger inferior
  2  RSI(14) por debajo de 30
  3  la vela cierra en verde (cierre > apertura)
  4  cierra en la mitad alta de su propio rango
```

**VENTA** — exactamente el espejo:

```
  1  el máximo de la vela perfora la banda superior
  2  RSI(14) por encima de 70
  3  la vela cierra en rojo
  4  cierra en la mitad baja de su propio rango
```

```
  ENTRADA    a mercado en la APERTURA de la vela SIGUIENTE.
             Nunca en el cierre de la vela que da la señal.
  STOP       15 pips fijos.
  OBJETIVO   el valor de la EMA 20 EN EL MOMENTO DE LA SEÑAL.
             Lo apuntas y no lo mueves aunque la media se mueva.
  TIEMPO     16 horas. Si no ha tocado nada, cierras a mercado.
  UNA        posición a la vez. Con una abierta, ignoras las señales.
```

### Por qué el objetivo congelado y no la media que se mueve

Te dije ayer que el objetivo dinámico ganaba. **Con stop fijo es al revés, y lo
he medido:**

```
  stop 15 pips, objetivo EMA20 congelada  ->  bruto +0,673 pips
  stop 15 pips, objetivo EMA20 dinámica   ->  bruto +0,426 pips
```

La media se mueve **hacia** el precio, así que el objetivo dinámico te saca
antes y te deja la mitad del recorrido. Lo de ayer salió con el stop pegado al
extremo, que es otra cosa. **Corrijo: objetivo congelado.**

---

## 2 · GESTIÓN DE RIESGO

```
  RIESGO         1,00 % por operación = 100 € sobre 10.000
  TAMAÑO         100 € / 15 pips = 6,67 € por pip = 0,78 lotes
  APALANCAMIENTO ~7,8x   (tu tope era 10x)   ok

  >>> LA REGLA QUE MÁS VALE DE TODO ESTO <<<
  PARAS EL DÍA TRAS 2 PÉRDIDAS SEGUIDAS.
  Cierras la plataforma. No hay excepciones. Mañana se empieza de cero.
```

### Por qué esa regla, con los números

El modo de fallo de la reversión a la media es el día de tendencia: el RSI se
queda clavado por debajo de 30, cada vela de rechazo falla, y encadenas
pérdidas. Eso es lo que te elimina, no una operación suelta.

```
  regla del día              n   neto pips  PEOR DÍA  riesgo máx  LAS DOS  muere día
  sin tope                1030      -0,027     -4,19      0,50 %     0,0 %      0,0 %
  tope 1 al día            710      -0,654     -1,05      2,75 %    25,2 %      0,0 %
  tope 2 al día            952      -0,090     -2,09      1,25 %    38,0 %      0,0 %
  tope 3 al día           1010      -0,030     -3,14      0,75 %    40,2 %      0,0 %
  PARAR TRAS 2 PÉRDIDAS    972      -0,019     -2,26      1,25 %    41,2 %      0,0 %
  parar tras 1 pérdida     772      -0,202     -1,05      2,75 %    27,5 %      0,0 %
```

«Parar tras 2 pérdidas» gana en las dos columnas a la vez: **conserva 972 de las
1.030 operaciones** (así que el neto es el mejor de la tabla, −0,019) y **recorta
el peor día de −4,19 R a −2,26 R**. Cortar más (parar tras 1) te quita 200
operaciones y empeora el neto a −0,202.

### Por qué 1,00 % y no 1,25 ni 1,50

```
   riesgo   peor día   fase 1   LAS DOS  días med  muere día
    0,75%     -1,70%    60,4%     23,5%        75      0,0%
    1,00%     -2,26%    54,9%     38,1%        59      0,0%   <- éste
    1,25%     -2,83%    55,9%     41,2%        41      0,0%
    1,50%     -3,39%    13,2%      5,2%        10     94,8%
```

A 1,25 % el peor día observado deja **17 céntimos de margen** sobre el límite del
3 %. A 1,50 % el acantilado: **94,8 % de muerte por límite diario**. A 1,00 % el
peor día te deja en −2,26 % y tienes colchón para un día peor que ninguno de los
1.426 medidos.

**No subas de 1,00 %.** Lo que ganas en velocidad lo pagas con la cuenta.

---

## 3 · LO QUE VALE, SIN ADORNOS

```
  operaciones            172 al año · señal en el 50 % de los días
  duración mediana       139 minutos
  acierto                46,6 %
  neto                   -0,090 pips por operación  ->  -4 EUR/mes
  pasar las DOS fases    38,1 %   ·  mediana 59 días
  muerte por límite diario   0,0 %
```

**Esperanza cero.** No te va a dar 300 €/mes: la ventaja bruta de esta señal es
de **medio pip** y el peaje normal cuesta **siete décimas**.

Pero ese **38,1 % de pasar las dos fases es la cifra más alta de todo el
proyecto**, y no viene de ninguna ventaja: viene de la regla de las 2 pérdidas y
del 1,00 %.

### Todo sigue colgando de tu peaje

```
  coste 0,3 pips  ->  +0,310 pips/op  ->  +14 EUR/mes
  coste 0,5 pips  ->  +0,110 pips/op  ->   +5 EUR/mes
  coste 0,7 pips  ->  -0,090 pips/op  ->   -4 EUR/mes   (mi supuesto)
  coste 1,0 pips  ->  -0,390 pips/op  ->  -18 EUR/mes
  coste 1,4 pips  ->  -0,790 pips/op  ->  -37 EUR/mes
```

**Mídelo antes de empezar**: abre una compra mínima, ciérrala al instante,
apunta la pérdida en pips. Cinco veces, a distintas horas. Si te sale por
debajo de 0,5 pips, dímelo y reoptimizo la rejilla con tu número.

---

## 4 · LAS RACHAS, PARA QUE NO TE PILLE

```
  por OPERACIÓN   acierto 46,6 % · racha de pérdidas mediana 2 · p90 5 · PEOR 23
  por DÍA         52 % en verde  · racha de días rojos mediana 2 · p90 4 · PEOR 14
```

**Veintitrés pérdidas seguidas pasaron una vez en 5,7 años.** Catorce días
rojos seguidos, también. Van a volver a pasar. Con la regla de las 2 pérdidas
esos días se te hacen cortos, que es justo para lo que está.

---

## 5 · LA RUTINA, DE PRINCIPIO A FIN

```
  1  Gráfico EUR/USD en 15 minutos. EMA20, Bollinger(20; 1,5), RSI(14).
  2  Esperas a que una vela cumpla las CUATRO condiciones.
  3  Entras en la apertura de la siguiente. Stop 15 pips. Objetivo: la EMA20
     donde estaba al dar la señal.
  4  Lo apuntas en la hoja ANTES de saber cómo acaba.
  5  No la tocas. Sale por stop, por objetivo, o a las 16 horas.
  6  Si llevas 2 pérdidas seguidas hoy -> cierras la plataforma hasta mañana.
  7  Nunca dos posiciones a la vez.
```

### El registro

```
  fecha · hora · dirección · RSI · entrada · stop · objetivo · resultado
```

Y la segunda hoja: **las señales que aparecieron y no tomaste**, con el motivo.
Con 172 operaciones al año llegas a 100 en siete meses; apuntando también las
descartadas, mucho antes. Ahí es donde puedo medir si tu criterio aporta algo
por encima de tomarlas todas, que es lo único del proyecto que sigue sin medir.
