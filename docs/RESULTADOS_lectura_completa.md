# Resultados · Las piezas que faltaban de la lectura

Tres mediciones para cerrar el marco de lectura del usuario: PDH/PDL como
objetivo, el FVG de verdad como entrada, y su lectura completa capa por capa.

---

## 1 · PDH y PDL como objetivo del barrido

La pregunta: ¿es el máximo o mínimo del día anterior un **imán**, o es un precio
como cualquier otro? Se compara contra un **placebo**: el mismo objetivo
desplazado 15 o 30 pips, con idéntica entrada y stop.

| objetivo | n | bruto/op | p | %TP | PF neto |
|---|---|---|---|---|---|
| **PDH/PDL de verdad** | 3.271 | −0,0813 | 0,017 | 15,1 % | 0,771 |
| desplazado 15 pips (placebo) | 3.098 | −0,0883 | 0,013 | 14,4 % | 0,764 |
| desplazado 30 pips (placebo) | 2.857 | −0,0714 | 0,056 | 13,0 % | 0,785 |

**Indistinguibles.** Un nivel arbitrario a 30 pips del PDH rinde exactamente igual
que el PDH. No hay nada especial en ese precio.

Y las tres son **negativas**, dos de ellas significativamente. Apuntar al PDH/PDL
tras el barrido de una sesión pierde dinero de forma sistemática.

## 2 · El FVG de verdad como entrada

Hasta ahora se había medido el Fibonacci como equivalente estructural. Aquí está
el FVG real: tres velas M15 cerradas, hueco entre el máximo de la primera y el
mínimo de la tercera, entrada limitada dentro del hueco.

| dónde entras | n | bruto/op | p | %TP | PF neto |
|---|---|---|---|---|---|
| borde cercano | 145 | +0,1138 | 0,480 | 29,7 % | 0,954 |
| 50 % del hueco | 136 | +0,0095 | 0,954 | 26,5 % | 0,830 |
| **borde lejano** | 122 | **+0,1802** | 0,333 | 30,3 % | **1,036** |

Mismo patrón que el Fibonacci: **cuanto más profundo, mejor**. El borde lejano es
la única celda con profit factor por encima de 1 en toda esta tanda.

Pero son **122 operaciones y p 0,333**. No significa nada todavía. Es la
candidata más interesante que queda, y necesitaría una prueba propia con reserva
ciega para valer algo.

## 3 · La lectura completa, capa por capa

Añadiendo una condición cada vez, sobre EURUSD 2020-2026:

| capa | n | bruto/op | p | PF neto |
|---|---|---|---|---|
| 1. solo turtle soup H4 | 1.009 | +0,0211 | 0,722 | 0,854 |
| 2. + turtle soup H1 | 826 | −0,0638 | 0,322 | 0,752 |
| 3. **+ killzone** | 308 | **−0,2998** | **0,0012** | **0,516** |
| 4. + entrada en FVG de M15 | 20 | +0,1238 | 0,729 | 0,941 |
| 5. + el barrido toca PDH/PDL | 12 | +0,3728 | 0,457 | 1,298 |
| 6. + Londres barrió el rango de Asia | 4 | −0,0044 | 0,997 | 0,755 |

**Dos lecturas de esta tabla.**

La primera: a partir de la capa 4 quedan **20, 12 y 4 operaciones**. El +0,3728
con profit factor 1,298 de la capa 5 son doce operaciones en seis años y medio.
No es un resultado, es ruido con formato de tabla. Ahí está la trampa de apilar
condiciones.

La segunda es más interesante, y va aparte.

## El hallazgo: la killzone RESTA

La capa 3 no solo no mejora: hunde el resultado de −0,0638 a −0,2998, con
p 0,0012. Verificado mirando el complementario:

| | n | bruto/op | p | PF neto |
|---|---|---|---|---|
| **dentro** de killzone | 308 | **−0,2998** | 0,0012 | 0,516 |
| **fuera** de killzone | 630 | **+0,0429** | 0,580 | 0,868 |

```
diferencia dentro menos fuera: −0,3426 R/op | z −2,83 | p 0,0046
```

Es coherente por los dos lados y el efecto es grande. **Sobre este setup, la
regla de «opera solo en killzones» destruye el resultado.**

Ojo con leerlo al revés: fuera de killzone tampoco se gana (PF 0,868). No es
«opera de madrugada y ganarás». Es que la regla más repetida de toda la
metodología ICT, aplicada a este setup concreto, es contraproducente.

Con quince contrastes en esta tanda el umbral de Bonferroni es p < 0,0033. El
nivel de dentro-de-killzone (p 0,0012) lo pasa; la diferencia (p 0,0046) se queda
justo fuera.

## Estado del marco de lectura, ya completo

| pieza | veredicto |
|---|---|
| Turtle soup H4 | cero |
| + turtle soup H1 | resta |
| Killzones | **resta, y de forma significativa** |
| FVG M15 borde lejano | única con PF > 1, sin significación (n=122) |
| PDH/PDL como filtro de dirección | cero |
| PDH/PDL como objetivo | igual que un placebo, y negativo |
| Liquidez de sesiones | moneda al aire (49,7 % / 50,3 %) |
| Rango de Asia barrido por Londres | no filtra: pasa el 94,8 % |

Las seis piezas del marco están medidas. Ninguna aporta ventaja. La única que
queda viva como hipótesis es la entrada en el borde lejano del FVG, y con 122
operaciones no da para más que para anotarla.
