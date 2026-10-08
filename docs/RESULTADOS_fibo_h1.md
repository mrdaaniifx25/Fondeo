# El fibo en H1 · lo primero con ventaja bruta, y por qué tampoco llega

Continuación de `RESULTADOS_barrido_dia_fibo.md`. Él preguntó si se había
equivocado de temporalidad. Se probó el fibo en M1, M5, M15 y H1.

## 1 · Sí importa la temporalidad, y sube con ella

EURUSD, fibo 0,790, objetivo 1:2:

| fibo dibujado en | acierto | R bruta | R neta |
|---|---|---|---|
| M1 | 33,5 % | +0,012 | −0,248 |
| M5 | 33,9 % | +0,026 | −0,235 |
| M15 | 34,7 % | +0,048 | −0,213 |
| **H1** | **34,9 %** | **+0,055** | −0,202 |

Monótono. Y en H1, positivo en 4 de 4 instrumentos: +0,055 · +0,100 · +0,043 ·
+0,047.

## 2 · Y aguanta fuera de muestra. Es lo primero del proyecto que lo hace

| época | n | acierto | R bruta | z |
|---|---|---|---|---|
| 2020-2022 | 9.153 | 35,7 % | +0,075 | **+5,04** |
| 2023-2026 | 11.587 | 34,9 % | +0,053 | **+4,04** |

Positivo en **8 de 8** celdas instrumento × época. No es ruido.

## 3 · Pero la ventaja vive pegada al stop estrecho, y ahí es donde el coste mata

El stop está un COLCHÓN de la pierna pasado el extremo barrido. Ensanchándolo:

| colchón | stop EURUSD | acierto | R bruta | R neta |
|---|---|---|---|---|
| **0,10** | 6,8 p | **35,2 %** | **+0,056** | −0,201 |
| 0,35 | 12,2 p | 33,4 % | +0,014 | −0,129 |
| 0,75 | 20,9 p | 31,1 % | −0,027 | −0,110 |
| 1,50 | 37,3 p | 29,1 % | −0,011 | −0,058 |

**La ventaja se evapora en cuanto el stop se ensancha.** No es una ventaja
direccional: es un efecto de *colocación del stop* —un precio que barre un nivel
y cierra de vuelta tiende a no volver enseguida al extremo—, y solo existe con el
stop pegado a ese extremo.

Y ese es exactamente el stop que hace el coste inasumible. **La ventaja y el coste
están acoplados**: no se puede tener una sin el otro. La palanca del stop ancho,
que era la idea de `RESULTADOS_donde_operar.md`, no sirve aquí.

## 4 · Lo más cerca que se llega

| instrumento | stop | coste/riesgo | R bruta | **R neta** |
|---|---|---|---|---|
| **NSXUSD** | 25,8 pt | 5,8 % | +0,047 | **−0,029** |
| GBPUSD | 8,9 p | 18,0 % | +0,106 | −0,110 |
| USDJPY | 9,4 p | 16,0 % | +0,046 | −0,155 |
| EURUSD | 6,8 p | 21,0 % | +0,056 | −0,201 |

Con el coste estimado del Nasdaq (1,5 puntos, **no verificado**) se queda en
−0,029. Lo más cerca de cero de todo el proyecto, y sigue siendo negativo.

## Lo que hay que decir del método

Esto es **exploratorio**: se han barrido 4 temporalidades × 4 fibos × 2 objetivos
× 4 instrumentos, más los colchones. Con ese número de celdas aparecen cosas por
azar. Lo que sostiene el hallazgo no es el tamaño sino la consistencia: monótono
en temporalidad, 4 de 4 instrumentos, 8 de 8 fuera de muestra. Aun así, **antes de
tratarlo como real haría falta un preregistro y un pase limpio**.

Y en todo caso no cambia la conclusión práctica: **0 de 128 celdas con R neta
positiva.**

## Reproducir

`TF=60 COLCHON=0.10 python3 bt/barrido_dia_fibo.py EURUSD GBPUSD USDJPY NSXUSD`
