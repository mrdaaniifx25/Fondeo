# Resultados · CRT canónico según la guía de Rubén Villahermosa

Reimplementación fiel del CRT a partir de la guía completa (35 páginas), después
de que el usuario pidiera revisar mi interpretación.

**Encontré dos errores reales en mi implementación anterior. Los dos cambian los
números. Ninguno cambia la conclusión.**

---

## Error nº1 · El anclaje de la rejilla H4

La guía dice: *«las velas de 4 horas que cierran a la 1am y 5am hora EST»*, y su
tabla de conversión confirma `1:00 AM EST = 7:00 CET`.

Yo anclaba a las **01:00 UTC**, que en horario de Nueva York son las 20:00. Mi
rejilla era la familia `{00, 04, 08, 12, 16, 20}` hora NY. La correcta es
`{01, 05, 09, 13, 17, 21}` hora NY, **con cambio de hora**.

| Anclaje | n | bruto/op | PF neto |
|---|---|---|---|
| 01:00 Nueva York · **la de la guía** | 122 | **−0,0895** | 0,791 |
| 00:00 Nueva York · la que yo usaba | 83 | −0,1935 | 0,670 |

Corregirlo mejora el resultado a menos de la mitad de malo. Sigue negativo.

*(01:00 y 05:00 dan idéntico resultado: en una rejilla de 4 horas, anclar a una u
otra produce la misma malla.)*

## Error nº2 · Entrar en la Vela 2 en vez de la Vela 3

La guía es explícita y lo llama **«Error #1: el mayor destructor de cuentas»**:

> *«Muchos traders entran en la Vela 2 apenas ven la liquidación. Esto es
> prematuro. La confirmación llega con la Vela 3 cuando cierra de vuelta dentro
> del rango.»*

Yo entraba dentro de la Vela 2. Comparación con todo lo demás igual:

| Entrada | n | bruto/op | p | PF neto |
|---|---|---|---|---|
| Vela 2 (agresiva) | 122 | −0,0895 | 0,458 | 0,791 |
| **Vela 3 (conservadora)** | 559 | **+0,0248** | 0,717 | **0,884** |

Corregirlo mueve el resultado de negativo a **cero**. No a positivo: p 0,717 es
indistinguible de la nada, y el profit factor neto de 0,884 sigue perdiendo.

Por instrumento con la corrección aplicada: EURUSD +0,036 · GBPUSD −0,026 ·
USDJPY −0,054 · NAS100 +0,118 · SP500 +0,103.

## Lo que sí tenía bien

Rango de la vela de referencia cerrada, barrido de un extremo, cierre de vuelta
dentro como confirmación, stop tras la mecha de manipulación, objetivo en el
extremo opuesto. Todo eso coincide con la guía.

## Las demás reglas de la guía, aplicadas

Todas implementadas: cierre estricto del cuerpo de la Vela 2 dentro del rango,
killzones en CET (Londres 08-11, NY 13-16 forex / 15:30-17 índices, London Close
16-18, excluyendo el almuerzo europeo 11-13), R:R mínimo 1,5, tope de 3
operaciones diarias, orden **stop** en lugar de a mercado, y mitigación.

Quitándolas de una en una, ninguna aporta:

| variante | n | bruto/op | PF neto |
|---|---|---|---|
| completa | 122 | −0,0895 | 0,791 |
| sin exigir cierre de V2 dentro | 255 | −0,0749 | 0,815 |
| sin killzones | 793 | −0,0254 | 0,882 |
| con R:R mínimo 1,0 | 365 | −0,0464 | 0,838 |

## Otras temporalidades de referencia

La guía admite H1, H4 y D1. Aquí aparecen las dos cifras más atractivas:

| referencia | n | bruto/op | p | PF neto |
|---|---|---|---|---|
| **H1** | 241 | **+0,1598** | 0,079 | **1,129** |
| H4 | 122 | −0,0895 | 0,458 | 0,791 |
| **D1** | 55 | **+0,2033** | 0,254 | **1,372** |

Con 18 celdas examinadas, el umbral de Bonferroni es **p < 0,0028**. Ninguna se
acerca.

## El control que cierra el asunto

Sobre la celda de mayor ventaja (D1, entrada en Vela 2), sorteando la
**dirección** al azar y dejando idéntica toda la mecánica — mismo rango, mismo
stop tras el barrido, mismo objetivo, mismas killzones:

| | n | bruto/op | z | PF neto |
|---|---|---|---|---|
| La estrategia | 55 | +0,2033 | +1,14 | 1,372 |
| **Dirección AL AZAR** (10 rep) | 269 | **+0,2610** | +3,26 | **1,513** |

**Sortear una moneda para decidir si comprar o vender rinde más que el patrón
CRT.** Lo positivo que se ve no es información direccional: es la geometría del
stop y el objetivo, que con R:R de 2 y stop tras una mecha produce ese número
tomes la dirección que tomes.

## El problema de fondo, que no es la estrategia

El CRT canónico con todos los filtros de la guía produce **122 operaciones en
seis años y medio repartidas entre CINCO instrumentos**. Son unas 24 por
instrumento, menos de 4 al año.

Con esa muestra no se puede demostrar nada, ni a favor ni en contra. Aunque el
patrón tuviera una ventaja real de +0,20 R, harían falta unas 600 operaciones
para distinguirla del azar. A 4 al año son 150 años.

## Dos limitaciones honestas de esta prueba

1. **El control de espejo que ejecuté primero no vale.** Invertir el signo del
   resultado bruto es aritméticamente forzoso y no informa de nada. El control
   válido es el de dirección al azar, que es el que reporto arriba.
2. **La celda «H1 + entrada en Vela 3» dio cero operaciones** por una limitación
   mía: aproximo la vela de reacción con la primera hora de la Vela 3, y en
   referencia H1 eso consume la vela entera. Es un hueco de implementación, no un
   resultado.

## Conclusión

Corregidos los dos errores, esta es la implementación más fiel del CRT que puedo
construir a partir de la fuente. Pasa de perder a no ganar. Y su mejor celda
pierde contra echar una moneda al aire.

Lo que la guía misma reconoce en su sección de limitaciones —*«no incluye
análisis de volumen, no identifica la fase del mercado, alta frecuencia de
señales falsas»*— coincide con lo medido. Su propia respuesta a eso es añadir
contexto Wyckoff discrecional, que no es mecanizable y por tanto no es
verificable con este método.
