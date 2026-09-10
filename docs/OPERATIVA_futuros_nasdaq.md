# La estrategia · NASDAQ, futuros micro (MNQ), evaluación de fondeo

Sale de `docs/RESULTADOS_alto_winrate.md` y de `bt/alto_winrate_optimo.py`.
Geometría ajustada en **2020-2023** y comprobada en **2024-2026**, que no se
tocó hasta el final.

## Lo primero, y sin adornos

**Esto no es una estrategia con ventaja.** Su esperanza por operación es cero:
+0,015 R en siete años, y ese +0,015 lo pagan 2020 y 2026 solos; los otros
cinco años están en el ruido. Si la operas en una cuenta tuya con dinero
tuyo, no ganas nada y pagas comisiones.

Lo que sí es, y está medido:

    la configuración que MAXIMIZA la probabilidad de pasar una evaluación
    de fondeo, dado que no hay señal con ventaja que aprovechar

Y esa probabilidad no depende de acertar. Depende de dónde están las dos
barreras -objetivo y drawdown- respecto del tamaño de tu operación. Eso es
geometría, y la geometría **sí generaliza**: al ordenar las 110
configuraciones por lo que hicieron en 2020-2023 y compararlas con lo que
hicieron en 2024-2026, la correlación es **+0,84** (y +0,94 en SP500). La
mejor según el ajuste sacó fuera de muestra un 36,2 %, y la mejor posible
fuera de muestra -que a priori no se podía saber- era 36,5 %. No hay
sobreajuste porque no hay nada que sobreajustar: es matemática de barreras.

Ninguna señal de este proyecto ha generalizado así. Esta sí, porque no es
una señal.

## NASDAQ, no SP500

Misma prueba en los dos:

    NASDAQ   mejor P(pasar) fuera de muestra   36,2 %
     SP500   mejor P(pasar) fuera de muestra   31,7 %

El SP500 se mueve menos y el coste pesa más en proporción. Opera NASDAQ.

## LA VERSIÓN QUE RECOMIENDO

    instrumento     MNQ (micro NASDAQ, 2 $ por punto)
    contratos       3
    entrada         COMPRA a mercado a las 09:35 hora de Nueva York
                    todos los días de mercado. Sin filtro, sin dirección,
                    sin esperar confirmación. Compra.
    stop            108 puntos por debajo de la entrada   ->  648 $
    objetivo        108 puntos por encima de la entrada   ->  648 $
    cierre forzoso  15:55 NY a mercado, pase lo que pase. Nunca overnight.
    una al día      si salta el stop, se acabó el día. No se reentra.

Números medidos, 1.691 sesiones:

    acierto                   51,7 %
    esperanza                 +0,015 R  (=  cero)
    resuelve en el día         74 %  (el 26 % se cierra a mercado a las 15:55)

    P(pasar) drawdown estático   45,1 %   fuera de muestra
    P(pasar) drawdown dinámico   34,4 %   fuera de muestra
    mediana                      14 días de operativa

Por qué esta y no otra: es la que más probabilidad de pasar da **por dólar
arriesgado**, tiene esperanza por operación ligeramente positiva (+9 $), y
648 $ de riesgo caben debajo del límite de pérdida diaria de cualquier
cuenta 50K. Las configuraciones más agresivas no lo hacen.

## LA VERSIÓN RÁPIDA, si tu cuenta la permite

    contratos       4        stop 216 pts (1.726 $)     objetivo 144 pts (1.152 $)

    P(pasar) estático   42,7 %      dinámico   36,4 %      mediana 6 días

Pasa antes -6 días contra 14- y tiene algo más de probabilidad con drawdown
dinámico. **Pero arriesga el 86 % del drawdown en una sola operación.** Si tu
prop firm tiene límite de pérdida diaria por debajo de 1.750 $, esta variante
te descalifica el primer día malo. No la uses sin comprobarlo.

## El plan de boletos, que es la parte que de verdad decide

Con P(pasar) = 34 % y una cuota de 80 €:

    1 evaluación     66 % de perder los 80 €
    6 evaluaciones   90 % de que al menos una pase        480 €
    13 evaluaciones  usando la tasa REAL observada por     1.040 €
                     un tercero (16,7 %, no la simulada)

Usa 16,7 %, no 34 %. La simulación no modela el límite de pérdida diaria, ni
la ejecución humana, ni los días en que no le das al botón. **Presupuesta
13 evaluaciones.**

Y el umbral que hace que el boleto valga la pena: una cuenta pasada tiene que
rendir más de **480 €** de media. El único dato real que existe sobre eso son
las 78 evaluaciones del psicólogo del trading: 1.823 € de media por cuenta
pasada. Con margen de sobra. Pero es UN dato, de UNA persona, de UN periodo.

## Reglas de parada, escritas antes de empezar

    · una operación al día, a las 09:35 NY. Si te la pierdes, no operas ese día.
    · nunca mover el stop. Nunca. Ni a beneficio.
    · nunca añadir contratos.
    · si pasas la evaluación, la cuenta fondeada se opera IGUAL. No cambies
      nada por tener dinero de verdad delante.
    · el presupuesto son N cuotas decidido HOY. Cuando se acaba, se acaba.
      No se recarga.

## Lo que hay que decir del riesgo, aunque no guste

Sobre las 1.691 operaciones, la peor racha acumulada de la versión de
4 contratos es de **-27.283 $**. En una cuenta tuya de 2.000 $ de margen eso
es la ruina catorce veces. Esta estrategia **solo** tiene sentido con la
pérdida topada en la cuota, que es exactamente el argumento del
`docs/RESULTADOS_arbitraje_fondeo.md`.

No es un negocio. Es un boleto con esperanza positiva. La diferencia importa.

## Lo que falta para que esto sea exacto

Tres datos tuyos que la simulación asume:

    1  qué prop firm de futuros, y su objetivo / drawdown / si es estático
       o dinámico / límite de pérdida diaria / días mínimos / tope de micros
    2  la cuota exacta
    3  la comisión ida y vuelta de MNQ en esa cuenta

Con el (1) cambia P(pasar); con el (2) cambia cuántos boletos necesitas.
El (3) casi no importa aquí, y eso es deliberado: esta configuración se
eligió porque doblar el coste solo le quita 2 puntos de probabilidad.
