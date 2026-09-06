# Resultado · la estrategia del grupo (primer pase)

Preregistro sellado en `6011c5b`, antes de correr nada.
Código en `bt/grupo_nasdaq.py`. Un solo pase, sin retoques posteriores.

## El resultado

    9.277 operaciones · 2020-01-02 a 2026-07-31 · NASDAQ y SP500

                      variante      n   acierto   R bruta       z    R NETA
    ------------------------------------------------------------------------
                  A · TP a 1:1   9277     48.4 %    -0.035   -3.36    -0.187
         EL · DOL si 1:1-1:1,5   9277     48.3 %    -0.035   -3.40    -0.187
               B · DOL tope 4R   9277     43.6 %    -0.020   -1.54    -0.172

    por ventana (A)      FRANKFURT  3012  -0.038  z -2.09
                           LONDRES  3061  -0.021  z -1.18
                         NUEVAYORK  3204  -0.044  z -2.54

    SMT (A)              CON SMT    1352  -0.040  z -1.47
                         SIN SMT    7925  -0.034  z -3.03
                         diferencia -0.006   z = -0.21

## Las seis predicciones firmadas

    1 · n entre 600 y 2.500                              FALLA (9.277)
    2 · PRINCIPAL: R bruta de A no supera +0,10 con z>2   ACIERTA
    3 · acierto de A entre 45 % y 55 %                    ACIERTA (48,4 %)
    4 · B con mayor R bruta que A                         ACIERTA
    5 · R neta de A negativa                              ACIERTA (-0,187)
    6 · C y D no se diferencian                           ACIERTA (z -0,21)

Cinco de seis. La que falla es la del número de operaciones, y falla de
una manera que importa mucho.

## EL PROBLEMA: mi reconstrucción no filtra

    9.277 operaciones en 1.697 días = 5,5 al día
    ventanas disponibles: 1.697 x 3 x 2 = 10.182
    -> DISPARA EN EL 91 % DE LAS VENTANAS

Él opera una vez al día, y hay días que ninguna. Yo entro en nueve de cada
diez oportunidades. Eso no es su estrategia: es un esqueleto sin criterio.

Y la causa es mía y concreta: **de sus cinco confluencias solo programé
dos.** La especificación (sección 4) lista:

    1. tapeo de FVG de M15 o M5          -> IMPLEMENTADA
    2. barrido de liquidez claro         -> implementada solo como el DOL
    3. Judas Swing con sus condiciones   -> NO IMPLEMENTADA
    4. LRL a favor                       -> NO IMPLEMENTADA
    5. LRL en contra ya barrida          -> NO IMPLEMENTADA

Con dos de cinco, el filtro casi no filtra.

## Qué SÍ queda establecido de este pase

    - El esqueleto mecánico -ventanas de apertura, sesgo por FVGs de H4/H1,
      confluencia de FVG de M15/M5, gatillo IFVG, stop en la inducción,
      TP a 1:1- NO tiene ventaja. R bruta -0,035 con z -3,36.

    - El SMT NO APORTA. z de la diferencia -0,21 sobre 9.277 operaciones.
      Era una de las dos cosas genuinamente nuevas de este método y es una
      predicción firmada que se cumple. Resultado limpio.

    - El 1:1 es la peor de las tres variantes de TP, otra vez. Coherente
      con todo el proyecto: el ratio 1:1 exige más del 60 % de acierto.

## Qué NO queda establecido

No se refuta su método. Se mide un esqueleto sin selectividad. La parte
que él llama "la balanza" y las tres confluencias que no programé son
justamente donde podría estar el valor.

Además el signo negativo no es estable: 2021 y 2023 salen planos-positivos
y 2020, 2025 y 2026 negativos. No hay ni ventaja ni anti-ventaja robusta.
Y operarlo al revés tampoco vale: +0,035 bruto menos 0,152 de coste
= -0,117 neto. El coste se come el 11 % de cada R con un stop mediano de
8 puntos.

## Siguiente paso, que requiere preregistro nuevo

Implementar las tres confluencias que faltan y volver a medir. NO es
buscar parámetros: es completar una implementación incompleta de una
especificación que ya estaba escrita y sellada antes. Pero como ya he
visto el resultado del primer pase, el segundo necesita su propio
preregistro firmado antes de correrlo.
