# Resultado · la estrategia del oro, fuera de muestra

El usuario descargó `XAUUSD` M1 de 2020, 2021 y 2022 de histdata.com, que es
lo único que faltaba para decidir esta estrategia. Tres años que ni yo había
visto ni, razonablemente, vio la optimización de StrategyQuant.

Se corrió `bt/sqx_xauusd.py` **sin tocar un solo parámetro** (`DATOS=fuera`).

## El resultado

    operaciones          473
    periodo              2020-01-15 -> 2022-12-30   (2,96 años)
    capital final        44.644 $   (-55,4 %)
    CAGR                 -23,87 %
    acierto              33,2 %      (era 42,5 % dentro de muestra)
    profit factor        0,740
    drawdown máximo      -54,9 %

      año   ops       neto   acierto
     2020   178    -21.756    37,1 %
     2021   149    -21.052    32,9 %
     2022   146    -12.548    28,8 %

**Negativa los tres años.** Pierde más de la mitad de la cuenta.

## No es el coste

    spread 0,20   -55,4 %   PF 0,740
    spread 0,14   -50,3 %   PF 0,772
    spread 0,00   -35,7 %   PF 0,851      <- sin ningún coste

Con **cero** coste sigue perdiendo el 35,7 %. El bruto ya es negativo
(−39.926 $). El spread real que midió el usuario no salva nada porque el
problema nunca estuvo ahí.

## Qué era en realidad

                          el oro hizo        su peor caída
    2020-2022 (fuera)       +19,9 %             -21,4 %
    2023-2025 (dentro)     +136,4 %             -11,4 %

La estrategia es una **rotura al alza**. Funciona en una tendencia limpia y
fuerte y se desangra en lateral. 2023-2026 fue una subida histórica del oro con
caídas pequeñas; 2020-2022 fue una subida parecida en total pero con un −21 %
por el medio. Eso basta para pasar de +87,8 % a −55,4 %.

    dentro de muestra   2023-2026   +87,8 %
    FUERA de muestra    2020-2022   -55,4 %

## Y un fallo mío que este dato deja al descubierto

En `RESULTADOS_sqx_xauusd.md`, el control 5 preguntaba justamente esto: *¿es del
instrumento o del régimen alcista?* Respondí que **no era el régimen**, porque
el US100 subió con fuerza en 2023-2026 y la estrategia no ganaba nada ahí.

**Esa conclusión era falsa.** Comparé regímenes *entre instrumentos* cuando la
pregunta exigía comparar regímenes *dentro del mismo instrumento*, y eso no
podía hacerlo porque no tenía oro anterior a 2023. Debí decir que el control no
respondía a la pregunta, en vez de darlo por respondido.

Con el oro de 2020-2022 delante, la respuesta es la contraria: **es el régimen.**

## Veredicto

La estrategia del oro está cerrada. Era el único resultado del proyecto que
pasaba sus controles internos, y lo que quedaba por comprobar era exactamente
lo que ha fallado.

Nota honesta, para no dejarla a medias: se podría añadir un filtro de tendencia
que la apague en lateral. Pero eso es un parche elegido **después** de ver que
2020-2022 falla, y este repositorio entero documenta lo que les pasa a esos
parches cuando se miden fuera de muestra.
