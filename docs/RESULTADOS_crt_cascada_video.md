# Resultado · la cascada CRT del curso en vídeo

Pre-registro: `docs/PREREGISTRO_crt_cascada_video.md`. Un solo pase.
Código: `bt/crt_video.py` (principal) y `bt/crt_video_variantes.py` (exploratorio).
EURUSD 2021-2026, oro y DAX 2023-2026. **8.175 señales** con las cuatro
temporalidades alineadas; 2.606 tomando una por día.

## El contraste principal

```
                                     n    R:R  acierto    geom   coste    BRUTA      z     NETA      z
  una operación por día           2606  16,48    14,9%   15,6%   66,8%  -0,0450  -0,66  -0,7131  -6,54
  todas las señales               8175  16,55    12,9%   13,2%   55,4%  -0,0072  -0,17  -0,5608  -9,81
```

**Bruta cero. Neta −0,71 R por operación.**

## Lo que mata la regla no es la dirección, es la geometría

Mire la columna del coste: **66,8 % del riesgo**. Eso no es un detalle, es la
respuesta entera.

El vídeo manda poner el stop *«por debajo de los mínimos anteriores»* — detrás
de la mecha del barrido, que son dos o tres pips — y el objetivo en el extremo
opuesto del rango H4, que está lejísimos. Resultado: **R:R de 16,5 a 1**. Suena
maravilloso y es justo lo que arruina la operación, porque con un riesgo de tres
pips la horquilla se lleva dos tercios de lo arriesgado **antes de que el precio
se mueva**.

La ecuación de siempre:

    neta = ventaja × (1 + R:R) − coste/riesgo

El R:R de 16,5 multiplicaría una ventaja. La ventaja es cero, así que multiplica
cero. Y el 0,668 de coste se resta entero.

En el DAX el coste es el **115,9 %** del riesgo: la horquilla es más ancha que
la distancia al stop. Esa operación pierde en el instante de abrirse.

## La cascada no es monótona — y la alineación completa es la PEOR celda

Ésta era la afirmación central del vídeo: la fractalidad, las cuatro
temporalidades alineadas. Si informara, más alineación tendría que ser mejor.

```
  alineadas      n    R:R  acierto    geom    BRUTA      z
          0   3512   5,42    32,7%   33,2%  +0,0179  +0,41
          1   3505   8,76    24,3%   25,9%  -0,0133  -0,13
          2   3546  12,08    20,3%   18,8%  +0,1094  +1,86
          3   2606  16,48    14,9%   15,6%  -0,0450  -0,66
```

0 → 1 → 2 → 3 sale +0,02 / −0,01 / +0,11 / −0,05. **No crece.** Y el cubo que
la teoría señala como el bueno —las tres alineadas, el paso 5 del vídeo— es el
único negativo junto con el de 1. Exigir que coincidan día, H4 y H1 no aporta
nada; lo único que hace de verdad es estrechar el stop y subir el coste.

## El placebo vuelve a ganar

Mismas entradas, mismos instantes, misma geometría, **lado invertido**:

```
  real      -0,0450   (z -0,66)
  placebo   +0,0676   (z +1,05)
```

Operar al revés de lo que dice CRT sale mejor que operar a favor. No
significativamente —los dos son ruido— pero es la cuarta vez en este proyecto
que el placebo de dirección iguala o supera a la señal real
(`RESULTADOS_rr_extremo.md`, `RESULTADOS_liquidez_sesiones_v2.md`,
`RESULTADOS_rsi_h1.md`). Cuando eso pasa cuatro veces, ya no es mala suerte:
es que **el lado no lleva información**.

## Las tres dianas del vídeo, y las nueve celdas (exploratorio, post hoc)

El vídeo menciona tres objetivos y yo añado tres anchos de stop:

```
  objetivo  stop     n    R:R  acierto    geom   coste    BRUTA      z     NETA      z
  H4         1x   2605  16,49    14,9%   15,6%   66,8%  -0,0446  -0,66  -0,7130  -6,54
  H4         2x   2605   8,24    23,6%   25,6%   33,4%  -0,0806  -1,81  -0,4148  -6,69
  H4         4x   2605   4,12    36,4%   38,7%   16,7%  -0,0496  -1,60  -0,2167  -5,70
  50 % D     1x   2577  23,34    13,3%   13,3%   67,0%  +0,0376  +0,32  -0,6322  -4,38
  50 % D     2x   2577  11,67    20,8%   22,1%   33,5%  -0,0256  -0,37  -0,3605  -4,42
  50 % D     4x   2577   5,83    31,5%   33,8%   16,7%  -0,0435  -1,01  -0,2109  -4,39
  rango D    1x   2606  39,57     6,8%    7,7%   66,8%  -0,2005  -2,58  -0,8687  -7,41
  rango D    2x   2606  19,79    10,8%   13,7%   33,4%  -0,2428  -4,57  -0,5769  -8,34
  rango D    4x   2606   9,89    17,5%   22,9%   16,7%  -0,2121  -5,48  -0,3791  -8,45
```

