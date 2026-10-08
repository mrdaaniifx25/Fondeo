# Resultado · la familia "alta tasa de acierto / cola catastrófica"

Preregistro sellado en `a9b6fe8`, antes de medir. Código en
`bt/alto_winrate.py`, `bt/alto_winrate_analisis.py`, `bt/alto_winrate_anios.py`.
Un solo pase. 216 celdas: 2 índices x 3 entradas x 12 geometrías x 3 tamaños.
1.691 sesiones de NASDAQ y 1.692 de SP500, 2020-01 → 2026-07.

## Dos correcciones que hubo que hacer sobre la marcha

1. **Marcado a mercado.** La primera versión daba 0 puntos a la operación que
   no tocaba ninguna barrera y se cerraba al final de la sesión. Eso es una
   opción gratis, y es falso: si estás plano a las 15:55 te llevas el precio
   que haya. Corregido — cambia todos los números de las celdas de stop ancho.
2. **La barra de entrada.** Entrando a la apertura de las 09:35 no se puede
   empezar a mirar en la barra siguiente: esa barra ya cuenta. Con TP pequeños
   el sesgo era brutal (el acierto de 1:30 pasó de 87,9 % a 95,5 %).

Ambas se descubrieron comparando el acierto observado con el geométrico. El
control funcionó como control.

## Las cinco predicciones firmadas: 2 aciertan, 3 fallan

### 1 · el acierto observado no bate al geométrico — **SE CUMPLE**

En las 44 celdas donde la prueba es válida (resuelven ≥ 94 % de las veces):

    desviación media respecto de SL/(SL+TP)   -0,86 pp
    celdas de COMPRA que la baten en > 2 pp        0

El acierto de una estrategia sin señal es exactamente `SL/(SL+TP)`. 50 %,
75 %, 90,9 %, 96,8 %. Medido, no supuesto.

En las 28 celdas de baja resolución el acierto sí parece batirla (+1,71 pp de
media). **Es un artefacto**, no una ventaja: al cortar la sesión a las 15:55 se
truncan más operaciones camino del stop lejano que camino del TP cercano. No
lo había anticipado en el preregistro; lo digo aquí.

### 2 · la esperanza neta por operación será negativa — **SE CUMPLE**

    210 de 216 celdas con esperanza neta negativa   =   97,2 %

### 3 · con drawdown estático da igual la geometría — **NO SE CUMPLE**

Predije que el teorema de la barrera lo aplastaría todo. Es al revés: la
geometría importa muchísimo. P(pasar), sin coste, drawdown estático:

    TP:SL       phi=0,20   phi=0,50   phi=1,00
    ------------------------------------------
      1:1         38,7 %     40,9 %     29,6 %
      1:3         22,2 %     37,3 %     41,0 %
      1:10         3,1 %     24,8 %     36,7 %
      1:30         0,0 %      6,3 %     25,0 %

(`phi` = cuánto vale la pérdida en fracción del drawdown entero)

El techo teórico es `DD/(objetivo+DD) = 2000/5000 = 40 %`, y **se alcanza**:
40,9 % y 41,0 %. Pero solo en una franja estrecha. Fuera de ella se cae:
el 1:30 con stop pequeño da 0,0 % porque haría falta pasar de 200 días
ganando de 13 $ en 13 $.

**La conclusión práctica es la contraria de la que firmé, y es útil:** para
acercarse al 40 % hay que casar el tamaño con la geometría. 1:1 arriesgando
medio drawdown, o 1:3 arriesgando el drawdown entero. Cualquier otra cosa
tira probabilidad a la basura.

### 4 · el drawdown dinámico favorece al alto acierto — **NO SE CUMPLE**

Era mi hipótesis central sobre por qué existe esta familia. Es falsa.
Diferencia dinámico menos estático, en puntos porcentuales:

    TP:SL       phi=0,20   phi=0,50   phi=1,00
    ------------------------------------------
      1:1        -11,0      -9,5       -5,6
      1:3         -3,9     -10,5       -8,8
      1:10        -0,0      -5,9       -9,9
      1:30        -0,0      -0,2       -6,4

El castigo es parejo, y con stop grande es **mayor** en las de alto acierto,
no menor. El mecanismo que no vi: la escalera suave no protege de nada,
solo hace que el máximo esté más alto cuando llega el hachazo. Y el drawdown
dinámico mide justo desde ese máximo.

### 5 · la regla de consistencia mata más al bajo acierto — **NO SE CUMPLE**

Coste de la regla del 40 %, aislado (sin coste, drawdown estático):

    alto acierto (1:10, 1:30)    -0,4 pp
    bajo acierto (1:1, 1:3)      +1,1 pp

Da igual. La regla no discrimina. Predije 10 pp de diferencia y no hay
ninguna.

**Balance: la familia de alto acierto no tiene ninguna de las tres ventajas
estructurales que le atribuí.** No aprovecha mejor el drawdown dinámico, no
sortea la regla de consistencia, y con coste es peor que el 1:1.

## El hallazgo central, que sí es sólido

