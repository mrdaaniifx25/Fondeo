# Resultado · casilla 4, el swap. Y la retractación del mejor hilo que quedaba

Código: `bt/swap.py`. 20 divisas, 623 meses, 1971-2026.
El usuario pidió mirar la casilla 4. Al revisar el código para hacerlo encontré
**un error mío en `bt/carry.py` y `bt/sistema.py`** que invalida la afirmación
central que llevo semanas repitiéndole.

---

## 0 · El error

El recargo del bróker se restaba al diferencial de tipos y **después** se
multiplicaba por la señal:

```python
  rend = ((C - recargo)/1200 - R)
  p    = sig * rend
```

Para una posición **larga** (`sig = +1`) eso resta el recargo. Correcto.
Para una **corta** (`sig = -1`) lo **suma**: el recargo entra como un **ingreso**.

La cartera de carry es mitad larga y mitad corta. **La mitad de las posiciones
recibía un abono donde tenía que pagar una comisión.**

Lo correcto es que el recargo cueste siempre:

```python
  p = (sig*(interes - R) - abs(sig)*recargo/1200) / VOL
```

### Cuánto valía el error

```
                                         meses    efecto       t  Sharpe
  recargo 1,5 pp/año · modelo ANTIGUO      623   +0,0324   +2,95   +0,41
  recargo 1,5 pp/año · modelo CORRECTO     623   ≈ 0       ≈ 0     ≈ 0
  recargo 3,0 pp/año · modelo ANTIGUO      623   +0,0296   +2,69   +0,37
  recargo 3,0 pp/año · modelo CORRECTO     623   -0,0365   -3,32   -0,46
```

A 3 puntos de recargo el error vale **0,066 de efecto**, que es el doble del
efecto total de la estrategia.

## 1 · Cuánto recargo aguanta de verdad

```
    recargo   20 divisas t   Sharpe      G10 t   Sharpe
        0 pp           3,21     0,45       2,64     0,37
        1 pp           1,03     0,14       0,92     0,13
        2 pp          -1,15    -0,16      -0,80    -0,11
        3 pp          -3,32    -0,46      -2,53    -0,35
        5 pp          -7,63    -1,06      -5,98    -0,83
```

**El punto de equilibrio está entre 0,5 y 1 punto porcentual al año.**

Publiqué que *«aguanta un recargo de 1,5 puntos, que se lleva sólo el 8 %»*.
**Falso.** A 1,5 puntos ya está en cero.

Y el dato que importa: **los recargos reales de un bróker minorista sobre el
swap van de 1 a 3 puntos al año** en los pares mayores, y más en los exóticos.
Es decir, el recargo real está **por encima** del punto de equilibrio.

## 2 · Por qué el recargo lo decide todo: la estrategia ES el swap

```
                                           meses    efecto       t  Sharpe
  completo (interés + movimiento)            623   +0,0352   +3,21   +0,45
  SOLO el interés (el swap)                  623   +0,0851  +64,43   +8,94
  SOLO el movimiento (sin swap)              623   -0,0502   -4,55   -0,63
```

Esto es la anatomía entera del carry y conviene leerla despacio:

- **Lo que se cobra de interés: +0,0851**, con t +64. Casi determinista: se
  recibe el diferencial, sin más.
- **Lo que se pierde en el movimiento del cambio: −0,0502**, t −4,55. La divisa
  de tipo alto **sí** se deprecia contra ti, y se come el **59 %** de lo
  cobrado.
- **Lo que queda: +0,0352.**

**El 100 % del rendimiento del carry es el interés cobrado.** El movimiento del
precio es puro coste. Tres consecuencias:

1. **Cualquier recargo sale directamente del único ingreso que hay.** No hay
   colchón.
2. **Una cuenta sin swap da t −4,55.** Garantizado perdedor. Y muchas cuentas de
   fondeo son sin swap, o cobran financiación diaria. En ésas esto es imposible
   por construcción.
3. No es una anomalía de precio: es **cobrar un tipo de interés asumiendo el
   riesgo de divisa**. Es un negocio real, y el bróker minorista se queda el
   margen.

## 3 · Mi esperanza de que los tipos reales mejorasen la señal: tampoco

Dije que mi versión era «coja» por usar inflación del Banco Mundial con dos años
de retraso, y que con tipos reales en vivo saldría mejor. Medido, con 2 pp de
recargo:

```
                                           meses    efecto       t
  inflación de Y-2 (lo que uso)              623   -0,0126   -1,15
  inflación de Y-1                           611   -0,0121   -1,08
  inflación de Y (mira al futuro)            599   -0,0235   -1,97
```

**Una señal más fresca no mejora nada; empeora.** Así que el retraso no era el
problema, y la tabla de swap del bróker no iba a arreglarlo. **No hace falta que
me la mande.**

## 4 · El tramo reciente, con el recargo correcto

```
                                           meses    efecto       t  Sharpe
  1971-1999                                  311   -0,0356   -1,94   -0,38
  2000-2012                                  156   +0,0325   +1,76   +0,49
  2013-2026                                  156   -0,0118   -0,77   -0,21
  G10 2013-2026                              156   -0,0107   -0,67   -0,19
```

Publiqué que el carry en 2013-2026 daba **t +2,46** y que era *«lo primero en
todo el proyecto que es significativo en el periodo reciente»*. Con el recargo
bien modelado da **t −0,77**.

**Esa frase era el hilo que le decía que quedaba sin cortar. No queda.**

## 5 · El sistema ensamblado, recalculado

El mismo error estaba en `bt/sistema.py`. Con el recargo correcto:

```
                                   meses       t  Sharpe  peor caída   €/mes 50k
  momento (los CUATRO juntos)        632   +5,51   +0,76       -4,54       +114
  carry                              632   +0,04   +0,01      -10,45         +0
  MEZCLA 50/50                       632   +5,53   +0,76       -2,13       +121
    mezcla 2013-2026                 165   +0,57   +0,15       -2,13        +23
```

Antes: mezcla **t +7,29, Sharpe 1,00**. Ahora: **t +5,53, Sharpe 0,76** — que es
**exactamente lo que da el momento solo** (t +5,51, Sharpe 0,76).

**El carry no aporta rendimiento al sistema.** Lo único que aporta sigue siendo
real y vale algo: con correlación −0,287 contra el momento, **baja la peor caída
de −4,54 a −2,13 y arregla la asimetría** (+0,54 a +0,02). Es un diversificador
de rendimiento esperado cero. Eso sirve para dormir, no para cobrar.

## 6 · En dinero

```
  completa, recargo 2 pp         rend -0,12 %/año    10k:  -1 €/mes
  2013-2026, recargo 2 pp        rend -0,37 %/año    10k:  -3 €/mes
  G10 2013-2026, recargo 2 pp    rend -0,41 %/año    10k:  -3 €/mes
```

## Lo que queda en pie y lo que no

**En pie:** el carry sin recargo da t +3,21, y eso es un hecho sobre el mercado
—el premio del forward existe—. Y su valor como diversificador del momento.

**Retractado:** que aguante el recargo de un bróker. Que fuera significativo en
el tramo reciente. Que fuera el hilo que quedaba. Y que el sistema ensamblado dé
Sharpe 1,00: da 0,76, el del momento solo.

**Casilla 4 cerrada, y cerrada por un error mío**, no por los datos. El error
llevaba tres semanas en el repositorio y lo he encontrado al ir a mirar lo que
él me pidió mirar.
