# Por qué no se mecaniza · el intento de aprender su criterio

Post hoc y declarado como tal: los datos del bloque 6 ya estaban recogidos. La
protección no es el preregistro sino la **validación fuera de muestra dejando
fuera una sesión entera**, para que ninguna rotura entrene con otra de su día.

Material: las **250 roturas** del examen del 4 de septiembre, con su SÍ/NO en cada
una, contra **17 variables** de todo lo que se ve en pantalla en ese minuto —
cuerpo y rango de la M5 de referencia, impulso a 10/30/60 minutos, rango de los
últimos 30, distancia al alto y al mínimo de Asia, ancho de Asia, posición dentro
del rango del día, tendencia de la M15 y de la H1 ya cerradas, stop, hora,
minutos desde la rotura anterior y dirección.

## 1 · Su SÍ/NO no se aprende

| | AUC dentro de muestra | AUC **fuera** de muestra |
|---|---|---|
| λ = 0,3 | 0,635 | **0,502** |
| λ = 1 | 0,633 | **0,502** |
| λ = 3 | 0,632 | 0,503 |
| λ = 10 | 0,634 | 0,510 |

0,50 es una moneda. **El modelo memoriza sus decisiones y no generaliza ninguna.**

## 2 · El desenlace tampoco

| | dentro | **fuera** |
|---|---|---|
| λ = 1 | 0,665 | **0,445** |
| λ = 10 | 0,669 | 0,483 |

Por debajo de 0,50: el gráfico no dice lo que va a pasar.

## 3 · Copiar el criterio aprendido pierde más que no copiarlo

| quién elige | n | acierto | R neta |
|---|---|---|---|
| todas, la regla a ciegas | 250 | 22,4 % | −0,477 |
| **él** | 145 | **26,9 %** | **−0,262** |
| copia de su criterio, top 50 % | 125 | 16,0 % | −0,633 |
| copia de su criterio, top 30 % | 75 | 13,3 % | −0,664 |
| modelo del desenlace, top 30 % | 75 | 14,7 % | −0,832 |

*(acierto contando el «cierre por hora» como fallo, ver abajo)*

## 4 · Corrección al resultado publicado del examen de roturas

`RESULTADOS_roturas.md` comparó el acierto **sobre las resueltas**: 34,8 % contra
18,7 %, +16,1 puntos. Al auditarlo aquí aparece que **no descarta el mismo
porcentaje de operaciones sin resolver en los dos grupos**:

```
  las que toma:  33 cierres de 145  (22,8 %)
  las que deja:  14 cierres de 105  (13,3 %)
```

Es decir, el corte «sobre resueltas» le quitaba más operaciones neutras al grupo
que él tomó. Con la contabilidad estricta:

| métrica | toma | deja | diferencia | z |
|---|---|---|---|---|
| acierto contando el cierre como fallo | 26,9 % | 16,2 % | +10,7 pt | **+2,00** |
| **R neta por operación** | **−0,262** | **−0,773** | **+0,511** | **+3,27** |

**El contraste aguanta, y en dinero aguanta mejor que en acierto.** El +16,1 de
puntos estaba algo inflado; el hallazgo no.

## Lo que esto significa

No es que su criterio no exista: el punto 4 dice que existe y con z +3,27. Es que
**no es una función de esas diecisiete variables**. Lo que decide no está en el
OHLC del minuto ni en nada que yo sepa derivar de él.

Cerrado, entonces, el último camino mecánico: ni describiendo su regla, ni
midiendo el mercado, ni aprendiendo de sus propias decisiones etiquetadas.

## Reproducir

`python3 bt/aprende_su_criterio.py`
