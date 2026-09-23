# Resultado · la estrategia CRT ensamblada, medida fuera de muestra

Todo lo que ha sobrevivido a dos meses de mediciones, montado como un solo
objeto y sometido a un corte temporal. Código en `bt/crt_final.py`.
Cinco instrumentos, 104.344 filas.

## Qué lleva dentro, y de dónde sale cada pieza

| pieza | qué | de dónde |
|---|---|---|
| rango | vela anterior cerrada | CRT canónico |
| manipulación | barre un extremo y **cierra** de vuelta dentro | CRT canónico |
| entrada | al cierre de la vela de manipulación, sin esperar retroceso | agresiva gana 19/20 (`RESULTADOS_crt_9am.md`) |
| stop | el extremo del **barrido**, no el del rango | liquidación gana 19/20 (`RESULTADOS_crt_9am.md`) |
| temporalidad | H12 y D1 | único sitio con coste/riesgo < 4 % (`RESULTADOS_crt_temporalidad.md`) |

**Las dos reglas de Brad Gould ya estaban dentro del +0,125 de H12.** No añaden
un punto: explican por qué H12 era la mejor celda. Eso conviene decirlo claro,
porque la esperanza era que sumaran.

## La única palanca que quedaba libre

    neta = (p - p0)·(1 + R:R) - coste/riesgo

Ensanchar el stop baja el coste en R **y** baja el R:R a la vez. Cuál gana es
empírico, y había motivo para probarlo: el resultado de Brad dice que los stops
estrechos los saltan por encima de lo que su geometría compensa.

Se probaron 4 anchos (×1,00 ×1,25 ×1,50 ×2,00) × 3 objetivos × 2 temporalidades
= **24 celdas**. La celda se eligió mirando **solo 2020-2023** y se informa su
resultado en 2024-2026. Un número.

## El resultado

**Dentro de muestra (2020-2023), 1 de 24 celdas es positiva:**

    H12 · stop ×1,00 · objetivo ext150   ->   neta +0,0192   z +0,72

**Fuera de muestra (2024-2026), esa celda da:**

    neta -0,0569   z -1,91   sobre 2.908 operaciones

Y el dato que cierra el asunto: **las 24 celdas son negativas fuera de muestra.**
Ninguna excepción. La mejor de las 24 fuera de muestra es −0,0384.

Por instrumento y por año, fuera de muestra:

       instr     n   R:R  acierto   geom    BRUTA     NETA      z
      EURUSD   613  3,16   19,4 % 31,8 %  +0,0045  -0,0679  -0,99
      GBPUSD   584  3,57   18,5 % 31,0 %  -0,0734  -0,1448  -2,33
      NAS100   559  3,36   29,9 % 37,2 %  +0,0045  -0,0112  -0,16
      SPX500   552  3,52   29,3 % 37,6 %  -0,0246  -0,0583  -0,90
      USDJPY   600  3,64   21,7 % 30,9 %  +0,0486  -0,0015  -0,02

        2024  1151  3,44   24,2 % 34,5 %  -0,0466  -0,1010  -2,34
        2025  1106  3,52   24,1 % 33,0 %  +0,0148  -0,0307  -0,63
        2026   651  3,34   21,7 % 33,1 %  +0,0236  -0,0235  -0,34

## La palanca no funciona

Familia H12 / ext150, variando solo el ancho del stop:

    2020-2023:  ×1,00 +0,0192   ×1,25 -0,0112   ×1,50 -0,0220   ×2,00 -0,0218
    2024-2026:  ×1,00 -0,0569   ×1,25 -0,0567   ×1,50 -0,0390   ×2,00 -0,0384

Dentro de muestra ensanchar **empeora**; fuera de muestra ensanchar **mejora**.
Los dos periodos apuntan a lados opuestos. Eso no es una palanca, es ruido.

El ahorro de coste es real —del 5,0 % al 2,5 % del riesgo— pero la pérdida de
R:R se lo come entero. **La última palanca que dejaba abierta la ecuación del
coste está medida y no está.**

## Y la ventaja bruta se sigue apagando

Diferencia fuera − dentro, celda por celda:

    24 celdas  ·  21 bajan, 3 suben  ·  media -0,0255

La prueba de signos anterior era 6 de 6 (`RESULTADOS_crt_tf_partido.md`,
p = 0,031). Ahora es **21 de 24**, p ≈ 0,0002. Ya no es una sospecha.

## En dinero

Cuenta de 10.000 €, riesgo 1 % = 100 € por operación, los cinco instrumentos:

    2020-2023   1.089 operaciones/año   +1,92 € por operación    +2.091 €/año
    2024-2026   1.129 operaciones/año   -5,69 € por operación    -6.424 €/año

En EURUSD solo, la quinta parte de las operaciones y del resultado.

Composición de cada operación (fuera de muestra): 23,6 % llega al objetivo,
55,8 % al stop, 20,6 % sigue abierta al vencer el horizonte de 3 velas y se
valora a mercado. Ese último grupo aporta +0,108 R de media al total — o sea
que **sin las posiciones sin resolver el resultado sería bastante peor**, no
mejor. Valorarlas a mercado es el trato honesto y aun así no llega.

## Conclusión

Está montada. Lleva dentro todo lo que sobrevivió a las mediciones, se eligió
sin mirar el futuro, y **fuera de muestra pierde dinero en las 24 celdas.**

No es que falte un filtro. Es que:

1. La ventaja bruta del CRT era pequeña (+0,08 R) y **se está apagando**
   (21 de 24 celdas a la baja, p ≈ 0,0002).
2. La única palanca contra el coste —el stop ancho— está medida y no funciona.
3. Las dos reglas nuevas que sobrevivieron ya estaban dentro del mejor número.

El CRT como fuente de ventaja está cerrado. Lo que queda del trabajo no es la
estrategia: es el método —controles, corte temporal, nulos— que permitió
saberlo en dos meses en vez de en dos años de cuenta real.
