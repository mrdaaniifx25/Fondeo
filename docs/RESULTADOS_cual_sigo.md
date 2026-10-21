# Resultado · cuál sigo, y el fallo que tuve que arreglar

Código: `bt/estrategia_cerrada.py`, `bt/cual_sigo.py`, `bt/intradia_cerrado.py`,
`bt/version_final.py`. Operativa: `docs/LA_ESTRATEGIA.md`.

---

## El agujero que tenía el plan anterior

`docs/JUEGO_JUSTO.md` decía «dirección: la que tú veas». Está medido que
ninguna regla mecánica de dirección es mejor que otra, así que creí que era
honesto dejarlo abierto. **No lo era**: le dejé a él la única pieza sin cerrar,
que es exactamente lo contrario de lo que hace falta para operar tranquilo.

Aquí se cierra con una regla y se mide.

## 1 · La primera candidata, y por qué no vale

Dirección = momento de 12 meses, que es la única regla de dirección del
proyecto con un resultado independiente y potente detrás
(`RESULTADOS_momento_largo.md`, t +5,04 sobre 26 series y 632 meses).

```
  instr         n  %largo  acierto    bruto     neto      z     PF
  EUR/USD    1234     51%    40.1%  -0.0093  -0.0232  -0.69   0.96
  oro         707    100%    53.5%   0.3484   0.3407   7.15   1.82
  DAX         684    100%    46.1%   0.1123   0.1048   2.25   1.21
  LAS TRES   2625     77%    45.3%   0.1187   0.1082   4.53   1.22
```

**z +4,53 y PF 1,22.** Y no vale nada, por dos motivos que están en la misma
tabla:

1. **`%largo` = 100 % en oro y DAX.** La regla no cambió de lado ni una vez en
   cinco años: es «ponte largo de oro y DAX y espera». El oro subió 143 % y el
   DAX 573 % en esa ventana. Es deriva, no dirección.
2. **La cartera a 0,50 % por operación da +142 % con una caída máxima del
   −46,6 %.** Con un límite del 10 % lo eliminan muchas veces antes de llegar.

Confirmación: en EUR/USD, donde no hay deriva, el lado largo da **−0,0310**.

## 2 · El fallo de modelo que encontré a mitad

Con tope de 5 días y una operación nueva cada día habría **hasta 15 posiciones
abiertas** a la vez. Yo estaba atribuyendo el resultado completo de cada
operación **al día en que se abría**, no a los días que vivía. Eso falsea el
P&L diario, que es justo lo que decide si rompe el límite del 3 %.

Mi simulación daba «muere por límite diario: 0,0 %» y no era verdad.

**Arreglado en `bt/version_final.py`**: una sola posición por instrumento (como
máximo 3 abiertas) y el P&L diario **marcado a mercado** día a día.

## 3 · La versión correcta

```
  instr      n ops  ops/año  acierto   %obj  %stop   neto R      z
  EUR/USD      359       61    43.7%  21.4%  48.7%   0.0728   1.11
  oro          242       64    43.0%  21.5%  48.3%   0.0737   0.92
  DAX          246       67    36.2%  17.9%  56.5%  -0.1018  -1.33

  serie diaria marcada: 1492 días · R/día +0.0127 · sigma 0.955
  peor día -3.72 R · mejor +3.98 R
```

Esperanza ≈ 0, los tres dentro de |z| < 1,4. **Juego justo, confirmado con el
modelo arreglado.**

## 4 · El tamaño sale del peor día, no de un ajuste

```
   riesgo  expos. max   fase 1   LAS DOS  días med  muere día
    0.50%      1.50 %    11.9%      0.0%       nan       0.0%
    0.75%      2.25 %    27.6%      8.9%       148       0.0%
    1.00%      3.00 %    47.6%     14.2%       115      25.5%
    1.25%      3.75 %    52.3%     19.1%       110      29.3%
    1.50%      4.50 %    49.5%     27.5%       111      42.4%
    2.00%      6.00 %    43.9%     20.9%        66      67.8%
```

A simple vista conviene 1,50 %. **No conviene**, y el motivo no está en esta
tabla sino en el peor día observado:

```
  peor día medido en 5,7 años: -3,72 R
    a 0,75 %  ->  -2,79 %   sobrevive        ✔
    a 1,00 %  ->  -3,72 %   ELIMINADO        ✘
```

**0,75 % es el riesgo más alto que sobrevive al peor día que ha pasado de
verdad.** Las celdas de 1,00 % en adelante compran probabilidad de aprobar
pagando con un 25-68 % de muerte por límite diario, y además sus cifras están
dentro del ruido de este remuestreo (5,7 años dan ~5 bloques independientes de
300 días: no distingue el 19,1 % del 27,5 %).

## 5 · Lo que descarto, y lo digo

Probé también cerrar dentro del día (`bt/intradia_cerrado.py`), que arregla el
solapamiento por completo. Resultado: con stop de 1,0 x ATR sólo el **0,6 %** de
las operaciones llega al objetivo y el 89,9 % cierra por hora. La estructura
1:2 no se materializa y la carrera se vuelve demasiado lenta: las dos fases,
**6,1 %**. Descartado.

Y la tabla de tope 1.200 días de `bt/version_final.py` **no vale**: con 1.492
días de serie sólo hay 292 arranques posibles para esa ventana, así que los
remuestreos son casi el mismo camino. Los 0,0 % y el 72,4 % de esa columna son
artefactos. Queda anotado en el propio código.

## 6 · Corrección a lo publicado ayer

`docs/LO_SIMPLE.md` daba **35,8 %** de pasar las dos fases. Sale de un modelo
que supone operaciones **independientes**. Con los caminos diarios reales —donde
los días malos van juntos— el mismo cálculo da **8,9 %** a 0,75 %, con el tope
de 300 días truncando por el otro lado.

**La cifra honesta es un rango: entre el 10 % y el 35 %**, y depende sobre todo
de si su examen tiene límite de días. Con 5,7 años de datos no se puede
estrechar más, y decir 35,8 % a secas era optimista.
