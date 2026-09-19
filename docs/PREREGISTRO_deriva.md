# Pre-registro · ¿predicen deriva estas señales?

Escrito y subido ANTES de medir. 19/09/2026.

## Por qué cambia el objeto

Las ~27 variantes medidas hasta hoy son todas la misma apuesta: entrar, poner
un stop y poner un objetivo. Para esa apuesta hay un teorema: en un precio
justo, la probabilidad de tocar el objetivo antes que el stop es exactamente
`riesgo / (riesgo + recorrido)`. Da igual la señal. Por eso todo cae en cero:
**no estábamos midiendo la señal, estábamos midiendo la geometría**.

Aquí se quita la geometría. No hay stop ni objetivo. Sólo:

> pasados **h** minutos desde que dispara la señal, ¿cuánto se ha movido el
> precio a favor, de media?

Dos ventajas:

1. El teorema de la barrera no dice nada de esto. Si el precio fuese un paseo
   sin memoria, la media sería 0. Si hay deriva, sale.
2. Usa el **tamaño** del movimiento, no sólo el signo. Una prueba de acierto
   tira esa información a la basura. Con 100 operaciones, detectar una deriva
   de 2 pips por la media es viable; por el acierto no.

Hay un indicio de que puede haber algo pequeño: el modelo de
`docs/RESULTADOS_barrido_ml.md` encontró bruta +0,0499 en su decil superior con
z +4,11, batiendo a los nulos 8 veces. Real pero más chico que el coste. Si eso
es deriva, aquí tiene que aparecer.

## La medición

**Sucesos.** Cada disparo es un par (instante, lado). El instante es el cierre
exacto de la vela de entrada. Señales:

| clave | señal | lado |
|---|---|---|
| `amdfvg` | caja apretada + finta + FVG de H1 (la regla corregida) | contra la finta |
| `finta` | caja apretada + finta, sin pedir FVG | contra la finta |
| `fvg` | sólo el FVG de H1, sin caja | a favor del hueco |
| `base` | todos los cierres de H1 (calibración) | alterno |

**Medida.** `r = lado × (cierre(t + h) − cierre(t))` en pips.
Horizontes h = 1, 4, 12, 24, 72, 168 horas, contadas en **filas de M1** para
saltar fines de semana.

**Coste.** 1,43 pips en EURUSD. La pregunta entera es si `media(r) > 1,43`.

**Intervalos.** Los sucesos se solapan: dos señales cercanas comparten futuro,
así que las observaciones están correlacionadas y un intervalo normal saldría
demasiado estrecho. Se usa **bootstrap por bloques de mes natural**, 10.000
remuestreos de meses con reemplazo. Es lo único honesto con datos solapados.

**Nulos**, los tres:
- N1 · lados barajados (mismos instantes, mismo reparto de lados, al azar).
- N2 · instantes al azar de todo el histórico, mismo reparto de lados.
- N3 · la señal al revés (lado invertido). Tiene que salir el espejo.

## Criterio, declarado antes de ver nada

Para decir que hay deriva aprovechable hacen falta las tres:

1. `media(r) − 1,43 > 0` con el IC95 del bootstrap **sin tocar el cero**, en
   algún horizonte.
2. El mismo signo en **al menos 2 de los 3 instrumentos** (EURUSD, oro, DAX).
3. Los tres nulos en cero, y N3 en el espejo.

Si se cumple 1 pero no 2, es un hallazgo de un instrumento y se dice así.
Si no se cumple 1, la respuesta es que no hay deriva y **se cierra esta vía**.

## Predicción

Para poder equivocarme en público:

- `media(r)` entre −1 y +1 pips en todos los horizontes cortos, con IC de
  ±2 a ±5 pips. O sea, **no se cumple el criterio 1**.
- La `base` (todos los cierres) en cero exacto, que es la calibración.
- Si algo aparece, será en los horizontes largos (72 h, 168 h) y será
  indistinguible de la deriva general del par en esos años, no de la señal.

## Lo que se hará si sale que no

Queda descartada la familia entera de «entrar por estructura en intradía» para
EURUSD, oro y DAX, no una variante más. Eso es información, no un fracaso: el
siguiente sitio donde buscar ya no es la señal, es el coste.
