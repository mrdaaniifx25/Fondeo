# Resultados · Estrategia del vídeo «de 120 a 1.000 dólares»

Reglas transcritas literalmente: pivote de H1 o H4 liquidado → operar en contra,
solo en Londres 09:00-11:00 y Nueva York 14:00-16:30 hora española, entrada en un
imbalance de tres velas en M1-M5, stop cubriendo el extremo, objetivo 1:2. EURUSD.

**Tal como se describe: pierde dinero. Pero deja el segundo hallazgo con profit
factor por encima de 1 de todo el proyecto, y una lección que sí generaliza.**

---

## La estrategia tal cual

| niveles | entrada | n | al año | bruto/op | p | %TP | **PF neto** |
|---|---|---|---|---|---|---|---|
| **H1** | **M1** | 2.504 | 379 | **+0,0566** | 0,046 | 34,5 % | **0,848** |
| H1 | M2 | 2.376 | 360 | +0,0198 | 0,490 | 32,2 % | 0,844 |
| H1 | M5 | 1.855 | 281 | −0,0261 | 0,403 | 28,6 % | 0,823 |
| H4 | M1 | 927 | 140 | −0,0211 | 0,644 | 31,4 % | 0,764 |
| H4 | M2 | 923 | 140 | +0,0018 | 0,969 | 31,5 % | 0,827 |
| H4 | M5 | 787 | 119 | +0,0119 | 0,805 | 29,5 % | 0,877 |

Ninguna llega a profit factor 1. La mejor, con los parámetros exactos del vídeo
(H1 + M1), da **0,848**.

## El control

| | n | bruto/op | PF neto |
|---|---|---|---|
| La estrategia | 2.504 | +0,0566 | 0,848 |
| Espejo (dirección contraria) | 2.264 | +0,0057 | 0,789 |
| **Dirección al azar** (5 rep) | 12.067 | **+0,0266** | 0,814 |

Diferencia estrategia menos azar: **+0,0300, z +0,96, p 0,336. No significativa.**
Otra vez indistinguible de una moneda.

## Lo que el vídeo acierta

**El objetivo 1:2 es el mejor de los cuatro probados.** No es arbitrario:

| objetivo | %TP | PF neto |
|---|---|---|
| 1:1 | 50,8 % | 0,738 |
| 1:1,5 | 40,9 % | 0,801 |
| **1:2** | 34,5 % | **0,848** |
| 1:3 | 24,6 % | 0,847 |

**Y los horarios aquí sí ayudan**, al contrario de lo que salió con el CRT:

| | n | bruto/op | PF neto |
|---|---|---|---|
| Londres 09-11 | 1.162 | +0,0641 | 0,846 |
| Nueva York 14-16:30 | 1.417 | +0,0644 | 0,866 |
| **fuera de las dos** | 4.072 | **−0,0041** | 0,738 |

Diferencia dentro menos fuera: +0,0607, z +1,68, **p 0,092**. No significativa,
pero apunta en la buena dirección.

### Corrección de un hallazgo anterior mío

En `RESULTADOS_lectura_completa.md` reporté que la killzone **restaba**
(−0,2998, p 0,0012) sobre el montaje del CRT. Aquí, sobre este otro montaje,
**suma**. Las dos cosas son ciertas y no se contradicen: **el efecto del filtro
horario depende del setup, no es una ley general.** Mi redacción anterior daba a
entender lo segundo y era demasiado amplia.

## El problema real, y la lección que sí generaliza

```
riesgo mediano                       7,7 pips
operaciones con stop < 5 pips        554  (22,1 %)
el coste de 1,2 pips es              el 17,0 % del riesgo
```

Diecisiete por ciento. Contra el 6,5 % del CRT y el 12,7 % de la liquidez de
sesiones. **El stop apretado es lo que la mata.**

Y al forzar un stop mínimo, esto pasa:

| stop mínimo | n | bruto/op | p | **PF neto** |
|---|---|---|---|---|
| sin mínimo | 2.504 | +0,0566 | 0,046 | 0,848 |
| ≥ 5 pips | 1.950 | +0,0752 | 0,020 | 0,918 |
| ≥ 8 pips | 1.181 | +0,0463 | 0,258 | 0,927 |
| **≥ 12 pips** | **591** | **+0,1131** | 0,050 | **1,068** |

**Es la segunda celda de todo el proyecto con profit factor por encima de 1**, tras
el efecto lunes. 591 operaciones, unas 90 al año.

No es una confirmación: p 0,050 justo en el filo, es un corte elegido después de
ver los datos, y no hay reserva ciega. Pero es la primera vez que aparece un
mecanismo claro y repetible detrás de un resultado positivo, en vez de ruido:
**si el coste es un porcentaje fijo del stop, agrandar el stop reduce el coste
relativo.** Eso no es una casualidad de la muestra, es aritmética.

## Contexto del vídeo

El autor vende referidos de empresas de fondeo, con código de descuento incluido.
No invalida sus reglas —están mejor especificadas que la mayoría— pero conviene
saber de dónde sale el incentivo: su negocio es que compres cuentas, no que ganes
con ellas.

Y su premisa de partida es falsa por construcción: «convertir 120 en 1.000
comprando tres cuentas de 10.000». Con la ventaja real de esta estrategia
(PF 0,848), la probabilidad de pasar las dos fases no es la que insinúa.

## Conclusión

Como se describe, no funciona. Pero deja dos cosas:

1. **Una pista real**: exigir un stop mínimo de 12 pips lleva el profit factor a
   1,068 sobre 591 operaciones, con un mecanismo aritmético detrás y no ruido.
2. **Una corrección**: el filtro horario ayuda o perjudica según el setup. Mi
   afirmación anterior era demasiado general.
