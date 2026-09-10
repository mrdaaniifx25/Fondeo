# El hallazgo por temporalidad, partido en dos mitades

## Qué es esto y qué no es

`RESULTADOS_crt_temporalidad.md` —el mejor resultado del proyecto— corrió sobre
**2020-2026 entero**. Es decir, quemó el conjunto que `BC_00` §a reservaba. No se
puede confirmar limpiamente, porque el hallazgo ya vio esos datos.

Lo que sí se puede hacer es partirlo por la mitad y ver si el neto positivo vive
en las dos o sale de una sola. **Un hallazgo que solo aparece en una mitad es
ruido con buena presentación.**

## El corte

| TF | n | coste | bruta | **neta** | | n | coste | bruta | **neta** | | dif bruta | z |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| | | 2020-2023 | | | | | 2024-2026 | | | | | |
| H1 | 28.227 | 14,6 % | +0,096 | −0,139 | | 19.181 | 14,0 % | +0,073 | −0,144 | | −0,023 | −1,68 |
| H2 | 13.872 | 10,1 % | +0,159 | −0,001 | | 9.308 | 9,6 % | +0,092 | −0,059 | | −0,067 | −1,02 |
| H4 | 6.809 | 6,8 % | +0,082 | −0,023 | | 4.583 | 6,5 % | +0,063 | −0,040 | | −0,019 | −0,65 |
| H8 | 2.945 | 4,7 % | +0,073 | +0,001 | | 1.985 | 4,3 % | +0,051 | −0,017 | | −0,022 | −0,50 |
| **H12** | 1.822 | 3,6 % | +0,140 | **+0,085** | | 1.286 | 3,1 % | +0,104 | **+0,055** | | −0,036 | −0,60 |
| D1 | 1.156 | 2,3 % | +0,050 | +0,019 | | 796 | 2,4 % | +0,030 | −0,005 | | −0,020 | −0,33 |

```
neta positiva en 2020-2023 :  H8, H12, D1
neta positiva en 2024-2026 :  H12
positiva en LAS DOS        :  H12
```

## H12 con intervalos honestos

```
n = 1.286   R:R mediano 1,38   aciertos 47,4 %
R neta media                   +0,0546
error estándar por bloques      0,0414   ->   z +1,32
IC 95 %                        [-0,027, +0,136]     ← incluye el cero
media recortada al 1 % superior +0,0324
```

Por instrumento, quien lo sostiene es uno solo:

| | n | neta | z |
|---|---|---|---|
| SPX500 | 288 | **+0,158** | +1,66 |
| NAS100 | 269 | +0,047 | +0,55 |
| USDJPY | 301 | +0,031 | +0,35 |
| EURUSD | 218 | +0,016 | +0,14 |
| GBPUSD | 210 | −0,002 | −0,02 |

**En EURUSD, que es lo que vas a operar, es +0,016 con z +0,14.** Es cero.

Por año: 2024 −0,031 · 2025 +0,075 · 2026 +0,148.

## Y una cosa incómoda que no había mirado

Las seis diferencias entre la segunda y la primera mitad:

```
H1 −0,023   H2 −0,067   H4 −0,019   H8 −0,022   H12 −0,036   D1 −0,020
```

**Seis de seis negativas.** Ninguna es significativa por sí sola —los z van de
−0,33 a −1,68— pero que las seis apunten al mismo sitio no es casualidad: prueba
de signos **p = 0,031**.

La ventaja bruta del CRT es menor en 2024-2026 que en 2020-2023, en todas las
temporalidades a la vez. Puede ser deriva de mercado, puede ser que 2020-2021
fuera un régimen raro, puede ser ruido correlacionado entre temporalidades que
comparten las mismas barras. Lo que no se puede es suponer que el número de
2020-2023 sigue vigente.

## Lectura

H12 es lo único que aguanta el corte, y aguanta **débilmente**: positivo en las
dos mitades, significativo en ninguna, sostenido sobre todo por SPX500, y en
EURUSD es exactamente cero.

No es una estrategia. Es, como mucho, el único sitio donde seguir mirando.
