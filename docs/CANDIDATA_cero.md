# Candidata congelada · Reversión de una hora en volatilidad alta

**Escrita ANTES de abrir el conjunto de confirmación. A partir de aquí no se
toca ni un parámetro.**

---

## De dónde sale

Cribado sistemático de 54 variables mecánicas sobre EURUSD M15, 2020-2023, según
`PREREGISTRO_cero.md`. Ninguna variable llevaba nombre de metodología.

**Resultado del cribado**, con nulo por permutación circular de 200 repeticiones:

| horizonte | variables que superan el percentil 99 del nulo |
|---|---|
| **4 velas (1 h)** | **15** |
| 12 velas (3 h) | 0 |
| 48 velas (12 h) | 0 |

Las 15 tienen correlación media de +0,21 entre ellas y máxima de +0,95: **no son
15 señales, son una sola** — si el precio acaba de subir o de bajar. Trece con
correlación negativa y dos positivas (`dmax_12`, `dmax_48`), que son justo las
dos que miden lo contrario —lo lejos que está el precio por *debajo* del
máximo—, así que las quince apuntan al mismo sitio: **reversión**.

## La regla, con números fijos

```
Señal compuesta = − media de los rangos percentiles móviles (2.688 velas)
                    de estas 15 variables:
   ret_1  ret_2  ret_4  ret_8  ret_12
   pos_12  pos_48  dmax_12  dmin_12  dmax_48  dmin_48
   cuerpo  cuerpo_m4  mecha_inf_m4  racha

Rango percentil      móvil de 2.688 velas, empates por el rango mínimo
Filtro de volatilidad    ATR(48) ≥ 9,4708 pips   (percentil 80 de 2020-2023)
Comprar  si  señal ≥ −0,199146   (los rangos están abajo: el precio acaba de caer)
Vender   si  señal ≤ −0,781742   (los rangos están arriba: el precio acaba de subir)
Horizonte                salir a las 4 velas M15 (1 hora), sin stop ni objetivo
```

Todo es causal: rangos móviles sobre ventana pasada, umbrales fijados solo con
2020-2023. Nada mira al futuro.

**Reproducibilidad.** `bt/cero.py` es esta especificación escrita como código y
`bt/reproduce_cero.py` la vuelve a correr sobre 2020-2023: 187 operaciones al
año, bruto +2,604, neta +1,404. Es el mismo número. El código y el documento
dicen lo mismo.

## Lo que dio en descubrimiento

```
188 operaciones al año
ventaja bruta  +2,61 pips por operación
coste           1,20 pips
NETA           +1,41 pips por operación
```

## Las tres reservas, dichas antes de mirar nada

**1. La celda se eligió después de ver la rejilla.** Probé cuatro umbrales de
volatilidad por cuatro de extremo, y toda la región positiva está en la esquina.
No hay interior cómodo: cualquier elección positiva es «la esquina».

| | 1 % | 2 % | 5 % | 10 % |
|---|---|---|---|---|
| ATR ≥ p80 | +1,94 | **+1,41** | +0,11 | −0,44 |
| ATR ≥ p60 | +0,78 | +0,23 | −0,36 | −0,68 |
| ATR ≥ p40 | +0,19 | +0,05 | −0,38 | −0,69 |
| todas | −0,05 | −0,31 | −0,68 | −0,79 |

Se congela **p80 + 2 %**, que no es el máximo, en vez del pico de +1,94 que solo
tiene 94 operaciones al año.

**2. A favor: el gradiente es monótono en las dos direcciones.** El ruido no
hace eso; el ruido se dispersa. Que crezca de forma ordenada al subir la
volatilidad y al ir a los extremos sugiere una relación real debajo. Y tiene
mecanismo: la reversión escala con la volatilidad, el spread no.

**3. Las celdas positivas son las de menos datos.** Eso es también la firma
clásica del sobreajuste. Las dos lecturas son compatibles y **solo la
confirmación las separa**.

## Criterio de confirmación, declarado ahora

Se abre una vez sobre:

- **EURUSD 2024-2026** — el mismo par, periodo nunca usado para este cribado
- **GBPUSD y USDJPY 2020-2026** — si el mecanismo es real, tiene que asomar

Se considera **confirmada** si:

1. El signo se mantiene en EURUSD 2024-2026
2. La ventaja neta es al menos **la mitad** de +1,41, o sea ≥ +0,70 pips
3. El signo se mantiene en al menos uno de los otros dos pares

Los umbrales de señal son rangos percentiles, adimensionales, y viajan tal cual
a los otros dos pares. El filtro de volatilidad no: «9,47 pips» no significa lo
mismo en GBPUSD que en USDJPY, donde el pip vale otra cosa. Lo que se congeló es
**el percentil 80**, así que en los otros pares se usa el percentil 80 de su
propio ATR en 2020-2023. Coste supuesto: 1,20 pips en EURUSD (el de
descubrimiento), 1,50 en GBPUSD, 1,30 en USDJPY.

Si falla el punto 1 o el 2, la candidata queda descartada y se dice así.
