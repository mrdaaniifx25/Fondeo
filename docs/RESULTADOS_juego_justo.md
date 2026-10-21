# Resultado · el juego justo

Pre-registro: `docs/PREREGISTRO_juego_justo.md`, escrito **antes** de medir.
Código: `bt/juego_justo.py`, `bt/juego_justo2.py`, `bt/juego_justo_tres.py`.

---

# Veredicto: **llevo tres meses midiendo mal el problema**

Cada vez que algo salía negativo lo conté como «no funciona». Al poner los
veinte resultados en la misma tabla se ve que **el negativo era el
diferencial**, no la apuesta.

```
  coste (% del riesgo)     1,0 %   1,4 %   1,9 %   2,9 %   5,7 %
  neto medido             -0,008  -0,003  -0,021  -0,023  -0,041
```

El neto **es** el coste, con el signo cambiado. El bruto es cero en las veinte
celdas.

---

## 1 · La rejilla completa

Una operación al día, apertura de Londres, objetivo 2R, salidas resueltas
minuto a minuto, coste 1,0 pip ida y vuelta, empates resueltos como pérdida.
**n = 2.914** (los dos lados de 1.457 días).

```
            stop  tope     n  coste/rgo  %barrera   %obj    bruto     neto      z
   0.25xATR(18p)     1  2914     0.0573     98.6%  33.2%   0.0160  -0.0414  -1.58
   0.25xATR(18p)     5  2914     0.0573    100.0%  33.9%   0.0161  -0.0412  -1.57
   0.50xATR(35p)     2  2914     0.0287     88.1%  27.2%  -0.0033  -0.0320  -1.30
   0.50xATR(35p)    20  2914     0.0287    100.0%  33.3%  -0.0018  -0.0305  -1.16
   0.75xATR(53p)     5  2914     0.0191     86.4%  26.5%  -0.0023  -0.0214  -0.87
   1.00xATR(71p)     5  2914     0.0143     67.3%  18.0%   0.0114  -0.0029  -0.13
   1.00xATR(71p)    20  2914     0.0143     98.0%  32.8%   0.0151   0.0007   0.03
  1.50xATR(106p)    20  2914     0.0096     83.8%  25.0%  -0.0006  -0.0101  -0.42
```

**El bruto no se separa de cero en ninguna celda** (rango −0,0144 a +0,0175, con
un error estándar de 0,022-0,026). Y con el stop ancho, **el neto tampoco**:
`1,00 x ATR · tope 20` da **+0,0007 R con z +0,03** sobre 2.914 operaciones.

Eso es un **juego justo**. No una pérdida.

## 2 · Y no es el espejo

A+B juntos tienen que dar cero casi por construcción, así que eso solo es un
control del motor. La prueba de verdad es que **ningún lado y ninguna dirección
se separa solo**:

```
  stop 1,00 x ATR (71 pips) · tope 5 dias · coste 1,43 % del riesgo
    brazo                              n  acierto    bruto     neto      z
    A · compra ciega                1457    40.6%  -0.0129  -0.0273  -0.89
    B · venta ciega                 1457    42.3%   0.0358   0.0215   0.68
    C · momento 12 meses            1222    41.0%   0.0194   0.0055   0.16
    E · continuacion dia ant.       1456    40.2%  -0.0079  -0.0222  -0.72
    F · reversion dia ant.          1456    42.6%   0.0300   0.0157   0.50
```

Cinco brazos, todos dentro de |z| < 0,9. **Ninguna dirección mecánica es mejor
que otra.** Eso tiene una lectura que no es mala: elegir dirección es gratis.

## 3 · La potencia, que es lo nuevo

Con n = 2.914 el error estándar es **0,022 R**.

```
  detecta                              +0,044 R  a z = 2
  ventaja que necesita para 300 EUR/mes +0,149 R  ->  saldria a z = 6,8
```

