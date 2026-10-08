# Las condiciones reales de FundingPips · 2 Step Standard, 10.000 $

Extraídas del documento oficial que él pasó
(`Objetivos_de_trading___FundingPips.pdf`). Sustituyen a los valores estándar que
yo estaba suponiendo.

## Evaluación · las dos fases

| | fase 1 | fase 2 |
|---|---|---|
| objetivo de ganancias | **8 %** (800 $) | **5 %** (500 $) |
| días mínimos de trading | **3** | **3** |
| período | **ilimitado** | **ilimitado** |
| apalancamiento | 1:100 | 1:100 |

**Límites, iguales en ambas fases:** pérdida diaria máxima **5 %**, pérdida total
máxima **10 %**.

**Lo que el documento sí aclara y yo no sabía:**

- **Sin límite de tiempo.** No hay prisa, y eso elimina el riesgo de forzar.
- **Por debajo de 25.000 $ no hay pautas de riesgo** ni *striking system*: no le
  aplica la restricción del 1 % por operación ni los avisos por pérdida flotante.
- **Trading de noticias permitido** durante la evaluación (en la cuenta maestra
  ya no: 5 minutos antes y después de carpeta roja).
- **Inactividad:** al menos una operación cerrada cada 30 días.
- **La regla del 60 %:** si una sola idea de trade se lleva más del 60 % del
  objetivo, la cuenta maestra exige 4 días rentables. Con su riesgo del 1 %, una
  ganancia es 200 $ = **25 %** del objetivo, así que **nunca la va a tocar**.

**Lo que el documento no dice**, y son justo los dos que más mueven el cálculo:
si la pérdida máxima total es fija o *trailing*, y si el límite diario se mide
sobre saldo cerrado o sobre equity. Ambas se han resuelto midiendo.

## La pérdida flotante no llega al límite diario

Medido sobre sus 86 operaciones, cuánto se va en contra cada una antes de
resolverse (`bt/examen_mae.py`):

```
mediana 0,75 R  ·  máximo 1,42 R
  las que acaban en TP     mediana 0,47 R
  las que acaban en SL     mediana 1,09 R
```

Y la peor caída **acumulada** dentro de una sesión, sumando las cerradas más la
flotante de la abierta en su peor momento:

```
mediana -0,75 R  ·  peor sesión de las 54: -2,78 R
sesiones que bajarían de -5 R: 0 de 54
```

El límite diario del 5 % son **5 R** con riesgo del 1 %. **No lo toca ni midiendo
sobre equity.** La pregunta queda cerrada: da igual cómo lo calculen.

## Fijo contra trailing: al 1 % da igual

Probabilidad de **pasar las dos fases**, 8.000 simulaciones por celda:

| riesgo | fijo | trailing | fijo (prudente) | trailing (prudente) |
|---|---|---|---|---|
| 0,50 % | 99,9 % | 99,9 % | 92,1 % | 92,1 % |
| 0,75 % | 100,0 % | 99,9 % | 96,5 % | 95,7 % |
| **1,00 %** | **99,9 %** | **99,5 %** | **95,8 %** | **92,5 %** |
| 1,50 % | 98,3 % | 96,3 % | 89,8 % | 82,1 % |
| 2,00 % | 72,5 % | 71,1 % | 64,9 % | 60,2 % |

«Prudente» = solo los bloques 1 y 2, sin el 81 % del tercero.

**Al 1 % la diferencia entre fijo y trailing es de tres puntos.** Solo empieza a
importar a partir del 1,5 %. Así que la duda del documento no cambia la decisión:
**1 %, y no hace falta averiguarlo.**

## Lo que queda ajustado en el examen

- Cuenta en **dólares**, no en euros.
- **Mínimo de 3 días operados** antes de poder superar el reto.
- Objetivo 800 $, límite diario 500 $, límite total 1.000 $.
- Riesgo 1 % = 100 $ por operación, lotaje calculado desde su stop.
