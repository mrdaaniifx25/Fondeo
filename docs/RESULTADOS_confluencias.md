# Resultados · Confluencias multiactivo sobre EURUSD

Ejecución del protocolo fijado en `PREREGISTRO_confluencias.md`.
**Resultado global: negativo.** Ninguna hipótesis alcanza el criterio declarado,
por lo que **la reserva 2024-2026 no se ha abierto** y queda intacta.

---

## Verificación previa (sección 2 del protocolo)

- Huso: los tres pares desplazan su pico de volatilidad exactamente una hora
  entre invierno y verano (mañana 08h→07h, tarde 15h→14h). Correcto.
- Sin OHLC incoherente en ninguno de los 7,2 millones de velas M1.
- Correlaciones de retornos diarios sobre 2.056 días:
  - EURUSD–GBPUSD **+0,728** (predicho +0,85) → 47 % de información independiente
  - EURUSD–USDJPY **−0,489** (predicho −0,50) → 76 % de información independiente

## Contrastes ejecutados: 11 de un tope de 12

Sobre 243 setups de `CRT + order block + DOL diario` en entrenamiento.
Referencia sin filtro: **+0,2143 R/op** (n=224, p 0,082).

| Hipótesis | n | bruto/op | p | 1ª mitad | 2ª mitad | PF |
|---|---|---|---|---|---|---|
| **H3a** confluencia de barrido | 142 | **+0,3521** | 0,027 | +0,239 | +0,465 | **1,382** |
| H3b confluencia en los tres pares | 87 | +0,3333 | 0,101 | +0,209 | +0,455 | 1,358 |
| H4a fuerza relativa | 123 | +0,2358 | 0,159 | −0,016 | +0,484 | 1,204 |
| H2b SMT laxo con USDJPY | 157 | +0,1975 | 0,178 | +0,077 | +0,316 | 1,152 |
| H2a SMT estricto con USDJPY | 110 | +0,1273 | 0,460 | +0,018 | +0,236 | 1,047 |
| H5a correlación desacoplada | 105 | +0,1048 | 0,550 | +0,385 | −0,170 | 1,030 |
| H1b SMT laxo con GBPUSD | 136 | +0,0588 | 0,699 | −0,059 | +0,176 | 0,970 |
| H5b muy desacoplada | 53 | +0,0566 | 0,817 | +0,692 | −0,556 | 0,965 |
| H4b fuerza relativa con umbral | 57 | +0,0526 | 0,823 | −0,143 | +0,241 | 0,967 |
| **H1a SMT clásico con GBPUSD** | 88 | **−0,1364** | 0,440 | −0,273 | +0,000 | **0,735** |
| H6 adelanto-retraso | — | resuelta negativa | — | — | — | — |

## Aplicación de la regla declarada

`n ≥ 150` **y** `bruto > +0,2584` **y** ambas mitades positivas.

**Ninguna la cumple.** H3a supera con holgura las otras dos condiciones pero se
queda en n=142, por debajo del umbral de 150. La regla se aplica tal como fue
escrita: no se mueve el listón a posteriori.

### Defecto reconocido del propio pre-registro

El umbral de +0,2584 se fijó con una cifra calculada sobre la **muestra
completa**, que incluye el periodo de reserva. Es una contaminación introducida
por mí al redactar el protocolo. La referencia correcta dentro de entrenamiento
es **+0,2143**, y contra ella H3a sí destacaría. Aun así H3a sigue fallando el
criterio de tamaño muestral, de modo que la conclusión no cambia.

## El hallazgo, que va en contra de lo esperado

H1a y H3a son complementarios exactos: parten los setups según si GBPUSD barrió
su extremo a la vez que EURUSD o no.

| Reparto | n | bruto/op |
|---|---|---|
| GBPUSD **también** barrió (confluencia) | 142 | **+0,3521** |
| GBPUSD **no** barrió (divergencia SMT) | 88 | **−0,1364** |

Diferencia **+0,4885 R/op**, error estándar 0,2378, **z +2,05, p 0,040**.
No supera la corrección de Bonferroni para 11 contrastes (p < 0,0045).

**La divergencia SMT, que las nueve transcripciones enseñan como confirmación
central, es el peor de los diez filtros probados. Su contrario es el mejor.**

## Decisión

Conforme a la sección 6 del protocolo: resultado negativo, no se buscan
hipótesis adicionales sobre esta muestra, y la reserva permanece cerrada.

H3a queda como hipótesis viva pero **no confirmada**. Probarla como es debido
exige datos que no se hayan tocado: otro instrumento (índices) sería una prueba
mucho más fuerte que gastar la reserva de EURUSD en un contraste post hoc.
