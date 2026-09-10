# Resultado · "en máximos históricos, buscar siempre compras"

Preregistro sellado en `02570ea`, antes de medir. Código en
`bt/maximos_historicos.py`. Un solo pase.

## El efecto "máximos históricos", aislado

Compras en máximos MENOS compras fuera de máximos, stop 80, M30:

       NASDAQ   +0.073 R   z = +4.76
        SP500   -0.059 R   z = -6.67
        GER40   +0.001 R   z = +0.03

**Signos opuestos en los dos índices que él opera.** NASDAQ dice que sí,
SP500 dice exactamente lo contrario, GER40 dice que nada. Eso es la
definición de ruido: un efecto real no cambia de signo entre dos activos
correlacionados al 0,9.

(Matiz honesto: la celda del SP500 solo resuelve el 20 % de las veces
-80 puntos es demasiado ancho ahí- así que es la menos fiable. Aun así
apunta al revés, y eso basta para tumbar la regla.)

## Lo que SÍ hay debajo, y es real

     instr        zona    lado      n  resuelve        R       z     NETA
     ------------------------------------------------------------------
    NASDAQ  EN MAXIMOS  COMPRA   5220       98 %   +0.097   +7.09   +0.078
    NASDAQ       fuera  COMPRA  19476      100 %   +0.023   +3.25   +0.005
    NASDAQ       fuera   VENTA  19476      100 %   -0.039   -5.45   -0.058
     SP500       fuera  COMPRA  17042       52 %   +0.054   +8.95   +0.048
     SP500       fuera   VENTA  17042       52 %   -0.054   -8.95   -0.060
     GER40  EN MAXIMOS  COMPRA   2512       90 %   +0.093   +4.88   +0.074
     GER40       fuera  COMPRA   7115       92 %   +0.092   +8.09   +0.074

En los tres índices, COMPRAR bate a VENDER, esté donde esté el precio.
Con z entre +3 y +9. Eso no es un patrón de trading: es la deriva alcista
de la renta variable, la prima de riesgo. Existe, es grande y no tiene
nada que ver con estar en máximos.

## Y decae

NASDAQ, compras con stop 80, todas las barras:

       2020  R +0.115  NETA +0.096
       2021  R +0.078  NETA +0.059
       2022  R -0.030  NETA -0.049
       2023  R +0.082  NETA +0.064
       2024  R -0.019  NETA -0.037
       2025  R +0.005  NETA -0.014
       2026  R -0.013  NETA -0.032
      TOTAL  R +0.033  NETA +0.014

Los tres últimos años son planos o negativos. La deriva pagó en
2020-2021 y en 2023, y no ha pagado desde entonces intradía.

GER40 solo tiene 2023-2025 en estos datos y ahí sí paga: NETA +0.080.
Tres años de mercado alcista alemán. No es una muestra que permita
concluir nada sobre el futuro.

## Las cuatro predicciones firmadas

    1 · existe deriva alcista cerca de máximos       PARCIAL: existe
        deriva alcista, pero no es "cerca de máximos"
    2 · la ventaja de las compras no llega a 3 pts   FALLA: es mayor
    3 · no sobrevive al coste con stop 20, sí con 80 ACIERTA
    4 · la diferencia máximos/no-máximos es menor
        de lo que él sugiere                          ACIERTA, y de una
        manera peor para él: cambia de signo

## Conclusión

Tiene razón en lo que observa y se equivoca en la causa, y la causa
importa. Ve que las compras funcionan mejor y lo atribuye a los máximos
históricos. Lo que funciona mejor son las compras, punto: en índices,
siempre, por la deriva estructural.

Operar esa deriva intradía es capturar BETA, no alfa. Se captura mejor
comprando y esperando, sin stop. Y con un límite de pérdida del 10 % en
una cuenta de fondeo, una estrategia solo-largos en índices te saca en
el primer 2022.
