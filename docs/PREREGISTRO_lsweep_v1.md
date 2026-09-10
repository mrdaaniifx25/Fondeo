# Preregistro · EUR/USD London Liquidity Sweep V1

Sellado ANTES de medir. Código en `bt/lsweep_v1.py`. EURUSD M1,
2020-01 → 2026-07, hora Europe/London. Un solo pase.

## Por qué esta especificación merece un trato distinto

Es la primera que me llega con:

    · prohibicion EXPLICITA de look-ahead (regla 29), con ejemplo
    · swings definidos mecanicamente (3 velas), sin subjetividad
    · desplazamiento medible: Body/Range >= 0,50
    · filtro de RR >= 2 ANTES de entrar
    · filtro de rango asiatico 10-35 pips
    · orden obligatorio del setup, con 20 condiciones de NO TRADE
    · regla de no-optimizacion prematura (34)
    · coste fijo declarado antes y prohibido cambiarlo despues (24)

No hay casi nada que inventar. Eso ya la separa de todo lo anterior.

## Lo que la especificación NO cubre · declarado antes de medir

1. **Noticias (regla 22).** No tengo calendario macro de 2020-2026. **No la
   implemento.** Mitigante: la ventana 07:30-10:30 Londres deja fuera casi
   todo lo grande (NFP y CPI de EE.UU. a las 13:30, FOMC a las 19:00, tipos
   del BCE a las 13:15). Lo que sí cae dentro es el CPI de la zona euro
   (10:00) y datos alemanes. **Esto sesga los resultados A FAVOR de la
   estrategia**, porque las operaciones que ella evitaría aquí sí cuentan.

2. **Vida de la orden limitada.** No se dice. La regla 23 dice "fuera de
   07:30-10:30 NO TRADE". Pruebo las **dos** lecturas: la orden debe llenarse
   antes de las 10:30, o puede llenarse hasta las 12:00.

3. **Previous Day High/Low.** Uso el máximo y mínimo del día hábil anterior
   completo, 00:00-24:00 hora de Londres.

4. **"La primera FVG válida creada por el desplazamiento que produjo el MSS".**
   Lo implemento como el trío de velas centrado en la vela del MSS
   (MSS-1, MSS, MSS+1), que es la lectura estándar. Se evalúa cuando cierra
   MSS+1, nunca antes.

## Dos redundancias de las reglas, que conviene señalar

- **El daily stop de -1 % no puede activarse nunca.** Con 0,25 % de riesgo y
  máximo 2 operaciones al día, el peor día posible es -0,5 %.
- **"+2R y se acaba el día"** sí muerde, y mucho: como el RR mínimo es 2, la
  PRIMERA ganadora ya cierra el día. En la práctica la regla es: *máximo 2
  operaciones, y se para tras la primera que gane.* Lo implemento así.

## Coste

1,43 pips fijos (spread 0,7-1,0 medido en su cuenta + comisión 5 EUR/lote).
Declarado aquí, antes de ver un solo resultado, y **no se toca después**, como
exige la regla 24.

## Los cinco criterios de éxito, firmados

    1  expectativa BRUTA positiva, z > 2
    2  expectativa NETA positiva tras 1,43 pips
    3  bate a entradas al azar en la misma ventana y geometria
    4  al menos 250 operaciones (el pide 300-500)
    5  profit factor neto > 1,15

Operable solo si cumple las cinco.

## Mi predicción

La anterior versión de barrido asiático que medí dio **bruta negativa**
(z -2,61). Ésta se diferencia en tres cosas que podrían cambiarlo: el filtro
de rango 10-35 pips, el filtro de desplazamiento, y sobre todo **el filtro de
RR >= 2**, que descarta los setups cuyo objetivo está cerca.

Firmo que **el filtro de RR será el que más mueva el resultado**, y que el
número de operaciones se quedará **por debajo de 300**, o sea por debajo de lo
que él mismo pide como muestra mínima.
