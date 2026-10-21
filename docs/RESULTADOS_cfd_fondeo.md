# Corrección · no hacía falta cambiarse a futuros

Código en `bt/cfd_fondeo.py`. Misma disciplina que el pase de futuros:
geometría ajustada en **2020-2023**, comprobada en **2024-2026**.

## Lo que dije mal

Le dije que se pasara a futuros porque "la cuota es 4,4 veces más barata,
una sola fase y hacen falta 15 victorias seguidas en vez de 33".

**Ese cálculo estaba hecho para la geometría equivocada.** Suponía la familia
de alto acierto y cola catastrófica, que es la que usa el psicólogo del
trading. Y el pase de `docs/RESULTADOS_alto_winrate.md` demostró que esa
familia no tiene ninguna de las ventajas que le atribuí: con coste es peor
que un 1:1, sufre más el drawdown dinámico, y la regla de consistencia no
discrimina.

Con la geometría correcta -la que sale de optimizar barreras, no acierto- el
reto de CFDs de dos fases da lo mismo que el de futuros.

## Los números

US100, compra ciega a las 09:35 NY, una al día, reglas de FundingPips
(fase 1 +8 %, fase 2 +5 %, límite diario 5 %, límite total 10 %, 60 días):

    stop 108 pts · TP 108 pts · riesgo 3 % por operación

    ajuste 2020-2023        37,0 %
    FUERA de muestra        36,9 %      fase 1  56,7 %   fase 2  65,0 %
    techo teórico sin ventaja  37,0 %
    mediana                 13 días de operativa
    correlación ajuste-fuera sobre 150 celdas   +0,939

**Toca el techo teórico exactamente.** Con ventaja cero, `10/(8+10)` por
`10/(5+10)` = 37,0 %. Se saca 36,9 %. No sobra nada y no falta nada.

Comparado con la evaluación de futuros medida el día anterior:

    futuros (MNQ)   P(pasar)  34,4 %
    CFD  (US100)    P(pasar)  36,9 %

**Los CFDs no son peores. Son ligeramente mejores**, porque la geometría de
dos fases al 8 % y 5 % con un tope del 10 % es más generosa que 3.000 $
contra 2.000 $.

Sensibilidad al coste del US100, que sigue sin ser un dato suyo:

    1 punto   ->  38,8 %        2 puntos  ->  36,9 %        4 puntos  ->  32,6 %

La geometría ganadora es la misma (108/108 al 3 %) en los tres casos.

## La economía del boleto

La cuenta fondeada, modelada como otro problema de barreras: retira cuando
toca +5 %, muere al -10 %, reparto 80 %.

    retiradas por cuenta fondeada:  media 1,99   ·   33 % no retira nunca

    cuenta    cuota   por retirada   esperado   EV boleto   x cuota   13 boletos
      5.000      49            200        147        +98      3,0x        637
     10.000      89            400        294       +205      3,3x      1.157
     25.000     189          1.000        734       +545      3,9x      2.457
     50.000     349          2.000      1.468     +1.119      4,2x      4.537
    100.000     549          4.000      2.936     +2.387      5,3x      7.137

Esperanza positiva en todos los tamaños, entre 3 y 5 veces la cuota. Y el
número de boletos para tener un 90 % de acabar en verde **no depende del
tamaño**: son 13, porque solo depende de P(pasar) = 37 %.

Así que el capital que hace falta es 13 x cuota. Con 80 € se compra **un**
boleto de 49 €: 63 % de perderlo, 37 % de una cuenta con 294 € de valor
esperado.

## Lo que sigue siendo verdad

Nada de esto es una ventaja. La esperanza por operación de la celda ganadora
es **+0,007 R**, o sea cero. Pasa el reto el 37 % de las veces por la
posición de las barreras, no por acertar.

Y por eso pasar un reto no demuestra nada, ni suyo ni de nadie.

## Lo que falta

    1  su cuota exacta y el tamaño de cuenta
    2  el spread real del US100 en su cuenta (lo pregunté siete veces)
    3  el reparto de beneficios y el mínimo de retirada
