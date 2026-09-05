# Resultado · Barrido de Liquidez Asiático en la apertura de Londres

Preregistro sellado antes de medir. Código en `bt/barrido_asiatico.py`.
EURUSD, 1.717 días de mercado, 2020-01 → 2026-07. Ejecución minuto a minuto.
Coste 1,43 pips (`docs/COSTE_real.md`). Un solo pase.

## El resultado, las seis variantes

     entrada  objetivo    n   stop    BRUTO      z      NETO      z   acierto  coste/R
     cerca        r3    419   9,3p  -0,1960  -2,61   -0,4169  -5,50    22,2 %   22,1 %
     cerca     rango    407   9,0p  -0,2586  -2,79   -0,4844  -5,21    26,3 %   22,6 %
     medio        r3    376   8,5p  -0,2295  -2,91   -0,4604  -5,74    20,7 %   23,1 %
     medio     rango    369   8,3p  -0,2796  -3,67   -0,5139  -6,58    24,7 %   23,4 %
     lejos        r3    343   7,8p  -0,2375  -2,88   -0,4842  -5,81    20,7 %   24,7 %
     lejos     rango    338   7,6p  -0,2963  -3,55   -0,5459  -6,41    22,5 %   25,0 %

**Las seis negativas en bruto**, con z entre -2,61 y -3,67. Falla antes de que
el coste entre en juego.

## Los cinco criterios firmados

    1  ventaja BRUTA con z > 2          -2,61 (negativa)      FALLA
    2  ventaja NETA positiva            -0,4169               FALLA
    3  bate a entradas al azar          -0,196 vs -0,126      FALLA
    4  bate a 5 nulos permutados        NO EJECUTADO
    5  >= 4 de 6 variantes netas > 0    0 de 6                FALLA

El criterio 4 no se ejecutó, y digo por qué en vez de dejarlo en blanco: un
nulo sirve para comprobar si una ventaja aparente es real. **Aquí no hay
ventaja aparente que comprobar** — la bruta es significativamente negativa.
Gastar el cómputo en eso habría sido teatro.

## El número que más dice

Con objetivo fijo 1:3, la probabilidad geométrica de acertar es **25,0 %**.

    las tres variantes "r3" aciertan   22,2 %   20,7 %   20,7 %

Está **por debajo del azar**. El déficit por sí solo da z ≈ -1,3, así que no
es concluyente aislado; lo concluyente es la R bruta (z -2,61 a -3,67), que
además de los aciertos incorpora las operaciones que no resuelven y cierran a
mercado al final del día.

## El control del azar

Entradas al azar en la misma ventana de Londres, con el mismo tipo de stop
(2 pips más allá del extremo asiático) y el mismo objetivo:

    objetivo 1:3        azar bruto medio  -0,1256    ·  la estrategia  -0,1960
    objetivo rango      azar bruto medio  -0,197     ·  la estrategia  -0,2586

**La estrategia es peor que entrar al azar** en las dos.

Aviso honesto, para no aprovecharme del número: **no es comparación limpia.**
Al entrar en cualquier momento de la ventana, la distancia hasta el extremo
asiático es mayor, así que el azar opera con stops de 13,7-17,3 pips contra
los 7,6-9,3 de la estrategia. Es otra geometría. La comparación es indicio
direccional, no un cara a cara.

Lo que sí es limpio: **las dos son negativas**, y la de la estrategia lo es
más, con un stop tres veces más corto que le hace pagar el triple de coste en
proporción (22-25 % del riesgo contra 8 %).

## El stop, que era el número anunciado

Firmé en el preregistro que publicaría el stop mediano junto al resultado
porque es lo que manda. Sale de **7,6 a 9,3 pips**, justo en la banda que
avisé, y ahí el coste se lleva del 22 al 25 % de cada operación.

## Dos fallos míos, corregidos antes de que dieran resultados

1. **Colisión de nombres con pandas.** Llamé `loc` y luego `lt` a la columna
   de hora local; las dos son atributos del DataFrame (`.loc` es el indexador,
   `.lt` es "menor que"). Reventó con un `TypeError` en vez de dar un número
   falso, que es la forma buena de fallar.

2. **Mirada al futuro dentro del minuto de entrada.** La misma que apareció
   hoy en la rejilla de EMA+Fibo: el minuto que llena la orden limitada no
   puede contar como objetivo alcanzado, porque el precio venía hacia la orden
   y su extremo favorable suele ser anterior al llenado. Corregido: el
   objetivo se busca desde el minuto siguiente, el stop desde el mismo.

## Mi predicción, y en qué me equivoqué

Firmé: *"espero que pase la 1 y falle la 2"* — o sea, ventaja bruta real que
el coste se come, que es el patrón de las otras dos estrategias de barrido
asiático medidas en este proyecto.

**Me equivoqué.** No hay ventaja bruta que comerse: es negativa y
significativa. Esta no muere por el coste. Muere antes.

## Sobre "sistema 100 % mecánico y probado"

**Mecánico, sí.** Y no es poco: pude programarla casi sin inventarme nada, y
eso la distingue de casi todo el material de estos dos meses. Las cuatro
ambigüedades que tenía las resolví probando las variantes en vez de elegir.

**Probado, no.** Nadie que la haya medido sobre 1.717 días con costes reales
y ejecución minuto a minuto puede haber visto estos números.
