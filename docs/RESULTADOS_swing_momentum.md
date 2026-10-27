# Resultado · swing momentum EUR/USD, según el encargo

Código: `bt/swing_momentum_eurusd.py` y `bt/swing_momentum_iter.py`.
**No llegó ningún CSV adjunto**: se usa EUR/USD M1 de HistData del repositorio,
agregado a diario con cierre a las 17:00 de Nueva York, y **las salidas se
resuelven minuto a minuto** con el M1 para que no haya ambigüedad intrabarra.
2021-2026, 1.439 días.

---

# VEREDICTO: **NO VALIDADA**

---

## 1 · Las reglas, congeladas antes de correr

```
  tendencia  EMA(50) diaria > EMA(200) -> sólo compras ; < -> sólo ventas
  gatillo    el cierre diario rompe el máximo (mínimo) de los 20 días previos
  entrada    APERTURA del día siguiente
  stop       entrada ∓ 2,0 x ATR(14) diaria
  objetivo   entrada ± 4,0 x ATR(14)        -> R:R 1:2 exacto
  tope       20 días hábiles, cierre a mercado
  riesgo     0,5 % ; tamaño = riesgo / distancia al stop
  coste      0,04 % por lado
```

Apalancamiento resultante: **0,35×** (stop mediano 1,445 % del precio). Muy por
debajo de su tope de 1:10. ✔

## 2 · El backtest

```
                                n  win rate    exp R      PF     maxDD   retorno ops/año
  DENTRO (ajuste, 70 %)        20     45,0%   -0,065    0,88     -3,2%     -0,7%     6,4
  FUERA (validación, 30 %)      9     44,4%   +0,138    1,37     -0,9%     +0,6%     7,4
  muestra completa             29     44,8%   -0,002    1,00     -3,2%     -0,1%     6,3
```

**Fuera de muestra cumple sus dos criterios** —win rate 44,4 % > 39,33 % y
expectativa +0,138— **y aun así no valido la estrategia. Son nueve
operaciones.**

Con n = 9 y una desviación de 1,3 R, el error estándar es **0,43 R**. Esa
expectativa de +0,138 tiene un intervalo que va de −0,70 a +0,98. No distingue
nada.

## 3 · La robustez la hunde

**No hay meseta.** De quince combinaciones de stop y objetivo, sólo dos son
positivas, y las dos están en R:R 1,5 — que **incumple su requisito de 1:2**:

```
   k stop   R:R     n   win rate    exp R      PF
      1,0   1,5    42     45,2%   +0,037    1,06
      1,5   1,5    33     45,5%   +0,074    1,13
      2,0   2,0    29     44,8%   -0,002    1,00   <- la elegida
      3,0   2,0    28     46,4%   -0,154    0,65
```

**Coste doble** (0,08 %/lado): expectativa **−0,061**.

**Parámetros vecinos**: EMA 50/150 −0,002 · EMA 50/250 −0,119 · EMA 30/200
−0,044 · canal 10 −0,037 · canal 40 −0,184. Todos negativos.

## 4 · Y depende de dos operaciones

```
  suma total        -0,06 R
  las 2 mejores     +3,90 R
  sin esas dos      -3,96 R
```

**Dos operaciones de veintinueve cargan con todo.** Y el año 2021 tiene una sola
operación, de +1,93 R.

Por año: 2022 −0,09 · 2023 −0,02 · **2024 −2,07** · 2025 +0,67 · 2026 −0,48.

## 5 · Las dos iteraciones

**Iteración 1 · quitar el filtro EMA** (momentum de ruptura puro), para ganar
muestra:

```
                           n  win rate    exp R      t      PF
  canal 10 · completa     50     34,0%   -0,335  -2,36    0,48
  canal 20 · completa     44     50,0%   -0,033  -0,20    0,93
     canal 20 · FUERA     14     71,4%   +0,430  +1,50    2,68
  canal 55 · completa     31     41,9%   -0,160  -0,79    0,73
```

El canal 20 fuera de muestra da **71,4 % de acierto y +0,430 R**. Con
**catorce operaciones** y t +1,50. No es un resultado, es una racha.

**Iteración 2 · ampliar a 27 años: NO SE PUDO EJECUTAR.** El fichero
`data/ext/fx_daily.csv` (serie diaria de la Reserva Federal, EUR desde 1999) se
perdió al reciclarse el contenedor y la política de red de esta sesión sólo
permite GitHub. **La muestra se queda en 2021-2026 y eso es lo que invalida
todo lo demás.**

## 6 · El problema de fondo no son los parámetros

**Son 29 operaciones en 5,7 años.** Swing momentum en un solo par con filtro de
tendencia produce 6 operaciones al año. Para distinguir una expectativa real de
+0,10 R de cero con un 80 % de potencia harían falta **unas 300 operaciones**:
cincuenta años de este par, o cincuenta pares durante uno.

**Ninguna cantidad de ajuste de parámetros arregla eso.** Lo que haría falta es
más mercado: la cartera de momento multi-activo que este repositorio ya tiene
medida en `RESULTADOS_momento_largo.md`, con 26 series y 632 meses, donde el
mismo arquetipo da t +5,04.

## 7 · Lo que diría un gestor

El arquetipo de momentum **no está refutado** — está medido y funciona en
cartera ancha. Lo que no se sostiene es **esta implementación**: un par, cinco
años, 29 operaciones, sin meseta de parámetros y con dos operaciones cargando
el resultado.

No se pasa a Pine. El código se entrega sólo si valida, y no valida.
