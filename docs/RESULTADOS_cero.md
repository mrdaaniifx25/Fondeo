# Confirmación del cribado de cero · **DESCARTADA**

Conjunto de confirmación abierto una sola vez, el 25 de agosto de 2026, contra
los tres criterios escritos en `CANDIDATA_cero.md` antes de mirar nada.

| criterio declarado | resultado | |
|---|---|---|
| 1. El signo se mantiene en EURUSD 2024-2026 | neta **−0,173** pips | **falla** |
| 2. La ventaja neta es ≥ +0,70 pips | −0,173 | **falla** |
| 3. El signo se mantiene en GBPUSD o USDJPY | USDJPY +0,712 | cumple |

**Falla el 1 y el 2. La candidata queda descartada.** No se toca, no se
reajusta, no se busca otra celda.

---

## Los números

**EURUSD, con los umbrales congelados tal cual:**

| | operaciones | al año | bruto | **neta** | IC 95 % | aciertos |
|---|---|---|---|---|---|---|
| 2020-2023 · descubrimiento | 748 | 187 | +2,604 | **+1,404** | [−0,002, +2,811] | 57,4 % |
| **2024-2026 · confirmación** | 277 | 107 | +1,027 | **−0,173** | [−2,480, +2,135] | 53,4 % |

**Los otros dos pares, 2020-2026 entero,** con el percentil 80 de su propio ATR:

| par | operaciones | bruto | neta | aciertos |
|---|---|---|---|---|
| GBPUSD (coste 1,50) | 847 | +0,727 | −0,773 | 52,4 % |
| USDJPY (coste 1,30) | 1.467 | +2,012 | **+0,712** | 54,7 % |

## Qué falló exactamente

**1. El signo sobrevivió. El tamaño no.** Antes de aplicar ningún filtro, la
señal sigue apuntando al lado correcto en 2024-2026: bruto +0,539 pips contra
+0,895 en descubrimiento. La reversión existe. Lo que pasa es que **vale la
mitad de lo que cuesta ejecutarla**. Para que 2024-2026 diera positivo haría
falta operar por debajo de 1,03 pips de ida y vuelta, y eso no existe.

**2. La rejilla entera se cayó, no solo la celda.** La razón por la que congelé
p80+2 % en vez del pico era que el gradiente subía de forma ordenada en las dos
direcciones, y el ruido no hace eso. Recalculada en 2024-2026, la fila de p80
queda +0,73 / −0,18 / −0,38 / −0,32: la monotonía desapareció. Esa reserva —la
número 2 de la ficha, la única que estaba a favor— era la lectura equivocada.

**3. Menos volatilidad, menos operaciones.** La mediana del ATR(48) pasó de 6,81
a 5,72 pips, y el umbral fijo de 9,47 dejó de seleccionar el 20 % de las velas
para seleccionar el 11 %. De ahí que caiga de 187 a 107 operaciones al año. Esto
no es un fallo del método: es el mercado.

## Lo que ya se veía en el descubrimiento y no supe pesar bien

El intervalo de confianza del descubrimiento era **[−0,002, +2,811]**. Tocaba el
cero. Con 748 operaciones y una desviación típica de 19,6 pips por operación,
para distinguir una ventaja de +1,4 pips de la nada con un 80 % de potencia
hacen falta **1.526 operaciones, o sea 8,2 años operando**.

Ese número es el que importa, y vale para cualquier cosa de este tamaño: **una
ventaja de un pip y medio por operación no se puede confirmar ni desmentir en un
horizonte humano**. Aunque la candidata hubiera pasado los tres criterios, no
habría habido forma de saber si estaba funcionando hasta 2034.

## Estado del método de cero

El cribado hizo su trabajo: encontró la única señal que hay en 54 variables
mecánicas sobre EURUSD M15 —reversión a una hora, concentrada en volatilidad
alta—, la midió contra un nulo honesto, y la confirmación la ha descartado por
tamaño. El proceso es correcto. El resultado es que **ahí no hay negocio a este
coste**.

Sigue en pie, sin tocar y sin confirmar en adelante, una sola cosa de toda la
semana: el efecto lunes del NAS100 (`RESULTADOS_efectos.md`).
