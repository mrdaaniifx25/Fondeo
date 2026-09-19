# La corrección por comparaciones múltiples · y qué queda en pie

Prueba hecha contra mi propio resultado, sin que nadie la pidiera.

## El problema

He mirado **65 celdas únicas** del SMC-71 (instrumento × temporalidad ×
variante). La mejor, EURUSD M30, dio z +3,01 y R neta +0,093.

    si NINGUNA celda tuviera ventaja, el z máximo de 65 celdas sería
    2,56 de mediana

    P(alguna celda con z >= 3,01 por puro azar entre 65) = 15,6 %

**EURUSD M30 es exactamente lo que produce mirar 65 celdas sin ventaja.**
No es evidencia de nada.

Y peor: de las 89 celdas, **37 dan R neta positiva. Por azar se
esperarían 44.** Los netos, en conjunto, son ligeramente PEORES que el
azar.

## Pero esto es distinto, y sí queda en pie

Un resultado AGRUPADO no es una celda elegida. Usa todo y da una sola
cifra, así que no hay comparación que corregir:

    M15 · los 6 instrumentos juntos   n=2331   R bruta +0.166   z +4.90
    M30 · los 6 instrumentos juntos   n=1290   R bruta +0.155   z +3.42

Eso NO se explica por selección. Ahí no elegí nada: están todos.

## El estado real del conocimiento, después de dos meses

    1. La señal del SMC-71 es REAL en bruto. z +4,90 sobre 2.331
       operaciones sin seleccionar nada.

    2. NINGUNA configuración concreta rentable está demostrada. Todas las
       celdas con neta positiva que he encontrado caen dentro de lo que
       produce elegir la mejor de 65.

    3. La señal vale +0,155 a +0,166 R. El coste vale ~0,15 R.
       **Son del mismo tamaño.**

## Por qué esto contesta a "no me creo que ninguna funcione"

Las estrategias que circulan no fallan por no contener señal. Fallan
porque **la señal que contienen es del tamaño del coste de operarla.**

Eso explica a la vez todo lo que se ve por ahí:

    - gente que cree de verdad en su método, porque el bruto SÍ funciona
      y en un backtest sin spread sale precioso
    - capturas de retiradas auténticas, porque el 24 % de una población
      con ventaja cero llega a retirar al menos una vez
    - y cuentas que mueren igual, porque el neto es cero

No hace falta ninguna conspiración ni ningún mercado impredecible. Basta
con que el coste y la ineficiencia sean del mismo orden, que es
exactamente lo que la teoría predice: si la ineficiencia fuera mayor,
alguien la habría arbitrado hasta aquí.

## Lo que queda

Una sola palanca, y no es de mercado: **bajar el coste.** Es la única
variable de las tres -señal, coste, frecuencia- que no depende de
encontrar nada nuevo.
