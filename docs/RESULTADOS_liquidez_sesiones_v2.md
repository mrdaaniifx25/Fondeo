# Resultados · ESTRATEGIA EUR/USD — LIQUIDEZ DE SESIONES

Especificación suya, íntegra en `docs/SPEC_liquidez_sesiones_v2.md`.
Decisiones de implementación en `docs/PREREGISTRO_liquidez_sesiones_v2.md`,
subidas **antes** de medir. Código: `bt/liquidez_v2.py`.
EURUSD M1, 2021-2026, 2.055.684 minutos, 5,7 años.

## Veredicto

La celda principal **no tiene potencia** (40 operaciones). La que sí la tiene
sale **claramente negativa**. Y el dato que decide no es ése: es que **la cadena
de filtros H4+H1 empeora el resultado** frente a no ponerla.

## La celda principal declarada

```
  margen 1p · espera 12 · H1 estricto
  n 40   riesgo 9,5 p   coste 15,7 %   acierto 27,5 %   umbral 38,6 %
  NETA -0,1834 [-0,6117, +0,2448]
```

Cuarenta operaciones en 5,7 años. El intervalo va de −0,61 a +0,24: **con esta
muestra no se puede afirmar nada**, que es lo que predije. Su §5 —que el sweep de
H1 cierre dentro de la ventana de 09-11 o 14-16:30— deja sólo dos velas H1 por
ventana, y casi nunca coinciden con las demás condiciones.

## La celda con potencia · H1 laxo (la H1 cierra dentro de la sesión)

```
  n 167   riesgo 8,9 p   coste 16,7 %
  acierto 22,2 %    azar de un 1:2 = 33,3 %    umbral con coste = 38,9 %
  NETA -0,3769 [-0,5705, -0,1832]
```

El intervalo **entero por debajo de cero**. Y el acierto no sólo está por debajo
del umbral: está **once puntos por debajo del azar**.

**Comprobado antes de leerlo**: sólo el **9,0 %** queda sin resolver al cierre
del día. El sesgo de truncamiento que ya me hizo retractarme una vez
(`docs/RESULTADOS_stop.md`) no explica esto. El 22,2 % es real.

## Lo que de verdad dice la prueba · los placebos

```
                              n      acierto     NETA
  lados barajados           167       29,3 %   -0,1433
  SIN la cadena H4+H1       794       27,1 %   -0,1942
  la señal completa         167       22,2 %   -0,3769
```

**La señal completa es peor que los dos placebos.** Barajar la dirección al azar
acierta un 29,3 %; quitar los filtros de H4 y H1 acierta un 27,1 %; aplicarlos
todos acierta un 22,2 %.

No es que la cadena no aporte. **Resta.**

### Por qué, y encaja con lo ya medido

Exigir que H4 **y** H1 **y** M5 hayan barrido *el mismo nivel* significa que ese
nivel lleva tres ataques encima antes de que usted entre. Está entrando en el
cuarto ataque a un nivel ya agotado.

`docs/RESULTADOS_barrido_sesion_v2.md` ya había medido exactamente eso: *«las
repeticiones sobre un nivel ya barrido son peores que la primera»*. Su cadena de
confirmaciones es, sin querer, un filtro que selecciona niveles gastados.

## Su §15 y §16, completos · celda con potencia

```
  operaciones 167   TP 37 (22,2 %)   SL 115 (68,9 %)   sin resolver 15 (9,0 %)
  R bruta total -35,1    R neta total -62,9
  esperanza/op   bruta -0,2103   neta -0,3769
  profit factor (neto) 0,544
  máximo drawdown -64,88 R
  racha máxima de ganancias 3   ·   de pérdidas 14
  MAE medio 3,46 R   MFE medio 3,05 R   duración mediana 61 min

  por SESIÓN        Londres    n 100   TP 24,0 %   neta -0,393
                    Nueva York n  67   TP 19,4 %   neta -0,352
  por DIRECCIÓN     LONG       n  82   TP 15,9 %   neta -0,531
                    SHORT      n  85   TP 28,2 %   neta -0,228
  por NIVEL         PDH        n  35   TP 22,9 %   neta -0,332
                    PDL        n  43   TP 11,6 %   neta -0,697
                    PSH        n  50   TP 32,0 %   neta -0,156   <- el único con bruta positiva
                    PSL        n  39   TP 20,5 %   neta -0,347
  por AÑO           2021 -9,4R · 2022 +4,2R · 2023 -18,9R · 2024 -14,1R
                    2025 -14,0R · 2026 -10,8R
```

Cinco años de seis en negativo. La racha máxima de pérdidas es de **14
seguidas**: con su límite del 10 % y riesgo del 0,25 %, eso son 3,5 puntos de
caída sólo por esa racha, y con un 1 % de riesgo son 14 — cuenta reventada.

Partido en dos mitades: **1ª −0,284, 2ª −0,469.** Las dos negativas.

## Lectura alternativa de su §5

Su texto dice «H1 debe barrer un máximo **relevante**». Lo implementé como *el
mismo nivel*. La otra lectura —cualquier pivote reciente de H1— es igual de
legítima, así que la probé también:

```
  pivote H1 · margen 1p   n 256   acierto 26,6 %   umbral 38,5 %   NETA -0,1846 [-0,3473,-0,0219]
  pivote H1 · margen 3p   n 257   acierto 25,7 %   umbral 37,4 %   NETA -0,1144 [-0,2736,+0,0448]
```

Mejor que mi lectura, y **sigue por debajo del azar y por debajo de cero**.

## Contra el criterio pre-registrado

| criterio | resultado |
|---|---|
| 1. acierto > umbral y neta con IC limpio | **NO.** 22,2 % contra 38,9 % |
| 2. neta por encima de +0,038 | **NO.** −0,377 |
| 3. mismo signo en dos mitades | sí, y **las dos negativas** |
| 4. los placebos no rinden igual | **al revés: rinden MEJOR** |

## Lo único que sobrevive, y se declara como exploratorio

**PSH** (máximo de la sesión anterior, en cortos) es el único de los cuatro
niveles con **bruta positiva**: +0,030 sobre 50 operaciones, acierto 32,0 %.
Sigue sin cubrir el coste y son 50 operaciones. **No es un hallazgo**: es la
mejor de cuatro casillas y con esa n el intervalo la cruza de sobra. Se apunta
sólo porque es la única dirección que no está muerta.

## Récord de predicciones

Tres de seis.

| predicción | resultado |
|---|---|
| entre 80 y 250 operaciones | 40 en el principal ✘ (167 en el laxo) |
| riesgo mediano entre 8 y 14 pips | 9,5 p ✔ |
| acierto entre 30 % y 38 % | 22,2 % ✘, muy por debajo |
| la neta será negativa o indistinguible de cero | negativa ✔ |
| el placebo sin H4+H1 rendirá parecido | rinde **mejor** ✘ |
| lo más probable es «no se puede saber» | cierto para el principal ✔ |

## Y el §17, que es suyo

Su artículo 17 dice que cualquier modificación posterior debe probarse sobre un
periodo distinto o fuera de muestra. Se respeta: nada de lo de arriba se ha
tocado tras ver los resultados, y lo único positivo (PSH) queda marcado como
candidato a comprobar en otros datos, no como conclusión.
