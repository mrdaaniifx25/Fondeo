# Resultado · la prima de riesgo contra las barreras del reto

Preregistro sellado antes de medir. Código en `bt/prima.py`.

    US100 · 1.690 días · 2020-01 -> 2026-07
    deriva +0,0804 % diario   ·   volatilidad 1,532 %   ·   Sharpe anual +0,83
    techo con ventaja CERO:  fase1 55,6 %  ·  fase2 66,7 %  ·  las dos 37,0 %

Por el teorema del muestreo opcional, una martingala da 37,0 % haga uno lo
que haga. Superarlo exige deriva real. Esto es, por tanto, una prueba directa
de si la deriva sirve para algo.

## Las cinco predicciones firmadas: 1 acierta, 4 fallan

    1  existe un L con P(fase 1) > 55,6 %          NO   máximo 52,3 %
    2  el L óptimo será <= 2,0                     SÍ   óptimo 1,25
    3  P(las dos fases) > 37,0 %, llegando al 45 % NO   máximo 34,1 %
    4  fuera de muestra saldrá peor                SÍ (en el óptimo: 34,1 -> 31,6)
    5  el bootstrap por bloques dará 5 pp MENOS    NO   da 6,6 pp MÁS

La 5 falló al revés de lo que pensaba, y el motivo es instructivo: el
bootstrap por bloques conserva las **rachas**, y una racha ayuda a tocar un
objetivo antes que un límite. El iid las destruye. O sea que los bootstrap
iid de todo el proyecto no eran optimistas: eran conservadores.

## El resultado, con financiación al 6 %

    L      ajuste 2020-2023     fuera 2024-2026
    1,00        33,6 %               25,7 %
    1,25        34,1 %  <- óptimo    31,6 %
    1,50        31,5 %               27,2 %
    2,00        21,3 %               27,1 %
    3,00        13,3 %               13,9 %

**Nunca llega al 37,0 %.** La deriva es real, es grande (Sharpe 0,83) y no
alcanza. Ese era el criterio de fin que firmé.

## Por qué no alcanza: la regla que se la queda

Aislando cada regla, con L = 1,25:

    reglas reales (diario flotante + total)     33,7 %
    SIN límite diario, solo el total del 10 %   42,1 %     <- bate el techo
    límite medido sobre CIERRES, no flotante    40,5 %     <- bate el techo

**Sin el límite diario del 5 %, la prima de riesgo SÍ bate al azar: 42,1 %
contra 37,0 %.** Con él, no.

Y se ve por qué:

    L=1,00   días que rompen el 5 % flotante  1,07 %  ->  en 60 días  47,7 %
    L=1,25                                    2,64 %  ->             79,9 %
    L=1,50                                    4,39 %  ->             93,3 %
    L=2,00                                   10,16 %  ->             99,8 %

Con el apalancamiento que hace falta para llegar a +8 % en 60 días, la
probabilidad de tener UN día malo que te descalifique es del 80 %.

**El límite diario no es una regla de gestión de riesgo. Es lo que convierte
una ventaja real en un boleto de lotería.**

## Y el intento de esquivarlo, que fracasa

Probé lo obvio: un cortacircuitos que cierra el día al -2,5 % / -4,5 %
flotante, antes de que salte el límite. Primera versión: 52,5 % en ajuste.
Demasiado bueno — porque dejaba escapar de los **huecos de apertura**.
Corregido (si la sesión abre por debajo del corte, se sale en la apertura,
más deslizamiento):

    30 celdas de (L, corte)
    la mejor en ajuste            44,7 %   ->   fuera de muestra   35,2 %
    media de todas fuera                          35,7 %
    celdas que baten el 37 % fuera                14 de 30
    correlación ajuste / fuera de muestra        -0,002

**Cero.** El orden de las celdas en el ajuste no dice absolutamente nada
sobre lo que harán después. Es sobreajuste puro, y se ve porque el mismo
proyecto tiene un control con el que compararlo:

    geometría de barreras   ajuste 37,0 %  fuera 36,9 %   correlación +0,939
    cortacircuitos          ajuste 44,7 %  fuera 35,2 %   correlación -0,002

Lo que generaliza, generaliza así. Lo que no, se ve.

## Conclusión, tal como la firmé

> Si P(pasar) no supera el 37,0 % con ningún L, entonces la deriva no alcanza
> para nada operativo y se acabó el proyecto: no hay ventaja explotable en
> estos datos, ni buscada ni regalada.

No lo supera. Se acabó la búsqueda.

La mejor configuración que existe sigue siendo la de
`docs/RESULTADOS_cfd_fondeo.md`: **36,9 % fuera de muestra, que es
exactamente el techo de ventaja cero**. No se puede hacer mejor porque no hay
nada mejor que hacer.

## La única pregunta que queda, y es gratis

**¿FundingPips mide la pérdida diaria del 5 % sobre la equity flotante o
sobre el saldo cerrado?**

    flotante   ->   33,7 %
    cerrado    ->   40,5 %

Siete puntos de diferencia, y está en el contrato. Es lo más rentable que
puede hacer hoy: leerlo.
