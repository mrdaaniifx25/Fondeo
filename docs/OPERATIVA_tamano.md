# El tamaño de la posición · lo único accionable que sale de dos meses

Nace de sus tres operaciones en real (sin cuenta) del 8 y el 10 de septiembre de
2026, leídas de sus capturas de TradingView.

## El hallazgo

TradingView calcula el R:R midiendo distancias en el gráfico. **No conoce su
spread ni su comisión.** Con stops de 3 pips esa omisión no es un detalle: es la
mitad del resultado.

| su operación | stop | objetivo | R:R que ve | **R:R real** | acierto necesario |
|---|---|---|---|---|---|
| jue 10 sep · venta | 2,8 p | 5,7 p | 2,04 | **1,01** | **49,8 %** |
| mar 08 sep · venta | 3,7 p | 7,4 p | 2,00 | **1,16** | **46,2 %** |

En euros, con 150 € de riesgo y la del jueves: cada pip le vale 53,57 €, abrir y
cerrar le cuesta 76,61 €, y entonces **gana 228,75 € si acierta y pierde 226,61 €
si falla.** Cree que juega un 1:2 y juega un 1:1.

## La corrección

El coste en pips es **siempre 1,43**, tenga 1 lote o 10 — subir lotes sube el
coste en euros exactamente igual que sube el beneficio. Lo único que cambia la
proporción es **cuántos pips mide el stop**.

| stop | coste/riesgo | 1:2 real | acierto necesario | lotes con 150 € |
|---|---|---|---|---|
| 2,8 p | 51,1 % | 0,99 | 50,4 % | 6,23 |
| 6 p | 23,9 % | 1,42 | 41,3 % | 2,91 |
| **7 p** | 20,4 % | **1,49** | **40,1 %** | **2,49** |
| 8 p | 17,9 % | 1,54 | 39,3 % | 2,18 |
| 10 p | 14,3 % | 1,62 | 38,1 % | 1,74 |

**Recomendación: stop mínimo 7 pips, objetivo al doble.** No 15 — los 15 pips que
propuse antes se cargaban su regla (`PINE_su_regla.md`: pasa el 2,4 % de las
señales y el acierto cae al 26,6 %). Siete es el doble de lo que hace ahora, no
cinco veces.

## Por qué 7 y no más

Recorrido medido de su ventana 08:00-11:30, EURUSD, 1.725 días:

```
percentil 25   22,7 pips
mediana        30,6 pips
percentil 75   42,2 pips
```

Un objetivo de 14 pips es la mitad del recorrido mediano: se pide. Uno de 40 no.

Y desde un minuto **cualquiera** de la ventana, el precio recorre 12 pips a favor
antes del cierre de sesión el **33,6 %** de las veces; 16 pips, el 23,8 %. Ése es
el listón del azar. Con stop de 6 pips y objetivo de 12 necesita el 41,3 %, o sea
que su criterio tiene que aportar unos **8 puntos** sobre entrar a ciegas.

Es el primer número concreto que este proyecto le pone por delante para batir.

## La regla operativa

```
riesgo fijo          150 €   (nunca se toca)
stop                 donde diga el gráfico, MÍNIMO 7 pips
objetivo             al doble de pips que el stop
lotes                17,4 ÷ pips de stop
```

El 17,4 sale de 150 € ÷ 8,60 €/pip por lote. Con 100 € de riesgo la constante es
11,6.

**Aviso en MT5:** da **puntos**, no pips. En EURUSD 1 pip = 10 puntos; 70 puntos
son 7 pips.

## Lo que esto NO es

No es ventaja. Es dejar de regalar la mitad del riesgo, que es distinto. Si
debajo su criterio no vale nada, con stops de 7 pips perderá más despacio en vez
de deprisa. Sigue sin estar medido si su criterio aporta algo — eso es
`PREREGISTRO_criterio.md`, escrito y nunca ejecutado.

Pero es lo único de estos dos meses que puede cambiar mañana y que es aritmética,
no opinión.

## Herramientas

- `docs/calculadora_lotaje.html` — mete entrada y stop, da los lotes, el objetivo
  y el aviso rojo por debajo de 7 pips.
- `docs/registro_operaciones.html` — registra cada operación antes de saber cómo
  acaba, y también las que ve y deja pasar. Guarda la hora en que se apunta.
