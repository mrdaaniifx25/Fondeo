# Resultados · la réplica de «vuelta limpia» en oro y DAX

Pre-registro: `PREREGISTRO_asia_limpia.md`, commit `faf6047`, escrito antes de
abrir los ficheros de 2026 y antes de tocar oro o DAX con esta estrategia.
Ejecutado una vez. Fecha: 2026-08-28.

## Veredicto: NO REPLICA

Prueba principal declarada: **el oro**, los dos periodos juntos.

| | n | %TP | geometría | coste/riesgo | bruta | neta | z |
|---|---|---|---|---|---|---|---|
| todas | 600 | 20,5 % | 33,3 % | 19,3 % | +0,187 | −0,070 | −0,78 |
| **cumple el filtro** | 59 | 18,6 % | 33,3 % | 16,7 % | **−0,096** | −0,279 | −1,32 |
| no cumple | 541 | 20,7 % | 33,3 % | 19,6 % | +0,218 | −0,048 | −0,49 |

Diferencia **−0,314**, z −1,34. El umbral pedía ≥ +0,13 con z ≥ 1,96 y neta ≥ 0.

**El filtro va en el sentido contrario en el oro.** No es que se quede corto: le
sale del revés. En EURUSD el subconjunto filtrado era el bueno (+0,218 contra
−0,043); en el oro es el malo (−0,096 contra +0,218).

Con eso, **se cierra la familia del barrido de Asia**: dos barajas ciegas, 150
cortes etiquetados, 1.428 operaciones diseccionadas con 28 contrastes, y una
réplica fallida en otro instrumento.

## El DAX dice lo contrario, y hay que contarlo

| | n | %TP | geometría | bruta | neta | z |
|---|---|---|---|---|---|---|
| **GRXEUR 2023-2025**, todas | 470 | 21,9 % | 33,3 % | −0,009 | −0,149 | −2,04 |
| GRXEUR 2023-2025, cumple | 40 | **42,5 %** | 33,3 % | **+0,688** | **+0,579** | +1,78 |
| GRXEUR 2026, todas | 122 | 20,5 % | 33,3 % | −0,155 | −0,240 | −1,80 |
| GRXEUR 2026, cumple | 11 | **45,5 %** | 33,3 % | **+0,331** | +0,278 | +0,61 |

Diferencia cumple − no cumple: **+0,762 (z +2,30)** en 2023-2025 y **+0,535
(z +1,11)** en 2026. Mismo signo en los dos tramos, y los únicos netos positivos
de todo el ejercicio.

Y aun así **no cambia el veredicto**, por lo que quedó escrito antes de mirar:

- El DAX era **secundario declarado**, porque el CFD sólo tiene **307 de los 480
  minutos** de la ventana de Asia. Su «rango de Asia» se construye con huecos.
- El pre-registro dice, literalmente: *«Si el DAX y el oro discrepan, manda el
  oro, y queda dicho ahora para que no se elija después.»*
- n = 40 y n = 11. Y es uno de los varios contrastes de esta misma pasada.

Lo honesto es dejarlo escrito como lo que es: **una pista que ya no se puede
probar.** No queda DAX sin usar. Contrastarla exigiría datos nuevos —otro índice
europeo, u otro proveedor— y sería otro pre-registro, no éste.

## De paso, dos cosas sobre el oro

La regla base **sí tiene ventaja bruta** en el oro: +0,187 R sobre 600
operaciones. Lo que la mata es el coste. El **coste de equilibrio** sale en
**24 unidades de 0,01 = 0,24 USD**, y el pre-registro asumía 0,35 USD. Con un
spread de oro por debajo de 0,24 la regla base empataría; por encima, pierde.
Cada uno con el suyo.

Y el acierto del oro es **20,5 % contra una geometría de 33,3 %**: por debajo.
La bruta positiva no viene de acertar más, viene de que la rama de compra apunta
al alto de Asia, que a veces está mucho más lejos de 2 R.

## Lo que quedó escrito antes y se cumplió

Del pre-registro: *«Que la regla sin filtrar salga negativa en neto en los dos
instrumentos, y que el filtro no llegue al umbral: +0,261 con z +1,93 sobre
datos ya vistos, después de 28 contrastes, es exactamente el tamaño de efecto
que suele evaporarse al replicar.»*

Se cumplió en el oro. En el DAX no. Una de dos no es un buen historial de
predicción, y así queda anotado.

## Ficheros

```
bt/load_reservado.py     abre los ZIP de reservado/ en parquet propios
bt/asia_limpia.py        la pasada, ejecutada una vez
data/asia_limpia.csv     las 1.192 operaciones resueltas, con su bloque
```
