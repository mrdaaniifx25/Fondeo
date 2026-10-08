# Resultados · ¿se puede vivir del fondeo con este sistema?

Pregunta del usuario: *«mínimo necesito 300 €/mes… no puede ser imposible pasar
una cuenta de fondeo sabiendo lo que se hace»*. Código: `bt/carrera_fondeo.py`.
Rendimientos por remuestreo de los **632 meses medidos** de
`RESULTADOS_momento_largo.md` + `RESULTADOS_carry.md`. 20.000 carreras de 3 años.

## Tiene razón en lo primero

Pasar un reto es un problema de barreras, igual que una operación:

```
  fase 1   +8 % antes de -10 %   ->  P = 10/(10+8) = 55,6 %
  fase 2   +4 % antes de -10 %   ->  P = 10/(10+4) = 71,4 %
  LAS DOS                        ->  39,7 %
```

**Con habilidad exactamente cero, 40 de cada 100 pasan un reto de dos fases.**
No es imposible ni de lejos. Por eso un papel de payout no demuestra nada
(`RESULTADOS_payouts.md`), y por eso el negocio de las fondeadoras funciona.

## Lo que decide no es pasar, es el tamaño de la cuenta

Para sacar 300 €/mes con reparto 80/20:

```
   10.000 €  ->  45,0 % al año   imposible con Sharpe 1
   25.000 €  ->  18,0 % al año   imposible
   50.000 €  ->   9,0 % al año   alcanzable
  100.000 €  ->   4,5 % al año   alcanzable
```

**En una cuenta de 10.000 € sus 300 € al mes no existen.** En una de 100.000, sí.

## La carrera completa · 100.000 €, escala 2×, 3 años

Escala 2× = la peor caída histórica del sistema sería del 20 %, el doble del
límite. La simulación ya lo cuenta: la cuenta muere y se compra otro reto.

```
  percentil       neto en 3 años     €/mes
  p5                     -1.000€      -28€
  p25                    +4.483€     +125€
  p50                   +11.691€     +325€
  p75                   +19.180€     +533€
  p95                   +31.158€     +866€

  media                 +12.700€     +353€
  carreras que ganan dinero        87,6 %
  cuenta viva a los 3 años         76,7 %
  retos comprados, mediana            1   (media 1,3)
  meses hasta pasar el reto          13
  cuotas arriesgadas, media         668 €
```

**Mediana 325 €/mes. El peor 5 % pierde 1.000 €**, que son las cuotas.

## Los dos controles, que es lo que hace creíble lo de arriba

Ya hubo una simulación de fondeo en este proyecto que daba +5.758 € **con
ventaja cero** (`bt/benjamin.py`), por el efecto de retirar y dejar el límite
quieto. Había que descartar que esto fuese lo mismo.

**Control 1 · la misma carrera con la media puesta a cero:**

```
  escala        con el sistema        con ventaja CERO
   2,0x      +350 €/mes  87,5 %       +29 €/mes  29,2 %
   3,0x      +656 €/mes  95,1 %      +107 €/mes  48,2 %
```

El efecto existe —29 € al mes salen de la asimetría de la fondeadora, no del
sistema— pero es **doce veces menor**. El sistema hace el trabajo.

**Control 2 · con pérdida máxima dinámica**, medida desde el pico y no desde el
inicio, que es la regla dura y la que usan casi todas hoy:

```
   2,0x      +355 €/mes  87,5 %       +28 €/mes  28,9 %
```

**Idéntico.** El resultado no depende de la regla blanda. Ése era el riesgo y
no se materializa: como se retira cada mes, el balance casi nunca se aleja del
punto de partida y las dos reglas coinciden.

## El caso malo · sólo con los meses de 2013-2026

Sharpe +0,45 en vez de +1,00. Si el futuro se parece a los últimos trece años:

```
  escala    %/año   viva   % que gana   mediana €/mes   media €/mes
   1,0x     1,95%   20,8%      17,5%           -14€          +2€
   2,0x     3,90%   48,7%      54,6%           +28€        +113€
   3,0x     5,84%   49,9%      73,1%          +179€        +263€
```

**La horquilla honesta para 100.000 € a escala 2× es de 28 a 325 €/mes de
mediana**, según qué régimen toque. No se puede estrechar más: el tramo reciente
tiene 165 meses y su intervalo no separa un Sharpe de 0,45 de uno de 1,00.

## La condición que lo invalida todo

**Mediana de 13 meses para pasar el reto.** Un sistema mensual con un 9 % de
rentabilidad anual tarda más de un año en hacer +8 % y luego +4 %.

**Si el reto tiene límite de tiempo —30, 60 o 90 días— este sistema no lo pasa
nunca.** No es una cuestión de suerte: no da tiempo material. Es lo primero que
hay que verificar antes de pagar nada:

1. ¿El reto tiene plazo máximo?
2. ¿Se pueden mantener posiciones **durante el fin de semana**?
3. ¿Hay regla de días mínimos de operativa? (con 12 operaciones al año, puede
   incumplirse)
4. ¿La pérdida máxima es estática o dinámica? (da igual, pero conviene saberlo)
5. ¿El swap que pagan es el del mercado o lleva recargo? (se modeló 1,5 puntos)

Si las respuestas a 1 y 3 son malas, esto no sirve y hay que decirlo antes de
gastar 500 €.

## Lo que sí queda en pie

- Su intuición era correcta: **pasar no es difícil**.
- Su objetivo de 300 €/mes **es alcanzable**, pero con una cuenta de 100.000 €,
  no de 10.000.
- Con este sistema, **87,6 % de las carreras acaban en positivo** y lo que se
  arriesga son 500-1.000 € de cuotas, no la cuenta.
- El límite diario del 5 % **no es un riesgo** aquí: con un 9 % de volatilidad
  anual, un día del −5 % está a más de cinco desviaciones. Ésa es una ventaja
  real de operar lento en una cuenta fondeada.
