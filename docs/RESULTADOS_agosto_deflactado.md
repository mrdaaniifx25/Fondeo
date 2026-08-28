# Agosto 2026, recalculado · y las variantes 09:00

Fecha: 28 de agosto de 2026.

Dos resultados que hay que leer juntos. Ninguno anula al otro.

---

## 1. Su agosto, con las operaciones que no tomó

De los 17 disparos de su regla en agosto, él tomó 4. De los 13 restantes, en
**11** contestó lo mismo: *"no estaba pendiente del gráfico pero sí hubiese
tomado la operación"*. Las otras dos (07-ago y 17-ago, ambas de tipo A) las
habría entrado en otra vela y con otro stop: no son la misma operación y
quedan fuera.

Esas 11: **2 TP y 9 SL**, acierto 18,2 %, R bruta media −0,455.

| escenario | ops | días | acierto | neta/día | z | euros a 150 € |
|---|---|---|---|---|---|---|
| tal como lo operó | 24 | 16 | 75,0 % | **+0,979** | **+3,29** | +3 590 € |
| si hubiese estado delante siempre (+11) | 35 | 19 | 57,1 % | **+0,440** | **+1,49** | +2 363 € |
| delante pero sólo desde las 09:00 (+6) | 29 | 19 | 65,5 % | **+0,672** | **+2,28** | +3 084 € |

**Lo que esto significa.** Parte de su mes la produjo su disponibilidad, no su
criterio. Estar delante de la pantalla no es una regla que se pueda escribir ni
repetir. Con las 11 dentro, el mes deja de ser significativo: z +1,49 es
compatible con la suerte.

Ojo con la fila de las 09:00: de las 11, **6 caen entre las 08:00 y las 09:00**
(1 TP y 5 SL). Su filtro horario recorta la parte peor de lo que se saltó, pero
es un filtro que él enunció *después* de ver esos resultados. Sirve para
entender, no para probar.

Reproducible: `python3 bt/agosto_deflactado.py`.

---

## 2. Las variantes de la regla en 2020-2025

`bt/asia_nivel_variantes.py`. **Exploratorio**: son especificaciones nuevas
sobre datos ya vistos. La prueba limpia fue `bt/asia_nivel.py` y está cerrada.

Se probaron los dos matices que él añadió después: empezar a las 09:00 en vez
de a las 08:00, y poner el stop al otro lado del nivel de Asia cuando la
entrada queda pegada al nivel.

```
2020-2025 · UNIDAD: EL DÍA          (n = días con al menos un disparo)
                                           n  riesgo     %TP  BRUTA/d      z   NETA/d      z
pre-registrada (08:00, stop vela)       1441    7.0p   30.8%   +0.024  +0.72   -0.282  -7.55
desde las 09:00 (lo que él dice)        1253    7.5p   32.6%   +0.016  +0.43   -0.263  -6.34
09:00 + stop al nivel si <5p            1253    7.5p   32.4%   +0.011  +0.28   -0.191  -5.12
09:00 + stop al nivel si <8p            1253    7.6p   32.3%   +0.009  +0.25   -0.189  -5.06
```

**Lo que esto significa.** Ninguna variante cruza el cero. El %TP se queda
pegado al 33,3 % que da la pura geometría de un 1:2 en las cuatro. El stop al
nivel mejora la neta (de −0,282 a −0,189) porque agranda el riesgo y diluye el
spread, no porque acierte más: el %TP incluso baja un poco. El filtro de las
09:00 quita 188 días (446 disparos) y no cambia el signo.

Es decir: los dos matices son mejoras reales de ingeniería del stop, pero no
convierten la regla en rentable. Lo que la regla no tiene, en seis años, es
ventaja de dirección.

---

## Dónde queda esto

- La regla, tal como está escrita, no gana en 2020-2025 en ninguna de las
  cuatro versiones probadas.
- Su agosto sigue siendo real y verificado al minuto (14 de 14 de acuerdo con
  su herramienta en las que hay datos M1), pero con las 11 que dice que habría
  tomado, cae a z +1,49.
- La diferencia entre las dos cosas es la **selección**: la regla dispara ~75
  veces al mes y él toma ~2. Lo que decide esas 2 no está escrito todavía.

**Lo único que puede resolverlo es el registro hacia delante**: anotar cada
operación *antes* de saber el resultado, incluidas las que se salta y por qué.
Sin eso, no hay forma de distinguir criterio de disponibilidad.


---

## Adenda · tres objeciones comprobadas

`bt/agosto_objeciones.py`.

**1. El filtro horario no es "de 8 a 9 no opero".** En sus 25 entradas reales
hay **0 antes de las 08:20** pero **6 entre las 08:20 y las 09:00** (el 24 % de
su mes). Lo que su registro sostiene es "no entro en los primeros 20 minutos",
no "no opero la primera hora". Con ese filtro — el único que sus datos
respaldan — sólo salen 3 de las 11, y queda z **+1,84**.

**2. La mecánica del stop no rescata a las 11.** Se resimularon con SU
colocación (2,5 p al otro lado del nivel de Asia) en vez de la de la regla
(al otro lado de la vela anterior). Riesgo mediano 5,5 p → 3,7 p, y el
resultado **no cambia: 2 TP / 9 SL**. Además las entradas de esas 11 quedaban
a 0,1-3,2 p del nivel, o sea que tampoco entraban peor que él.

**3. "Suerte" es la palabra equivocada.** El binomial contra el 33,3 %:

| escenario | acierto | 1 entre |
|---|---|---|
| como lo operó | 75,0 % | 27 794 |
| + las 11 | 57,1 % | 311 |
| + las 8 (>= 08:20) | 59,4 % | 450 |
| + las 6 (>= 09:00) | 65,5 % | 2 545 |

Ninguno de esos números es suerte. z +1,49 significa *19 días no bastan para
demostrarlo*, no *queda demostrado que no lo hay*.

**4. Y queda el hecho que no explica nada de lo anterior:** sus compras
hicieron 11 de 12 (92 %); las compras de esas mismas 11 hicieron 2 de 9 (22 %).
Mismo lado, mismo nivel, mismo mes, resultado opuesto. Lo que las separa no es
la dirección, ni el stop, ni la hora.
