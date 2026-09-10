# Resultados · GPSO «Trading en 5 Pasos», la versión completa con fibonacci

Especificación completa que él transcribió del material público: niveles en H1,
reacción, fibonacci sobre la vela ya cerrada, retroceso al 38,2/50/60 %, filtro de
invalidez al 75 %, confirmación por envolvente o martillo en M5, y la gestión
(BE a 1R, 80 % a 2R, resto corriendo).

**Ni un parámetro ajustado por mí.** Un solo pase, siete instrumentos.

## El embudo (EURUSD)

```
  11.476  reacciones en un nivel
   8.179  llegan a la zona de fibonacci
   4.589  se invalidan por pasar del 75 %
   5.531  entran con confirmación
```

## El resultado

| instrumento | entradas | A · 2R seco | B · BE a 1R | C · parciales |
|---|---|---|---|---|
| EURUSD | 5.531 | 32,2 % · **−0,705** | 24,4 % · −0,707 | 24,4 % · −0,753 |
| GBPUSD | 5.781 | 31,9 % · −0,612 | 24,6 % · −0,590 | 24,6 % · −0,637 |
| USDJPY | 5.515 | 34,5 % · −0,528 | 26,2 % · −0,533 | 26,2 % · −0,581 |
| XAUUSD | 2.147 | 33,3 % · −0,209 | 25,5 % · −0,188 | 25,5 % · −0,237 |
| GRXEUR | 2.214 | 36,0 % · −0,238 | 28,5 % · −0,239 | 28,5 % · −0,285 |
| NSXUSD | 5.207 | 34,0 % · −0,179 | 25,8 % · −0,193 | 25,8 % · −0,241 |
| SPXUSD | 5.399 | 33,7 % · −0,300 | 25,9 % · −0,295 | 25,9 % · −0,338 |

```
  A  2R seco       R bruta +0,009   ·   R NETA -0,396   ·   neta positiva 0/7
  B  BE a 1R       R bruta +0,013   ·   R NETA -0,392   ·   neta positiva 0/7
  C  parciales     R bruta -0,034   ·   R NETA -0,439   ·   neta positiva 0/7
```

## El asesino: el stop mide 2,8 pips

La confirmación en M5 —envolvente o martillo— da un stop diminuto:

```
  stop en EURUSD:  p10 1,1 p   ·   mediana 2,8 p   ·   p90 6,7 p
  coste / riesgo:  51 %
```

**Con el coste valiendo la mitad del riesgo haría falta acertar el 50,3 % para
quedar en tablas**, contra el 33,3 % que da la geometría. Ninguna ventaja
concebible cubre eso. El acierto medido es 33,2 %.

## La gestión no añade nada, y esto conviene entenderlo

Mover el stop a break-even en 1R **no crea ventaja**. Cambia la forma del pago,
no la esperanza:

```
  2R seco:   -1·P(pierde) + 2·P(gana)
  BE a 1R:   -1·P(pierde antes de 1R) + 0·P(vuelve a BE) + 2·P(llega a 2R)
```

En un paseo aleatorio con 1:2 las dos valen exactamente cero. Y medido: bruta
+0,009 con 2R seco contra +0,013 con BE. Idénticas.

*(En la primera versión de esta prueba yo tenía un fallo: al mover el stop a BE
seguía comprobando el stop original, así que dejaba correr operaciones que en
realidad habrían saltado en BE. Eso daba una bruta de +0,169 y era falsa. Con el
arreglo, +0,013.)*

Los parciales del 80 % a 2R **empeoran**: −0,034. Cortan la cola derecha, que es
donde vive lo poco que hay.

## Las dos piezas nuevas tampoco aportan

| | R bruta con 2R seco |
|---|---|
| completa | **+0,009** |
| sin la confirmación de envolvente/martillo | +0,015 |
| sin el filtro de invalidez del 75 % | −0,005 |

Quitar la confirmación **mejora** ligeramente. El filtro del 75 % aporta algo
minúsculo. Ninguna de las dos es el motor de nada.

## Comparación con lo único que sí pasó un preregistro

| | stop | coste/R | R bruta | R neta |
|---|---|---|---|---|
| GPSO completa (confirmación en M5) | 2,8 p | 51 % | +0,009 | −0,396 |
| GPSO simple (cierre de H1) | 12,0 p | 12 % | +0,011 | −0,179 |
| **Fibo H1 con stop al extremo barrido** | **6,8 p** | **21 %** | **+0,043** | −0,201 |

La versión que pasó el preregistro sigue siendo la única con ventaja bruta
medible. Añadirle la confirmación de M5 no la mejora: **le estrecha el stop y
multiplica por dos el peso del coste.**

## Reproducir

`python3 bt/gpso_completa.py` · ablaciones con `CONF=no`, `INVAL=9.9`
