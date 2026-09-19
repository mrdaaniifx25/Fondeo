# Resultados · Seguimiento de tendencia

Ejecución del protocolo de `PREREGISTRO_tendencia.md`.

**Resultado: negativo en los dos contrastes primarios.** Operar a favor de la
rotura no funciona mejor que operar en contra. Las dos mitades de la moneda
valen cero.

---

## Los dos contrastes primarios

| | n | bruto/op | z | p | PF neto | veredicto |
|---|---|---|---|---|---|---|
| **T1** divisas · N=55 · salida Turtle | 86 | +0,0721 | +0,32 | 0,7482 | 1,104 | **falla** |
| **T2** índices · N=55 · salida Turtle | 50 | +0,3470 | +1,44 | 0,1503 | 1,667 | **falla** |

| Criterio | T1 | T2 |
|---|---|---|
| 1 · n ≥ 200 | ✗ (86) | ✗ (50) |
| 2 · ventaja bruta p < 0,05 | ✗ (0,748) | ✗ (0,150) |
| 3 · PF neto > 1 | ✓ (1,104) | ✓ (1,667) |
| 4 · espejo negativo | ✓ (−0,2642) | ✓ (−0,1544) |
| 5 · supera a la entrada al azar | ✗ (percentil 40) | ✗ (percentil 75) |
| 6 · supera a comprar y mantener | — | ✗ (+9,9 % vs **+218,6 %**) |

## Las ocho celdas, incluidas las seis de robustez

| N | salida | divisas n / bruto / p | índices n / bruto / p |
|---|---|---|---|
| 55 | Turtle **(primaria)** | 86 · +0,0721 · 0,748 | 50 · +0,3470 · 0,150 |
| 55 | 3R | 94 · −0,0926 · 0,581 | 59 · +0,5659 · **0,025** |
| 20 | Turtle | 206 · −0,1362 · 0,083 | 123 · +0,1788 · 0,111 |
| 20 | 3R | 119 · +0,1351 · 0,397 | 84 · +0,2495 · 0,213 |

Por instrumento, celda primaria: EURUSD +0,127 · GBPUSD −0,122 · USDJPY +0,213 ·
NAS100 +0,393 · SP500 +0,301.

La celda más vistosa de toda la tabla es índices con N=55 y objetivo 3R:
**+0,5659 con p 0,025**. Es exactamente la celda que uno escogería si quisiera
venderse a sí mismo un resultado. No es la primaria, tiene n=59, con ocho celdas
el umbral de Bonferroni sería p < 0,00625, y el control 6 la destroza igual que a
las demás. Queda registrada aquí precisamente para no escogerla.

## Los tres controles, y lo que enseñan

### Espejo

Con salida Turtle el espejo es **degenerado y no informativo**: al invertir una
rotura, el Donchian opuesto queda pegado al precio de entrada, el 1R tiende a
cero y la R estalla (divisas +0,41 con z de solo +0,45 sobre 243 operaciones, y
una duración media de 5,1 días frente a 31). Es aritmética, no señal.

El espejo válido es el del brazo 3R, con stop fijo: **divisas −0,2642, índices
−0,1544**. Sale negativo, que es lo coherente. Este control se pasa.

### Entrada al azar · aquí está la lección de todo el proyecto

20 repeticiones de entradas en días aleatorios con idéntica gestión:

| | azar (media de 20 rep.) | dispersión | rango observado | estrategia | percentil |
|---|---|---|---|---|---|
| divisas | **+0,1682** | ±0,3350 | −0,3964 a +0,8178 | +0,0721 | **40** |
| índices | +0,0449 | ±0,5962 | −0,7069 a +1,9901 | +0,3470 | **75** |

En divisas, entrar al azar rinde **más** que entrar en la rotura. Y mírese la
dispersión: con este número de operaciones, cualquier cifra entre −0,40 y +0,82
es ruido normal en divisas, y entre −0,71 y +1,99 en índices.

**Ese es el problema de fondo de estos sistemas: producen entre 25 y 90
operaciones en seis años y medio, y con esa muestra el error de medición se come
cualquier ventaja plausible.** No es que no se encuentre la ventaja. Es que con
50 operaciones no se podría distinguir una ventaja real del azar aunque
existiera.

### Comprar y mantener

| | estrategia (riesgo 1 %, compuesto) | comprar y mantener |
|---|---|---|
| NAS100 | +9,9 % | **+218,6 %** |
| SP500 | +7,3 % | **+130,0 %** |

Un sistema largo/corto sobre un activo que se triplica en seis años tiene que
batir a no hacer nada. No lo hace, ni de lejos. Lo poco positivo que se veía en
índices era deriva alcista mal medida.

## Defecto de mi propio motor que encontró el control

En la primera ejecución el control de entrada aleatoria salió +0,1676 con
p 0,0018: un resultado imposible que delataba un fallo mío. Lo era. Yo
normalizaba toda R por 2×ATR, pero con salida Turtle el Donchian opuesto puede
estar más cerca que el 2×ATR, de modo que las pérdidas reales eran menores de 1R
mientras el denominador seguía siendo el grande. Eso inflaba la R de forma
sistemática.

Corregido: el 1R pasa a ser la distancia al stop **realmente vigente** el primer
día. Las cifras primarias apenas se movieron (T1 y T2 no cambian: tras una rotura
de 55 días el Donchian opuesto queda lejos), pero el control cayó de +0,1676 a
+0,1589 y el de índices de +0,0439 a −0,0067.

Segundo defecto, también corregido: agrupar las 1.195 operaciones de las 20
repeticiones y sacar un z de ahí infla el estadístico, porque las repeticiones
solapan en el mismo periodo y el mismo instrumento y no son independientes. Se
resume por repetición.

Los controles no están para adornar el informe. Están para esto.

## Conclusión

Se cierra también esta vía. Sumado a lo anterior:

- **Reversión** (CRT, turtle soup, barrido, order block): cero, en 5 mercados.
- **Tendencia** (Donchian 20/55, Turtle canónico): cero, en los mismos 5 mercados.
- Ninguna de las dos supera a entrar al azar con la misma gestión.
- En índices, ninguna supera a comprar y mantener.

Las dos familias mecánicas grandes que se pueden construir con solo el precio
están medidas y las dos dan cero. Lo que quede tendrá que venir de una entrada
distinta a «una figura en el gráfico»: calendario, flujo, tipos, o sección
cruzada entre instrumentos. Nada de eso está probado todavía.