Celda NASDAQ, compra ciega a las 09:35 NY, stop 108 pts, TP 108 pts,
5 micros MNQ:

     anio     n   acierto    R neto    $ / op
     2020   258     55,8%    +0,078    +84,22
     2021   257     51,8%    -0,011    -12,15
     2022   258     50,8%    -0,006     -6,96
     2023   252     51,2%    +0,001     +1,38
     2024   259     48,6%    -0,012    -12,65
     2025   257     51,8%    +0,019    +20,50
     2026   150     52,7%    +0,050    +54,37
    TOTAL  1691     51,7%    +0,015    +16,15

**Esperanza esencialmente cero.** El +0,015 total lo pagan 2020 y los siete
meses de 2026; cinco de los siete años están en el ruido. No hay ventaja.

Y sin embargo:

    con TODOS los años (2020-2026)   P(pasar) estático 42,8 %   dinámico 33,0 %
    con SOLO 2024-2026               P(pasar) estático 42,5 %   dinámico 32,4 %

**Una estrategia con esperanza cero pasa la evaluación un 33-43 % de las
veces, y ese número no se mueve al cambiar de periodo.** Porque no depende
de la señal. Depende de dónde están las dos barreras.

Es la misma conclusión que dio `bt/reto_montecarlo.py` para el reto de CFDs
(36,6 % de cuentas fondeadas con ventaja cero), llegando desde otro sitio.
**Pasar una evaluación no demuestra absolutamente nada.**

## El muro del coste, en su forma más extrema

La celda de 1:30 en SP500 es el caso límite y merece decirse solo:

    stop 11,5 pts   ·   TP 0,38 pts   ·   coste ida y vuelta 0,80 pts

El objetivo es **la mitad de lo que cuesta abrir y cerrar**. Acierta el
95,6 % de las veces y pierde dinero en el 100 % de las operaciones ganadoras.
Ese es el muro del coste sin ningún disfraz.

En general: el TP tiene que ser grande frente al coste, el stop tiene que ser
grande frente al drawdown, y las dos cosas juntas obligan a un TP:SL entre
1:1 y 1:3. Ahí es donde vive todo lo que funciona, y no es donde vive la
familia de alto acierto.

## La esperanza del boleto

Asumiendo cuota 80 € y 1.823 € de ganancia media por cuenta pasada (el dato
real medido del psicólogo del trading, 13 cuentas de 78 evaluaciones):

    P(pasar)   EV por boleto   pago que hace falta   evaluaciones para
                                para no perder       90 % de acabar en verde
    --------------------------------------------------------------------
    33,6 %      +532 EUR            238 EUR           6   (480 EUR)
    16,7 % (*)  +224 EUR            480 EUR          13  (1.040 EUR)

    (*) su tasa real observada, no la simulada

La simulación da 33,6 % y él observó 16,7 %. La diferencia es lo que la
simulación no modela: límite de pérdida diaria, ejecución humana, y que él
opera lo que opera. **Usa el 16,7 %, no el 33,6 %.**

El EV es positivo y con mucho margen: haría falta que una cuenta pasada
rindiera menos de 480 € para que el boleto fuera perdedor, y rinden 1.823 €.
**Lo que no aguanta no es la esperanza: es la varianza.** Con 13 boletos hay
un 90 % de acabar en verde. Con uno, hay un 83 % de perderlo.

## Lo que este trabajo NO dice

No dice que esto sea una estrategia rentable. Su esperanza por operación es
cero o negativa **por construcción**, y en cuenta propia arruina.

No dice que el 33 % simulado sea alcanzable: no tengo las reglas exactas de
ninguna prop firm de futuros suya. Objetivo 3.000 $, drawdown 2.000 $,
5 días mínimos y consistencia al 40 % son **asunciones declaradas** de una
cuenta 50K genérica.

El coste (1,20 pts en MNQ, 0,80 en MES) también es asunción mía, no dato
suyo. La sensibilidad está medida y publicada abajo.

## Sensibilidad al coste · y por qué esto cierra el debate

P(pasar) con drawdown dinámico, media por geometría, con el coste a la mitad,
al asumido y al doble:

    TP:SL   phi   x0,5     base     x2
    ------------------------------------
      1:1   0,50  28,6 %   27,0 %  23,8 %      <- aguanta
      1:3   1,00  30,4 %   27,1 %  22,9 %      <- aguanta
     1:10   1,00  20,2 %   14,2 %   8,3 %      <- se hunde
     1:30   1,00   7,6 %    3,5 %   1,1 %      <- desaparece

Y la celda concreta que recomiendo, NASDAQ 1:1 con 5 micros:

    coste x0,5   neto +22,15 $/op   P(pasar) 43,5 / 33,0 %
    coste base   neto +16,15 $/op   P(pasar) 42,2 / 33,6 %
    coste x2     neto  +4,15 $/op   P(pasar) 40,7 / 31,3 %

Doblar el coste le quita **dos puntos** de probabilidad de pasar. Al 1:30 le
quita el 69 % de lo que tenía.

La razón es de una línea: en el 1:1 el objetivo son 108 puntos y el coste
1,2 — el coste es el 1,1 % del objetivo. En el 1:30 el objetivo son 3,6
puntos y el coste 1,2 — es el 33 %.

**Por eso el "más del 90 % de acierto" no es la parte que funciona del
arbitraje de fondeo. La parte que funciona es que la pérdida está topada en
la cuota.** Y para eso vale cualquier geometría; de hecho vale mejor 1:1.
