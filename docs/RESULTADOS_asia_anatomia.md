# Anatomía · por qué unas van al stop y otras al objetivo

Exploratorio. **Nada de este documento es un hallazgo**: son candidatos sacados
de datos ya vistos, con veintiocho contrastes encima. Fecha: 2026-08-28.

Población: **1.428 operaciones**, EURUSD M5, 2020-2026, regla laxa con un setup
por día. Se usa el histórico y no sus 37 porque con 37 no hay potencia para nada.

## El hallazgo que más explica no es un filtro, es un reloj

| | mediana | a los 30 min |
|---|---|---|
| las que acaban en el **stop** | **21 min** | **44,9 %** del total ya ha perdido |
| las que acaban en el **objetivo** | **52 min** | **7,5 %** del total ha ganado |

Reparto final tras ocho horas: 73 % stop, 25 % objetivo, 2 % sin resolver.

A la media hora casi la mitad de la baraja está decidida, y decidida en contra.
Después, la curva del stop se aplana y la del objetivo sigue subiendo despacio:
**las ganadoras necesitan tiempo y las perdedoras no.** Eso explica el 19 contra
7 de su segunda baraja mejor que cualquier variable de entrada.

## Sus tres hipótesis

### 1 · «algunas pueden ser por la hora de entrada» — a medias

El efecto existe bajo su regla y **desaparece cuando se iguala el tiempo**:

| | antes de las 10 vs desde las 10 | z |
|---|---|---|
| cerrando a las 14:00 (su regla) | +0,300 R | **+3,30** |
| horizonte fijo de 4 h desde la entrada | +0,052 R | +0,52 |

Correlación con la hora, horizonte fijo: **+0,007**. No es que el setup de las
12:00 sea peor. Es que a las 12:00 quedan dos horas, el stop llega en 21 minutos
y el objetivo necesita 52.

*Nota metodológica:* un test de rangos sobre la regla original daba z +4,59 en el
sentido contrario. Es un espejismo de la truncadura: las tardías esquivan el −1
porque se quedan a medias, no porque acierten más. El de medias es el bueno.

### 2 · «he entrado lejos del high o low» — no es eso

| | %TP | R bruta |
|---|---|---|
| entrada pegada al nivel (Q1) | 24,9 % | +0,071 |
| entrada lejos del nivel (Q4) | 17,1 % | +0,016 |

Diferencia −0,041, **z −0,37**. El acierto baja pero la R no se mueve: cuando se
entra lejos del nivel el objetivo también queda más cerca, y se compensa solo.

### 3 · «liquidez de otra sesión que el precio vaya a buscar» — la dirección sí

Máximos y mínimos de ayer: del día, de la sesión de Londres y de la de NY.

| nivel de ayer por detrás de la entrada | n | R bruta |
|---|---|---|
| a menos de 1 R | 243 | **−0,128** |
| entre 1 y 3 R | 309 | +0,062 |
| a más de 3 R, o ninguno | 876 | −0,007 |

**z +1,06.** Es la mejor de las tres ideas y va en el sentido que él dice, pero
el tramo intermedio sale mejor que los extremos, y eso es lo que hacen los datos
cuando no hay señal.

## Las dieciocho variables, ordenadas

Incluye la tipología de vela de la documentación: cuerpo, mechas, y lo de *«la
mecha se lleva el nivel pero el cuerpo queda del otro lado»*.

| variable | tercil bajo | tercil alto | dif | z |
|---|---|---|---|---|
| mecha de rechazo del gatillo | +0,075 | −0,136 | −0,211 | −1,98 |
| volatilidad previa (ATR M5) | +0,056 | −0,147 | −0,203 | −1,96 |
| mecha que se lleva el nivel | +0,125 | −0,071 | −0,196 | −1,83 |
| el gatillo cierra dentro del rango | −0,065 | +0,109 | +0,174 | +1,83 |
| día de la semana | +0,092 | −0,075 | −0,168 | −1,65 |
| cierre pasado el nivel | +0,097 | −0,068 | −0,165 | −1,55 |
| hora de entrada | +0,046 | −0,079 | −0,125 | −1,42 |
| atractor detrás de la entrada | −0,059 | +0,065 | +0,124 | +1,24 |
| distancia entrada-nivel (en R) | +0,019 | −0,023 | −0,041 | −0,37 |
| cuerpo del gatillo (pips) | +0,014 | +0,022 | +0,008 | +0,07 |
| dónde cae la entrada en el rango | −0,062 | −0,055 | +0,008 | +0,07 |
| mecha contraria del gatillo | +0,002 | +0,007 | +0,005 | +0,04 |

Con 28 contrastes hace falta **|z| ≥ 3,1**. El máximo es 1,98: **ninguno llega.**
Pero los cuatro primeros describen lo mismo — barrido corto, vuelta de cuerpo
limpio, mercado tranquilo, cierre de vuelta dentro del rango — que es la *turtle
soup* de manual. `exceso` y `mecha_niv` correlan 0,99: son la misma variable.

## El mejor filtro posible, y su techo

Las dos piezas con motivo propio: entrar antes de las 10:00 (su hipótesis) y que
el gatillo cierre dentro del rango (su documentación).

| subconjunto | n | %TP | geometría | bruta | neta | z |
|---|---|---|---|---|---|---|
| todo | 1.428 | 21,8 % | 33,3 % | −0,012 | −0,261 | −5,87 |
| antes de las 10:00 | 764 | 25,9 % | 33,3 % | +0,046 | −0,195 | −3,00 |
| cierra dentro del rango | 433 | 29,8 % | 33,3 % | +0,109 | −0,108 | −1,39 |
| **las dos cosas** | 288 | **33,7 %** | 33,3 % | +0,199 | **−0,013** | −0,13 |

El acierto del mejor subconjunto es **33,7 % contra una geometría de 33,3 %**:
no aporta información sobre la dirección. Lo único que consigue es que el coste
deje de comerse el resultado — la neta pasa de −0,261 a −0,013. **De perder a
empatar. Nunca a ganar.**

## Y en sus veintiséis no separa

- **15 de sus 19 stops** cerraron dentro del rango. Y **6 de sus 7 objetivos**
  también.
- **9 de sus 19 stops** entraron a las 8:00, la mejor hora de la población.
- Mecha del barrido mediana: 3,4 p en los stops, 3,8 p en los objetivos. Al revés.
- **10 de sus 19 stops nunca llegaron ni a media R a favor.** No se torcieron:
  no arrancaron.

Ese último punto es la respuesta corta: la mayoría de sus stops no son entradas
mal puestas, son entradas donde la vuelta no se produjo — y eso pasa el 73 % de
las veces por diseño.

## Qué haría falta para creerse algo

Fijar por escrito «barrido corto, vuelta limpia, antes de las 10:00» con sus
umbrales y probarlo **una sola vez** donde no se ha mirado nunca: el oro y el DAX
de 2026 en `reservado/`, y el oro y el DAX de 2023-2025, que jamás se han tocado
con esta estrategia.

Aunque la última fila ya marca el techo: **empatar**. Con stops de cinco a ocho
pips y 1,2 de diferencial, no hay filtro que convierta esto en una estrategia de
cuenta de fondeo.

## Ficheros

```
bt/asia_anatomia.py                    construye las 1.428 con 18 rasgos y las resuelve
data/asia_anatomia.csv                 la tabla completa, con tiempos hasta cada nivel
data/asia_anatomia_graficos.json       datos de los dos gráficos
docs/asia_anatomia.html                el informe
```
