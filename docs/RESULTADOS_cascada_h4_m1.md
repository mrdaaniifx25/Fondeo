# Resultados · H4 marca, CRT en M15, confirma M5, ejecuta M1

Pre-registro: `docs/PREREGISTRO_cascada_h4_m1.md`. Un solo pase.
Tres instrumentos, 2020-2026. **19.621 señales de CRT en M15** en EURUSD, de las
cuales **8.590 caen sobre un nivel de Asia**.

## EURUSD

| | n | stop | coste | acierto | vs geometría | z ac. | R bruta | **R neta** | z neta |
|---|---|---|---|---|---|---|---|---|---|
| **PRINCIPAL** H4+Asia+M1+1:2 | 1.953 | 2,4 p | 60 % | 34,3 % | +1,0 pp | +0,90 | +0,029 | **−0,611** | −18,68 |
| sin filtro de Asia | 3.964 | 2,5 p | 57 % | 33,5 % | +0,2 pp | +0,21 | +0,005 | −0,622 | −27,17 |
| **sin filtro de H4** | 3.540 | 2,4 p | 60 % | **35,0 %** | **+1,6 pp** | **+2,06** | +0,049 | −0,594 | −24,24 |
| sin ninguno de los dos | 8.045 | 2,5 p | 57 % | 34,2 % | +0,9 pp | +1,62 | +0,025 | −0,599 | −37,11 |
| stop en el barrido | 1.508 | 12,9 p | 11 % | 32,8 % | −0,5 pp | −0,36 | −0,011 | **−0,186** | −5,95 |
| objetivo al extremo del rango | 1.069 | 2,3 p | 62 % | 28,3 % | −5,0 pp | −3,49 | −0,007 | −0,668 | −9,79 |
| solo Londres 08:00-11:30 | 964 | 2,3 p | 62 % | 34,8 % | +1,4 pp | +0,93 | +0,043 | −0,629 | −13,33 |

GBPUSD y USDJPY, misma forma. La principal: **−0,581** (z −16,5) y **−0,622**
(z −18,3).

## Los dos filtros no se portan igual

**El de Asia suma.** Sin él, 33,5 % — la geometría clavada. Con él, **35,0 %, con
z +2,06**. Exigir que el barrido ocurra pegado a un nivel de Asia añade punto y
medio de acierto, y tiene mecanismo: no todos los barridos valen lo mismo, solo
los que ocurren donde hay liquidez que barrer.

**El de H4 resta.** Con Asia sola, 35,0 %. Añadiendo H4, **34,3 %**. Filtrar por
la dirección de las últimas dieciséis horas quita ventaja en vez de darla. Es la
segunda vez que se mide, en otra muestra, y coincide con la primera —30,8 % a
favor contra 30,8 % en contra—: **H4 no sabe nada de lo que hará el precio en la
próxima hora.**

## La celda post hoc, y por qué falla

Las dos piezas que funcionaban por separado eran el filtro de Asia (sube acierto)
y el stop ancho (baja coste). Nunca se habían corrido juntas. **No estaba
preregistrado**, así que se corre marcado y no cuenta como hallazgo.

| | n | stop | coste | acierto | vs geometría | R neta |
|---|---|---|---|---|---|---|
| EURUSD | 2.802 | 13,2 p | 11 % | 32,0 % | **−1,3 pp** | −0,202 |
| GBPUSD | 2.315 | 18,0 p | 8 % | 29,5 % | −3,8 pp | −0,223 |
| USDJPY | 2.608 | 12,2 p | 12 % | 32,0 % | −1,3 pp | −0,214 |

**La ventaja de Asia no sobrevive a ensanchar el stop.** Con stop de M1 daba
+1,6 pp sobre la geometría; con stop en el barrido da **−1,3 pp**. Desaparece.

Y eso dice **qué es** esa ventaja. Con stop de 2,4 pips el objetivo está a 4,8;
con stop de 13,2 está a 26,4. El efecto vive en los primeros pips: **tras barrer
un nivel de Asia, el precio da un rebote corto y fiable antes de decidir.** Ese
rebote paga un objetivo de cinco pips y no paga uno de veintiséis.

## La cuenta que resume todo el proyecto

La ventaja bruta en R engaña, porque la R depende del stop. En pips:

```
ventaja en pips = R bruta × stop en pips

  EURUSD · Asia, stop de M1      +0,049 R × 2,4 p  =  +0,118 pips
  EURUSD · Asia + H4             +0,029 R × 2,4 p  =  +0,070 pips
  EURUSD · sin filtros           +0,025 R × 2,5 p  =  +0,062 pips
  coste redondo                                       1,430 pips
```

**La mejor combinación de todo este pase rinde 0,118 pips de ventaja contra 1,43
de coste. Haría falta que la ventaja fuese doce veces mayor de lo que es.**

Y el efecto está atrapado: solo existe a stops cortos, y a stops cortos el coste
se lleva el 60 % del riesgo. Ensanchar el stop mata el efecto; estrecharlo
multiplica el coste. No hay ventana.

## La predicción firmada

| | |
|---|---|
| 1 · Asia recorta la muestra y sube el acierto, no lo bastante | **acierto** |
| 2 · H4 no cambiará el acierto | **acierto**, y de hecho lo baja |
| 3 · la principal entre −0,3 y −0,9 R | **acierto** — −0,611 |
| 4 · ninguna celda con z > +1,96 en R neta | **acierto** — la mejor es −5,95 |

Cuatro de cuatro. Es la primera vez en el proyecto, y no es buena noticia: quiere
decir que la aritmética ya predice sin necesidad de correr nada.

## Reproducir

`python3 bt/cascada_h4_m1.py` · salida en `data/cascada_h4_m1_salida.txt`
