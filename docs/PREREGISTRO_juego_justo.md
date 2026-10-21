# Pre-registro · el juego justo

Firmado **antes** de medir.

## Por qué este test y no otro

Llevo tres meses midiendo mal el problema. He estado buscando **ventaja**, y
cada vez que algo salía negativo lo he contado como «no funciona». Pero al
mirar los números juntos, casi todos los negativos tienen la misma forma:

```
  bruto  ~ 0,00     (el mercado valora la geometría EXACTAMENTE)
  neto   ~ -coste   (lo que se perdía era el diferencial, no la apuesta)
```

El vídeo de la cascada: bruto −0,045, **coste 66,8 % del riesgo**. El CRT
clásico en M15: stop de 8,9 pips sobre una referencia de 5-8 pips. El muro del
coste medido por horizonte: EUR/USD a 1 hora **0,1076** del riesgo, a 1 día
**0,0226**, a 1 mes **0,0053**.

**La pregunta que no he hecho nunca**: si el coste baja al 1 % del riesgo en
vez del 67 %, ¿qué queda? Si el bruto es cero de verdad, queda un **juego
justo**: una moneda con pago 1:2 que se puede jugar todos los días.

## Las reglas, congeladas

```
  instrumento   EUR/USD M1 del repositorio, 2021-2026
  una operación al día como máximo
  entrada       a mercado en la apertura de Londres (08:00 Madrid)
  stop          1,5 x ATR(14) DIARIA   (~100 pips -> coste = 1 % del riesgo)
  objetivo      2R
  tope          3 días hábiles, después a mercado
  coste         1,0 pip ida y vuelta (ECN, conservador)
  salidas       resueltas minuto a minuto con el M1
```

Brazos, todos con el mismo stop y el mismo objetivo:

```
  A  compra ciega todos los días
  B  venta ciega todos los días
  C  dirección del momento de 12 meses
  D  dirección del canal de 20 días
  E  continuación: dirección del día anterior
  F  reversión: contra el día anterior
```

## Lo que declaro antes

1. **A y B deben dar bruto ≈ 0 y neto ≈ −0,01 R.** Si dan eso, el juego es
   justo y el coste deja de ser el problema. Si A o B dan bruto muy distinto de
   cero, hay deriva y hay que descontarla.
2. **A + B deben sumar ≈ 0** por construcción (son el mismo mercado en espejo).
   Es el control de consistencia del motor.
3. **Espero que C, D, E y F no se separen de A/B más de lo que permite el
   ruido.** Sería coherente con todo lo medido hasta ahora.
4. **La potencia es lo nuevo.** Con ~1.400 días, el error estándar de una
   apuesta con pago 2R es 1,41/√1400 = **0,038 R**. Detecto +0,075 R a z = 2.
   Y la ventaja que necesita para 300 €/mes sobre 10.000 es **+0,149 R**: si
   existiera, este test la vería a **z ≈ 4**.

   **Es la primera prueba del proyecto con potencia suficiente para zanjarlo a
   horizonte diario.** No «no he encontrado nada»: o aparece, o queda excluida
   de verdad.

## El criterio, declarado antes

- Si algún brazo da neto ≥ +0,075 R con z ≥ 2 → hay algo que medir en serio.
- Si todos quedan dentro de ±0,075 → **el juego es justo y eso es el
  resultado**, no un fracaso. Un juego justo con 1:2 y tamaño correcto da
  35,8 % de aprobar el examen, se puede jugar casi todos los días, y la
  racha de pérdidas esperada es calculable de antemano.

## Lo que además mido, porque es para su cabeza y no para el paper

La distribución de rachas de pérdidas con acierto ~36 %: cuántas seguidas es
normal, y cuál es la peor que debe esperar en 100 operaciones. Operar tranquilo
exige saber eso antes, no descubrirlo en la racha.
