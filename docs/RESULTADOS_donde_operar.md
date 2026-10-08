# ¿Está operando en el sitio equivocado?

Pregunta suya: *«¿y si pruebas en otro par? lo mismo estamos muy centrados y
estrategia hay, pero lo mismo no la estoy aplicando donde debo»*.

Se mide **su regla** —el cuerpo de la última M5 cerrada, roto por el cierre de
una M1, stop en el extremo de los últimos diez minutos, objetivo 1:2— en los
siete instrumentos del proyecto. 493.186 roturas.

## 1 · La ventaja no cambia de sitio. La geometría manda igual en todos

| instrumento | roturas | acierto de la regla a ciegas |
|---|---|---|
| EURUSD | 85.156 | 31,3 % |
| GBPUSD | 85.363 | 31,8 % |
| USDJPY | 84.499 | 31,4 % |
| XAUUSD | 38.924 | 32,0 % |
| GRXEUR | 38.149 | 30,8 % |
| NSXUSD | 80.493 | 30,4 % |
| SPXUSD | 80.602 | 30,5 % |

Entre 30,4 % y 32,0 % en medio millón de operaciones. **Ninguno tiene ventaja
mecánica, y la respuesta directa a su pregunta es que cambiar de par no la crea.**

## 2 · Pero el LISTÓN sí cambia, y muchísimo

Lo que varía entre instrumentos no es la ventaja: es **cuánto pesa el coste sobre
el tamaño natural de su stop**.

| instrumento | stop natural | coste / stop | acierto para no perder | **listón sobre la geometría** |
|---|---|---|---|---|
| **NSXUSD** | 25,8 pt | **5,8 %** | 35,3 % | **+1,9 pt** |
| SPXUSD | 5,3 pt | 9,4 % | 36,5 % | +3,1 pt |
| GRXEUR | 13,6 pt | 11,0 % | 37,0 % | +3,7 pt |
| XAUUSD | 1,66 $ | 12,0 % | 37,3 % | +4,0 pt |
| GBPUSD | 6,4 p | 25,0 % | 41,7 % | +8,3 pt |
| USDJPY | 5,4 p | 27,8 % | 42,6 % | +9,3 pt |
| **EURUSD** | 4,7 p | **30,4 %** | 43,5 % | **+10,1 pt** |

Su ventaja de selección, medida en el examen de roturas con contabilidad
estricta, es **+10,7 puntos**. En EURUSD el listón es +10,1: **está justo en la
raya**. En el Nasdaq sería +1,9.

Y se ve en la R neta de la regla ciega: −0,357 en EURUSD contra **−0,069** en
NSXUSD. La misma regla, sin ventaja en ninguno, pierde cinco veces menos.

## 3 · La objeción grande: esos costes NO están medidos

Solo el de EURUSD lo está (1,43 pips, verificado en la cuenta de FundingPips).
Los otros seis son estimaciones de spread típico y pueden estar cortos.
Sensibilidad, multiplicando el coste estimado:

| instrumento | ×1 | ×2 | ×3 | ×4 |
|---|---|---|---|---|
| NSXUSD | +1,9 | +3,9 | +5,8 | +7,8 |
| SPXUSD | +3,1 | +6,3 | +9,4 | +12,6 |
| XAUUSD | +4,0 | +8,0 | +12,0 | +16,1 |
| EURUSD | +10,1 | +20,3 | +30,4 | +40,6 |

**Aunque el coste real del Nasdaq fuera el cuádruple de mi estimación, su listón
seguiría siendo más bajo que el de EURUSD con el coste verificado.** Esa es la
única conclusión que aguanta la incertidumbre, y aguanta bien.

## 4 · Lo que esto NO dice

- No dice que su criterio funcione en el Nasdaq. Su 64,8 % se midió en EURUSD, en
  Londres, sobre 223 operaciones. Su ojo está entrenado en ese gráfico.
- La ventana del Nasdaq aquí es 15:30-19:00 hora de Madrid, no su horario.
- Falta comprobar el spread y la comisión reales del Nasdaq en su cuenta. Es un
  dato que puede conseguir él en cinco minutos y que decide todo lo anterior.

## Lo que cambia en el proyecto

Es la primera vez en dos meses que la pregunta útil no es *qué estrategia* sino
**en qué escala**. Todas las familias probadas morían por el mismo sitio: un stop
de 4-6 pips contra un coste de 1,43. Ese cociente —no el patrón— es lo que hay
que atacar, y se ataca de dos maneras: stops más anchos, o un instrumento cuyo
movimiento natural sea grande comparado con lo que cobran.

## Reproducir

`python3 bt/su_regla_instrumentos.py` · `data/su_regla_instrumentos.csv`
