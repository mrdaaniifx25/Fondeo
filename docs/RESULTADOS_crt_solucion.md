# Resultado · el objetivo pendiente, fuera de muestra

Todo lo anterior sobre esta idea estaba medido en 2020-2026 entero, que es
**donde se encontró la idea**. Eso no vale como prueba. Código en
`bt/crt_solucion.py`.

Aquí la regla se construye mirando **solo 2020-2023** y se suelta tal cual
sobre **2024-2026**, sin tocar nada.

Se le dan a la idea sus 12 mejores opciones —objetivo pendiente en diario o en
semanal, con tres caducidades cada uno, con y sin el sesgo diario encima— pero
la elección se hace sin ver el futuro.

## El resultado

        objetivo pendiente  +sesgo |     n     NETA      z |     n  NETA fuera      z
                       D10      si |   424  +0,0826  +1,01 |   305     -0,0447  -0,57
                       D10       - |  1144  +0,0708  +1,36 |   802     -0,0757  -1,40
                       D20      si |   462  +0,0571  +0,75 |   324     -0,0771  -1,03
                       D20       - |  1270  +0,0430  +0,89 |   862     -0,0847  -1,62
                        D5       - |   998  +0,0283  +0,54 |   709     -0,0663  -1,13
                        D5      si |   381  +0,0188  +0,24 |   270     -0,0548  -0,66
                        W6      si |   399  +0,0069  +0,09 |   326     -0,0974  -1,23
                       W12      si |   448  +0,0015  +0,02 |   357     -0,0888  -1,20
                        W3      si |   323  -0,0085  -0,10 |   265     -0,0784  -0,85
                       W12       - |  1207  -0,0568  -1,26 |   827     -0,0122  -0,22
                        W3       - |   859  -0,0730  -1,37 |   605     -0,0041  -0,06
                        W6       - |  1082  -0,0827  -1,76 |   753     -0,0157  -0,26

                SIN FILTRO       - |  2657  +0,0078  +0,23 |  1797     -0,0707  -1,87

**Las doce variantes son negativas fuera de muestra.** Sin excepción.

Y hay algo más elocuente que eso: **el orden se invierte**. Las seis mejores
dentro de muestra (todas las diarias) son las seis peores fuera. Las tres
peores dentro (las semanales sin sesgo) son las tres menos malas fuera. Eso es
la firma exacta del sobreajuste: lo que se eligió por bueno resultó ser lo que
más se había ajustado al ruido de ese tramo.

## La regla elegida sin mirar el futuro

Objetivo pendiente diario con caducidad de 10 días, más sesgo diario a favor.

    dentro  2020-2023    424 operaciones   R neta +0,0826
    FUERA   2024-2026    305 operaciones   R neta -0,0447   z -0,57

                 n  acierto    azar     BRUTA      NETA       z
      EURUSD   107   29,0 %  40,1 %  +0,1791   +0,1169   +0,77
      GBPUSD   106   27,4 %  39,5 %  -0,0179   -0,0734   -0,64
      USDJPY    92   27,2 %  41,9 %  -0,1581   -0,1995   -1,47
        2024   123   28,5 %  40,1 %  +0,0563   +0,0002   +0,00
        2025   117   27,4 %  40,6 %  +0,0113   -0,0362   -0,28
        2026    65   27,7 %  41,0 %  -0,0851   -0,1449   -0,98

EURUSD aguanta (+0,1169) y los otros dos se caen. Un par de tres, otra vez.

## En dinero

Cuenta de 10.000 €, riesgo del 1 % = 100 € por operación:

    2020-2023   106 operaciones/año   +8,26 €/op    +877 €/año
    2024-2026   118 operaciones/año   -4,47 €/op    -529 €/año

## Veredicto

La idea era buena, apuntaba al sitio correcto y ganaba a todo lo que proponen
los vídeos. Medida como hay que medirla —eligiendo con el pasado y cobrando con
el futuro— **pierde dinero en las doce formas de plantearla**.

Con esto el CRT queda cerrado del todo. No por falta de ganas ni de ideas: por
haber probado la mejor que había, de doce maneras, con la disciplina correcta.
