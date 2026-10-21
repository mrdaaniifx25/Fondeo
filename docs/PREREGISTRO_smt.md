# Pre-registro · divergencia SMT entre instrumentos

Escrito y subido ANTES de medir. 22/09/2026.

## De dónde sale

Dos vídeos más del mismo operador (Lozano, «programa Focus»). Casi todo lo que
enseña ya está medido y cerrado: FVG, order block, killer block, 50 % de Asia,
R:R 1:12 (`RESULTADOS_rr_extremo.md`, del mismo día).

**Salvo una cosa**, que repite en los dos vídeos:

> *«si en euro voy a buscar compras, en DAX tengo que tener esas posibles
> ventas»* · *«aunque hayamos tenido un SMT y el DAX no haya conseguido llegar
> a barrer su máximo de Asia»*

Eso es **divergencia SMT**: dos instrumentos correlacionados, uno barre su nivel
y el otro no. Quien no barre «delata» que el barrido del otro era falso.

**Es la primera idea de toda la serie que no es un patrón de un solo gráfico.**
Por eso merece medirse aunque el resto esté cerrado.

## El diseño, que es lo que hace que esta prueba valga

No se mide si el barrido funciona —eso ya está medido y sale en el precio justo—
sino **la diferencia entre dos brazos**:

```
  brazo A · CON divergencia   el EURUSD barre su nivel de Asia, el socio NO
  brazo B · SIN divergencia   los dos barren a la vez
```

Ambos brazos son la misma operación con la misma geometría. **Si el SMT es real,
A tiene que batir a B.** Y esa diferencia es inmune a que el nivel base salga en
el precio justo, que es el problema que ha tumbado las 30 pruebas anteriores.

**El contraste PRINCIPAL, declarado ahora: A − B, con el socio = DAX, entrada en
M5, R:R 2, los dos brazos juntos sobre Londres y Nueva York.**

## Qué se mide

| | |
|---|---|
| instrumento operado | **EURUSD** |
| socios | **DAX** (el suyo) y **oro** (declarado también: los dos cotizan contra el dólar, así que comparten factor) |
| niveles | máximo y mínimo de **Asia** (00:00-08:00 Madrid) de cada instrumento |
| ventanas | Londres 09:00-11:00 · Nueva York 14:00-16:30 |
| barrido | el precio supera el nivel y la vela de M5 **cierra de vuelta dentro** |
| divergencia | el socio **no** ha barrido su nivel correspondiente en las últimas **2 horas** |
| entrada | al cierre de la vela M5 que cierra dentro |
| stop | extremo del barrido + 1 pip |
| R:R | **2** (principal) · también 1, 3 y 5 |
| horizonte | hasta las 23:00 del mismo día |

Datos: EURUSD, DAX y oro en M1, **2023-2026** (donde se solapan los tres), unos
3,6 años.

## Potencia, calculada antes

Si quedan menos de **150 operaciones por brazo**, el error estándar de la
diferencia de aciertos pasa de 5,5 puntos y **no se podrá distinguir nada**. En
ese caso el resultado es «no se puede saber» y se dirá así.

## El sesgo de selección

2 socios × 4 R:R = **8 celdas**. El mejor de 8 sale **1,42 errores estándar** por
encima de la verdad. El principal está fijado arriba y sobre él no hay regalo.

## Criterio

1. La diferencia **A − B > 0** con el IC95 sin tocar el cero en el principal, **y**
2. el mismo signo con el **otro socio** (oro), **y**
3. el mismo signo **partido en dos mitades** por fecha.

Si A y B salen iguales, el SMT no aporta nada y queda cerrado con el resto.

## Predicción

- **A y B saldrán iguales**, con la diferencia entre −3 y +3 puntos y el cero
  bien dentro del intervalo.
- Motivo: para que el SMT funcione haría falta que la divergencia contenga
  información sobre la dirección futura, y todo lo medido en tres meses dice que
  la dirección futura tras un barrido está en su precio justo.
- **Habrá pocas operaciones**: espero 100-300 por brazo con el DAX.
- Si me equivoco y A bate a B por más de 5 puntos con el intervalo limpio, sería
  el primer patrón de gráfico intradía con ventaja real del proyecto, y habría
  que replicarlo cambiando el instrumento operado antes de creérselo.

Van quince predicciones con errores. Ésta también puede fallar.
