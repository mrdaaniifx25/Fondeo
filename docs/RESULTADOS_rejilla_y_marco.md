# Dos comprobaciones sobre el marco del curso

Nacen de una pregunta suya: *«nos estamos centrando en H4 únicamente, ¿es
correcto?»*. Son dos cosas distintas y conviene separarlas.

## 1 · ¿La investigación ha sido sólo H4? No

`RESULTADOS_crt_temporalidad.md` cubre siete temporalidades (H1 → D1) en cinco
instrumentos, y `RESULTADOS_h12_ciego.md` añade una pasada ciega pre-registrada
en oro y DAX. Lo que sí es casi todo H4 es **el curso** —lecciones 4, 5 y 6—, y
esa elección la tomé yo por razones didácticas, no porque los números la
respalden.

## 2 · El desglose de H4 por instrumento, que no estaba publicado

La tabla de temporalidad daba la media de los cinco. Desglosada:

| instrumento | n | ops/año | acierto | riesgo med. | coste %R | R bruta | ±IC95 | **R neta** | z |
|---|---|---|---|---|---|---|---|---|---|
| EURUSD | 2.298 | 348 | 49,2 % | 12,9 | 9,3 % | +0,146 | 0,074 | **+0,009** | +0,23 |
| GBPUSD | 2.345 | 355 | 46,2 % | 16,9 | 8,9 % | +0,037 | 0,059 | **−0,089** | −2,92 |
| USDJPY | 2.355 | 357 | 49,2 % | 17,9 | 7,3 % | +0,105 | 0,059 | **−0,011** | −0,35 |
| NAS100 | 2.199 | 333 | 46,8 % | 45,3 | 3,3 % | +0,051 | 0,070 | **+0,002** | +0,06 |
| SPX500 | 2.195 | 333 | 46,9 % | 10,7 | 5,6 % | +0,031 | 0,060 | **−0,059** | −1,92 |
| media ponderada | 11.392 | 1.726 | | | | +0,075 | | **−0,030** | 2/5 positivos |

**H4 es el marco que peor sale de todos los que aguantan una tabla.** Los dos
«positivos» son +0,009 y +0,002, es decir cero. El curso se está dando sobre el
marco que la aritmética rechaza.

Para que conste, el mismo desglose en H12 —el único marco donde los cinco salen
positivos a la vez, y la única configuración de todo el proyecto que no ha
cambiado de signo entre instrumentos:

| instrumento | n | ops/año | coste %R | R bruta | **R neta** | z |
|---|---|---|---|---|---|---|
| EURUSD | 516 | 78 | 5,4 % | +0,129 | +0,049 | +0,64 |
| GBPUSD | 509 | 77 | 5,0 % | +0,109 | +0,038 | +0,49 |
| USDJPY | 723 | 110 | 4,0 % | +0,092 | +0,034 | +0,60 |
| NAS100 | 671 | 102 | 1,6 % | +0,063 | +0,041 | +0,70 |
| SPX500 | 689 | 104 | 2,7 % | +0,228 | +0,187 | +2,41 |
| media ponderada | 3.108 | 471 | | +0,125 | +0,072 | 5/5 positivos |

Cinco de cinco es llamativo (p = 1/32 bajo moneda justa), pero **no rescata
nada**: los cinco z individuales son pequeños, SPX500 aporta la mitad del
efecto, los instrumentos están correlacionados dos a dos, y sobre todo esta
misma celda ya se probó a ciegas en oro y DAX con predicción escrita de
antemano — y **falló** (`RESULTADOS_h12_ciego.md`: bruta −0,003, neta −0,055).

## 3 · ¿Importa que su rejilla no sea la del estudio? No, en H4

Los estudios anclan las velas a la hora local de Nueva York (`ancla_ny = 1`).
Sus gráficos de TradingView (OANDA) van en **01/05/09/13/17/21 UTC fijo**. No
son la misma rejilla: en invierno se separan cinco horas y en verano cuatro.
Era una grieta razonable entre la investigación y lo que él ve en pantalla, y no
estaba comprobada.

Misma maquinaria canónica, mismos costes medidos (1,43 / 1,60 / 1,50):

| | | rejilla del estudio | | su rejilla UTC | |
|---|---|---|---|---|---|
| marco | instrumento | R bruta | R neta | R bruta | R neta |
| H4 | EURUSD | +0,146 | −0,018 | +0,130 | −0,027 |
| H4 | GBPUSD | +0,037 | −0,097 | +0,029 | −0,105 |
| H4 | USDJPY | +0,105 | −0,028 | +0,117 | −0,013 |
| H12 | EURUSD | +0,129 | +0,033 | +0,143 | +0,070 |
| H12 | GBPUSD | +0,109 | +0,033 | +0,153 | +0,091 |
| H12 | USDJPY | +0,092 | +0,025 | +0,141 | +0,074 |
| D1 | EURUSD | −0,001 | −0,052 | −0,010 | −0,060 |
| D1 | GBPUSD | +0,105 | +0,061 | +0,148 | +0,106 |
| D1 | USDJPY | +0,071 | +0,024 | +0,150 | +0,103 |

**En H4 las dos rejillas dicen lo mismo** —las diferencias son de una centésima
de R, muy dentro del ruido de un IC de ±0,06—. Eso es lo que hacía falta saber:
lo que él aprende marcando velas en su pantalla es lo mismo que se ha medido.

**En H12 y D1 su rejilla sale mejor en los seis casos.** No lo voy a usar. Es
una segunda rejilla probada después de ver la primera, ningún z llega a 1,7, y
adoptarla ahora porque sale mejor es exactamente el error que este proyecto
lleva dos meses evitando. Queda anotado como observación; si alguna vez se
prueba, se prueba pre-registrado y en instrumentos que no hayan participado.

## Consecuencia para el curso

H4 está bien para **aprender**: hay 348 operaciones al año por instrumento, se
ven muchos patrones en poco tiempo, y la rejilla es la suya. H4 no está bien
para **operar**: es el marco donde el peaje es del 7-11 % del riesgo y la neta
media es −0,030.

Las dos frases hay que decirlas juntas, y hasta ahora sólo se decía la primera.

Código: `bt/crt_por_temporalidad.py` (original), y los desgloses en
`bt/rejilla_y_marco.py`.
