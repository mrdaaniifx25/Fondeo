# El suelo de detección: qué NO he probado, y qué sí

El usuario lleva tres meses sin creerse los resultados. Tiene razón en una parte
y conviene escribirla antes de seguir discutiendo.

## Lo que NO he probado

`t = Sharpe × √años`. Para que un resultado salga significativo (t > 2) hace
falta que el Sharpe real supere `2/√años`. Eso pone un **suelo** a cada prueba:

| prueba | años | Sharpe mínimo detectable |
|---|---|---|
| panel completo 1971-2026 | 55,0 | **0,27** |
| panel 2000-2012 | 13,0 | 0,55 |
| **panel 2013-2026 — el que decide** | **13,8** | **0,54** |
| EURUSD M15, sus datos | 5,0 | 0,89 |
| oro y DAX, sus datos (32 meses) | 2,7 | **1,22** |

**En el tramo 2013-2026 no puedo distinguir cero de un Sharpe de 0,54.** Una
estrategia con Sharpe real de 0,40 —que es una estrategia buena de verdad, de
las que gestionan dinero ajeno— habría salido de mis pruebas como «no
significativa». Y en oro y DAX, con 32 meses, el suelo es 1,22: ahí casi nada
real se habría visto.

Así que la frase «no funciona nada» es **falsa como conclusión de mis datos**.
Lo correcto es: *no he encontrado nada, y mi aparato no puede ver por debajo de
estos suelos.*

## Lo que SÍ he probado

Su objetivo son 300 €/mes sobre 10.000 €. Eso es **3.600 €/año = 36 % anual**.

La caída máxima esperada de una estrategia con deriva es `DD = vol / (2·Sharpe)`.
Imponiendo el límite de la cuenta de fondeo y despejando:

| límite de caída | volatilidad implícita | **Sharpe necesario** |
|---|---|---|
| 10 % | 27 %/año | **1,34** |
| 7 % | 22 %/año | 1,60 |
| 5 % (para sobrevivir de verdad) | 19 %/año | **1,90** |

Y ahora el contraste que cierra el asunto:

| qué | Sharpe |
|---|---|
| sistema ensamblado, 55 años | +0,64 |
| momento + carry, FX mensual, 55 años | +1,00 |
| mejor celda individual de los indicadores | +1,14 |
| sistema ensamblado, 2013-2026 (operable) | −0,05 |
| exceso sobre comprar-y-aguantar, la mejor de 108 celdas | **+0,00** |
| **lo que su objetivo necesita (límite 10 %)** | **+1,34** |
| **lo que necesita para sobrevivir (límite 5 %)** | **+1,90** |

**Un Sharpe de 1,34 está muy por encima de mi suelo de detección de 0,54.**

Eso es lo decisivo. Si existiera una estrategia lo bastante buena para su
objetivo, **mis pruebas la habrían visto con holgura** — no estaría al borde de
la significación, estaría a t +5 en el tramo reciente. No está.

## La frase correcta, por fin

No es «no funciona nada».

Es: **puede perfectamente existir algo con Sharpe 0,2-0,5 que yo no sea capaz de
ver con los datos que tengo. Lo que no existe, porque lo habría visto, es algo
con Sharpe 1,3 o más.**

Y la diferencia entre esas dos cosas no es académica. Un Sharpe de 0,4 es real,
es valioso, y da **unos 40-80 €/mes sobre 10.000 €**. No da 300.

## Referencia externa

Los mejores fondos cuantitativos de la historia sostienen Sharpe **2-3 bruto**
durante décadas, con equipos de cien personas, datos que cuestan millones y
costes de ejecución cien veces menores que los suyos.

Su objetivo, sobre una cuenta de 10.000 € con un límite de caída del 10 %, pide
**la mitad de eso, sostenido, en solitario, con una plataforma de minorista.**

Ésa es la razón por la que no aparece. No es que el mercado sea perfecto: es que
el listón que hay que superar no lo pone el mercado, lo pone el tamaño de la
cuenta.
