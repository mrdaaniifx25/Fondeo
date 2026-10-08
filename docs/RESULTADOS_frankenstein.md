# Resultado · Frankenstein v1

Preregistro sellado en `37fd375`, antes de medir.

## El resultado

    M60 · SMC-71
                        variante     n   acierto   R bruta       z    R NETA
    ------------------------------------------------------------------------
               0 · índices, todo   315     36.2 %    +0.248   +2.65    +0.200
       1 · índices, SOLO COMPRAS   108     44.4 %    +0.533   +3.22    +0.490
        2 · índices, SOLO VENTAS   207     31.9 %    +0.099   +0.89    +0.048
       3 · forex, todo (control)   379     31.7 %    +0.080   +0.98    -0.046

       diferencia compras-ventas    +0.433   z = +2.17
          lo mismo en forex        -0.054   z = -0.33

    bootstrap de la celda 1: neta +0.490, IC 95 % [+0.170, +0.810],
    p(neta <= 0) = 0,1 %

## Las cuatro predicciones firmadas

    1 · las compras dan más R bruta que las ventas en índices   ACIERTA
    2 · la diferencia NO alcanza |z| > 2,0                      FALLA
        (z = +2,17, y falla a favor de la estrategia)
    3 · la variante 1 da neta positiva por encima de +0,065     ACIERTA
    4 · en forex no hay diferencia compras-ventas               ACIERTA

## Consistencia

    POR AÑO (compras, índices, M60)
      2020 +0.384 · 2021 +0.435 · 2022 +0.346 · 2023 +0.397
      2024 +0.571 · 2025 +0.697 · 2026 +1.044      -> 7 de 7 positivos
      quitando el mejor año: neta +0.463, z +2.99

    POR INSTRUMENTO
      NSXUSD n=52 +0.556 · SPXUSD n=45 +0.329 · GRXEUR n=11 +0.833

Si la ventaja real fuera cero, P(7 de 7 años positivos) = 0,8 %.

## Control de la deriva: la señal aporta por encima del sesgo alcista

Compras del SMC-71 contra COMPRAS ALEATORIAS con la misma geometría de
stop y objetivo, mismo instrumento y mismo periodo:

      instr  señal n   señal R   azar n    azar R  diferencia       z
     --------------------------------------------------------------
     NSXUSD       52    +0.592     2080    +0.048      +0.544   +2.24
     SPXUSD       45    +0.379     1800    +0.039      +0.340   +1.32
     GRXEUR       11    +0.881      440    +0.105      +0.776   +1.42
     --------------------------------------------------------------
      TODOS      108    +0.533     4320    +0.050      +0.482   +2.88

La compra aleatoria captura la deriva y da +0,050. La señal da +0,533.
**El +0,48 de diferencia no es deriva: lo aporta la señal.**

## POR QUÉ ESTO NO ESTÁ DEMOSTRADO

Y hay que decirlo con la misma fuerza que lo anterior.

    1. n = 108. Son 1,4 operaciones al mes. Cada año individual tiene
       15-20 operaciones y un z de 1,0 a 1,6: ninguno es significativo
       por sí solo. La consistencia vale, el tamaño no.

    2. LA CELDA SE ELIGIÓ CON CONOCIMIENTO PREVIO. Cuando firmé el
       preregistro yo ya sabía que el SMC-71 iba mejor en M60 y que los
       índices tienen deriva. El preregistro me ata las manos pero NO
       convierte esto en fuera de muestra.

    3. +0,49 R netas por operación es una ventaja enorme. En un mercado
       líquido, una ventaja así es implausible y debe levantar sospecha,
       no entusiasmo. La simulación del challenge da 96-100 % de aprobado,
       que es exactamente el tipo de número que en este proyecto siempre
       ha resultado ser un error.

    4. GRXEUR tiene 11 operaciones. El "3 de 3 instrumentos" es débil ahí.

## Qué lo demostraría

Datos de índices que yo no he visto nunca: M1 de US100, US500 y GER40 de
agosto y septiembre de 2026. Mis series acaban el 31 de julio de 2026.

Con seis semanas de datos vírgenes salen ~8-12 operaciones. Poco, pero es
la diferencia entre una hipótesis y una comprobación.
