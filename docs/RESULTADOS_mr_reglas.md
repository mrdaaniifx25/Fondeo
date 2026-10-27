# Resultado · cerrar las reglas de la reversión a la media

Código: `bt/mr_reglas.py`, `bt/mr_tope_dia.py`. Operativa: `docs/MEAN_REVERSION_REGLAS.md`.
EUR/USD M15, 2021-2026, salidas resueltas minuto a minuto, coste 0,7 pips.

---

## 1 · Corrección a lo que publiqué ayer

Dije: «el objetivo dinámico bate al congelado». **Con stop fijo es al revés.**

```
  stop 15 pips · objetivo EMA20 congelada  ->  bruto +0,673 pips
  stop 15 pips · objetivo EMA20 dinámica   ->  bruto +0,426 pips
```

La medición de ayer usaba el stop «detrás del extremo reciente» (7,5 pips de
mediana), y ahí sí ganaba el dinámico. Al cambiar el stop, el orden se da la
vuelta: la EMA se mueve **hacia** el precio, así que el objetivo dinámico saca
la posición antes y deja la mitad del recorrido.

**Era una combinación que nadie había medido y por eso la medí antes de
entregarla.** La regla operativa es: objetivo congelado.

## 2 · La rejilla del objetivo dinámico, completa

```
     k  stop     n  acierto  BRUTO      t    NETO   dentro    fuera
   1,5    10  1091    47,2%  0,452   1,25  -0,248   -0,316   -0,075
   1,5    12  1063    51,0%  0,420   1,06  -0,280   -0,336   -0,135
   1,5    15  1034    55,3%  0,426   0,98  -0,274   -0,120   -0,661
   1,5    18  1012    58,0%  0,268   0,57  -0,432   -0,351   -0,639
   2,0    15   527    55,2%  0,541   0,87  -0,159   -0,566    0,873
```

Ninguna celda positiva en los dos tramos. Mejor t: **1,25**, con un listón por
selección de 2,23.

## 3 · El hallazgo: la cola izquierda del día

El P&L diario tiene una cola izquierda gorda. **Peor día sin tope: −4,19 R.**

El mecanismo es el modo de fallo propio de la reversión a la media: en un día
de tendencia el RSI se queda clavado por debajo de 30, cada vela de rechazo
falla, y las pérdidas se encadenan. **Lo que elimina la cuenta no es una
operación: es un día.**

## 4 · La regla del día, medida

```
  regla del día              n   neto pips  PEOR DÍA  riesgo máx  LAS DOS  muere día
  sin tope                1030      -0,027     -4,19      0,50 %     0,0 %      0,0 %
  tope 1 al día            710      -0,654     -1,05      2,75 %    25,2 %      0,0 %
  tope 2 al día            952      -0,090     -2,09      1,25 %    38,0 %      0,0 %
  tope 3 al día           1010      -0,030     -3,14      0,75 %    40,2 %      0,0 %
  PARAR TRAS 2 PÉRDIDAS    972      -0,019     -2,26      1,25 %    41,2 %      0,0 %
  parar tras 1 pérdida     772      -0,202     -1,05      2,75 %    27,5 %      0,0 %
```

`riesgo máx` es el que hace que el **peor día observado** no toque el −3 %, y el
examen se simula con **ese** riesgo, no con uno elegido a conveniencia.

**«Parar tras 2 pérdidas seguidas» gana en las dos columnas a la vez**:
conserva 972 de 1.030 operaciones —así que el neto es el mejor de la tabla— y
recorta el peor día de −4,19 R a −2,26 R. Cortar más empeora el neto a −0,202
porque te quita 200 operaciones, casi todas buenas.

## 5 · Reconciliación con `RESULTADOS_lo_simple.md`

Ahí medí que «parar tras la primera pérdida» era **la peor** regla de cierre de
día, y aquí una regla de parada es **la mejor**. Las dos cosas son verdad:

- Allí el modelo era **iid**: las pérdidas no se apelotonaban, el límite diario
  mataba al 0,0 %, y recortar el día sólo alargaba la carrera y pagaba más
  coste.
- Aquí las pérdidas **sí se apelotonan**, porque los días de tendencia encadenan
  fallos de la reversión. Ahí la regla corta exactamente la cola que mata.

**Una regla de parada vale cuando las pérdidas se agrupan, y no vale cuando son
independientes.** Es el tipo de cosa que sólo se ve con los caminos reales.

## 6 · El tamaño

```
   riesgo   peor día   fase 1   LAS DOS  días med  muere día
    0,75%     -1,70%    60,4%     23,5%        75      0,0%
    1,00%     -2,26%    54,9%     38,1%        59      0,0%   <- recomendado
    1,25%     -2,83%    55,9%     41,2%        41      0,0%
    1,50%     -3,39%    13,2%      5,2%        10     94,8%
```

A 1,25 % el peor día deja 17 céntimos de margen sobre el límite. A 1,50 % el
acantilado es total: **94,8 % de muerte por límite diario**. Se recomienda
**1,00 %**, que deja colchón para un día peor que ninguno de los 1.426 medidos.

Apalancamiento resultante **7,8x**, dentro de su tope de 10x.

## 7 · Veredicto

**Esperanza cero**, como todo lo demás: neto −0,090 pips por operación con coste
0,7, frente a una ventaja bruta de medio pip.

**Y aun así es la mejor configuración del proyecto para su examen: 38,1 % de
pasar las dos fases, con 0,0 % de muerte por límite diario.** Esos puntos no
vienen de ninguna ventaja. Vienen de la regla de las 2 pérdidas y del tamaño.

Que es, literalmente, lo que decía el vídeo de gestión de riesgo que me pasó.