**Es la primera prueba del proyecto con potencia para zanjarlo.** No es «no he
encontrado nada»: una ventaja del tamaño que él necesita, a horizonte diario,
en este instrumento, con estas reglas, **queda excluida**. Y a la vez queda
establecido que el juego es justo, que es cosa distinta de estar perdido.

## 4 · Tres instrumentos son tres apuestas

```
  instrumento      n  coste/rgo  acierto    bruto     neto      z
  eurusd        2914     0.0143    41.4%   0.0114  -0.0029  -0.13
  xauusd        1862     0.0098    42.1%   0.0342   0.0244   0.87
  grxeur        1814     0.0151    39.5%  -0.0260  -0.0410  -1.46

  correlacion de resultados diarios (compra ciega)
          eurusd  xauusd  grxeur
  eurusd   1.000   0.291   0.185
  xauusd   0.291   1.000   0.204
  grxeur   0.185   0.204   1.000
```

Correlaciones de 0,19 a 0,29: **bajas.** Tres instrumentos dan tres apuestas
casi independientes sin apilar riesgo en el mismo par. Y eso, por la rejilla de
`RESULTADOS_lo_simple.md`, mueve la aprobación del examen de **26,2 % (una
operación al día) a 35,5 % (tres al día)**.

Nueve puntos de aprobación, sin ninguna ventaja. Sólo por no concentrar.

## 5 · La trampa del oro, que hay que decir

```
  instrumento lado         n    bruto     neto      z
  xauusd      compra     931   0.2751   0.2653   6.36
  xauusd      venta      931  -0.2067  -0.2164  -6.09
  grxeur      compra     907   0.0971   0.0820   2.04
  grxeur      venta      907  -0.1490  -0.1641  -4.22
```

**z +6,36 comprando oro.** Y no vale nada como estrategia: es **deriva**. El oro
subió un 143 % en esta ventana y el DAX un 573 %. Comprar algo que sube no es
una ventaja de entrada, es la prima de riesgo, y `RESULTADOS_rejilla_indicadores.md`
ya estableció que **nada bate a comprar y mantener**.

Lo honesto: la prima de riesgo **es** lo único con esperanza positiva y
mecanismo real en todo este proyecto. Pero su tamaño esperado no es +0,2653 —
eso es la ventana — sino del orden de **+0,015 R por operación** para una bolsa
con prima del 5 % anual. Una décima parte de lo que él necesita.

En EUR/USD, sin deriva, el lado largo da **−0,0273**. Es la prueba de que el
+0,2653 del oro es el activo, no el método.

---

## 6 · Lo que esto cambia, en una frase

No ha estado perdiendo porque sea malo ni porque el mercado le tenga algo
guardado. **Ha estado pagando el diferencial.** El vídeo de la cascada se
dejaba el **66,8 % del riesgo** en coste; con un stop de 71 pips el coste es el
**1,4 %**, cuarenta y siete veces menos, y lo que queda es una moneda honrada
con pago 1:2 que puede lanzar todos los días.

Un juego justo no da 300 €/mes. Pero sí da **35 % de pasar un examen que le
salió gratis**, y sí se puede jugar con la cabeza tranquila, que es lo que
pedía.

## 7 · Y lo que tiene que esperar, para poder estar tranquilo

Con 36 % de acierto, medido sobre sus propias rachas:

```
  racha de perdidas: mediana 3 · p90 8 · PEOR observada en 5,7 anios: 23
  peor racha en 100 operaciones: mediana 8 · p90 13 · p99 18
  P(al menos una racha de 8 seguidas en 100 operaciones): 67 %
```

**Perder ocho seguidas le va a pasar, con un 67 % de probabilidad, en las
primeras cien operaciones.** No significa que algo se haya roto. Significa que
el acierto es 36 % y que así se ven el 36 % de acierto. Saberlo de antemano es
la diferencia entre aguantar el plan y abandonarlo en la racha.