**Las nueve son negativas en bruto y en neto.** Ensanchar el stop baja el coste
del 67 % al 17 %, exactamente como manda la aritmética, y aun así no alcanza:
la mejor de las nueve sigue en −0,21 neta.

Y hay algo peor en la última familia. Ir a por el extremo completo del rango
diario —lo que el vídeo describe como *«un 25 de rentabilidad riesgo»*, el trade
que queda espectacular en pantalla— **no es neutro, es significativamente malo**:
acierta el 17,5 % donde la pura geometría da 22,9 %, con z −5,48. El precio se
queda corto del extremo diario mucho más a menudo de lo que la barrera predice.

Es el mismo patrón exacto que `RESULTADOS_crt_cascada.md` encontró con el
objetivo semanal: tocado el 1,92 % de las veces contra un 3,19 % geométrico.
**Los objetivos lejanos de CRT se alcanzan MENOS que por azar.** Eso es el
retroceso medio de un movimiento, visto desde el lado equivocado.

## Mi predicción firmada, y dónde falló

| firmé | salió |
|---|---|
| bruta entre −0,05 y +0,05 | −0,045 ✔ |
| cascada no monótona | no monótona ✔ |
| placebo empata | placebo **gana** ✔ |
| **neta entre −0,10 y −0,40, z < −3** | **−0,71, z −6,54** ✘ |

**Me quedé corto en la neta, y por mucho.** Subestimé el coste: di por hecho un
stop de unos diez pips y salen tres. Es el mismo error que cometí en
`RESULTADOS_rsi_h1.md` —estimar el ancho del stop en vez de medirlo— y van dos.
Anotado: en la próxima estrategia con «stop detrás de la mecha», el ancho se
mide antes de escribir nada.

## Lo que el propio vídeo dice, y conviene no pasar por alto

Tres frases del autor, textuales:

> *«no soy experto en CRT. Yo tengo mis estrategias de trading con las que ya soy
> rentable. Tengo mi track récord auditado **con esas mismas estrategias**»*

Su historial auditado **no es de CRT**. Lo dice él.

> *«una de las personas de máxima confianza que yo tengo en el mundo del trading
> opera de forma diaria y de forma rentable»*

La rentabilidad se delega en un tercero sin nombre y sin auditar.

> *«todos los mejores traders, los que ganan la Robbins Cup Trading
> Championship, **no utilizan ninguno de ellos métodos como este**. Utilizan
> métodos más algorítmicos, más con indicadores... medias móviles, RSIs, MACDs,
> ATRs»*

El autor del curso dice que los que ganan de verdad no usan esto. Y cierra con
*«esto no es el Santo Grial de absolutamente nada»*.

**El vídeo es honesto.** No vende CRT como rentable: lo presenta como una
metodología, avisa de que no basta, y señala él mismo dónde está su propio
historial. Lo que este documento añade es el número que falta: medida tal cual
viene, la cascada da cero en bruto y pierde 0,71 R por operación en neto.

## Dónde encaja esto en el resto del proyecto

Es el vigésimo documento de CRT de este repositorio y coincide con todos:

- `RESULTADOS_crt_canonico.md` — CRT canónico, entrada en Vela 3: +0,0248 bruto,
  p 0,717, PF neto 0,884.
- `RESULTADOS_crt_cascada.md` — la cascada hacia el objetivo semanal: cubo de 3
  alineadas +0,029 (z +0,20), no monótono.
- `RESULTADOS_cascada_h4_m1.md` — el filtro de H4 **resta**: 35,0 % de acierto
  sin él, 34,3 % con él.
- `RESULTADOS_crt_final.md` — el sistema ensamblado: **24 celdas de 24 negativas
  fuera de muestra.**

Y coincide con las otras ocho familias de ideas intradía: el mercado cobra la
geometría del gráfico exactamente a su precio.
