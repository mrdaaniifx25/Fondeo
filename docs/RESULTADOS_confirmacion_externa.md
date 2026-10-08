# Confirmación externa · el backtest de CRT del psicólogo del trading

Un tercero, con otro software (Forex Tester), otro instrumento (GBPUSD),
otro método (CRT) y otro periodo, llega a los mismos números.

## Sus números contra los míos

    SUYOS · CRT · GBPUSD · 2019-2025 · ~300 operaciones
      win rate 40 %  ·  ratio 1,8:1  ·  profit factor 1,16
      -> esperanza BRUTA = 0.392*1.8 - 0.608 = +0.097 R por operación

    MÍOS · SMC-71 · 2020-2026 · código propio
      forex M30 agrupado   +0.183 R bruta  (z +3.07, n=752)
      M15 los 6 juntos     +0.166 R bruta  (z +4.90, n=2331)

**El mismo orden de magnitud, por caminos completamente independientes.**

## Donde él se equivoca, y a su favor

Dice: *"esto está sin comisiones, ni swap, ni slipaje, ni spread... con un
profit factor de 1,16 sin castigar, es demasiado justo para sobrevivir"*.

Pero su stop medio son ~60 pips (swing, diario/H4):

    coste GBPUSD 1,6 pips  ->  2,7 % de la R
    neta = +0.097 - 0.027 = +0.071 R

**Con stops de 60 pips el peaje casi no pesa.** No es el coste lo que la
mata.

## Lo que sí la mata: la frecuencia

     3 operaciones/mes al 1 % de riesgo  ->   +2,5 % anual
    10 operaciones/mes                   ->   +8,5 % anual
    30 operaciones/mes                   ->  +25,4 % anual

Él midió **14 % en 5 años** con 3 al mes en un solo par = 2,7 % anual.
Cuadra exactamente con la aritmética. Sus números son coherentes consigo
mismos y con los míos.

## LA SÍNTESIS DE TODO EL PROYECTO

    STOP ESTRECHO (intradía):  la ventaja existe pero el coste se la come
    STOP ANCHO (swing):        el coste no pesa, pero la frecuencia mata

Los dos caminos llevan al mismo sitio. Y ahora está medido dos veces por
dos personas que no se conocen.

La única salida aritmética es la TERCERA variable: **más instrumentos.**
30 operaciones al mes con +0.071 R dan +25 % anual. Eso exige operar
diez pares a la vez, no encontrar una señal mejor.

## Lo que él dice y confirma cosas ya medidas aquí

    "yo mismo he retirado dinero en Fondeo con ESTRATEGIA PERDEDORA"
        -> confirma el cálculo de que el 24 % de una población con
           ventaja cero llega a retirar

    "en cuenta real personalmente yo no lo haría... es una estrategia
     ganadora para Fondeo pero no trasladable al mercado real"

    "la gente que tiene éxito tiene muchas EXCEPCIONES DE ENTRADA...
     esas excepciones son ajustes a la muestra"
        -> es exactamente "la balanza" del grupo de WhatsApp

    "no vais a encontrar dos traders con los mismos resultados en el
     mismo periodo, y eso implica subjetividad"

    Enseña el backtest de otro trader algorítmico: 12 años de CRT,
    resultado NEGATIVO.

    Sobre el 80-90 % de win rate que se anuncia: "es imposible. Si
    tienes un 80 % de win rate tendrás 0,75 a 1. Con un 2 a 1 te pasas
    al 40 %."   -> la misma geometría 1/(1+k) de este proyecto

## Aviso de conflicto de interés

El vídeo es, en parte, publicidad de Forex Tester con enlace de afiliado
y descuento de Black Friday, repetido cinco veces. Eso no invalida su
análisis -que es correcto y honesto- pero conviene saberlo.
