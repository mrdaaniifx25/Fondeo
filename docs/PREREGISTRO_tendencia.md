# Pre-registro · Seguimiento de tendencia, la mitad no probada de la moneda

**Escrito ANTES de ejecutar nada.**

---

## 1 · Por qué esta prueba y no otra

Todo lo medido hasta ahora ha sido **reversión**: el CRT, la turtle soup, el
barrido de liquidez y el order block consisten en operar *contra* la rotura de
un extremo previo. Los tres dan cero, en cinco mercados.

La mitad complementaria nunca se ha probado: operar **a favor** de la rotura.

Hay dos motivos para probarla y no otra cosa:

1. **Es el complemento mecánico exacto de lo ya refutado.** Si desvanecer la
   rotura vale cero, lo que hay al otro lado del mismo suceso merece una
   medición, no una suposición.
2. **Encaja con el único hallazgo positivo de toda la investigación.** Medí que
   la gestión protectora (break-even, parciales, trailing corto) destruye el
   resultado porque los retornos tienen cola derecha: unas pocas operaciones muy
   grandes sostienen todo lo demás. Esa es la firma de una distribución de
   tendencia, no de reversión.

Además es el único patrón con evidencia externa larga y fuera de muestra
(décadas, muchos mercados). Eso no lo hace cierto aquí, pero sí lo hace la
siguiente hipótesis a gastar.

## 2 · Parámetros, canónicos y no elegidos por mí

Se usan los parámetros clásicos del sistema Turtle, publicados en 1983. No los
elijo yo mirando estos datos, y por tanto no hay margen de pesca.

| Parámetro | Valor |
|---|---|
| Marco | diario, día cerrado a las 17:00 Nueva York |
| Entrada | cierre diario que rompe el máximo/mínimo de los N días previos |
| Ejecución | apertura del día siguiente |
| N | 55 (**principal**), 20 (robustez) |
| Stop | 2 × ATR(20) diario |
| Salida A (**principal**) | Donchian opuesto de N/2 días, actualizado a cierre |
| Salida B (robustez) | 3R fija, la misma que se usó en el CRT |
| Vida máxima | 120 días |
| Una posición por instrumento a la vez | sí |

## 3 · Instrumentos y coste

Los cinco que hay, sin escoger: EURUSD, GBPUSD, USDJPY, NAS100, SP500.
Periodo completo 2020-01 → 2026-07.

Coste ida y vuelta: 1,2 pips en EURUSD y USDJPY, 1,5 en GBPUSD, 1,5 puntos en
NAS100, 0,6 en SP500. Los mismos de siempre.

## 4 · Contrastes primarios: SON DOS

| # | Contraste |
|---|---|
| T1 | N=55 + salida Turtle, agregado de los **tres pares de divisas** |
| T2 | N=55 + salida Turtle, agregado de los **dos índices** |

Las otras seis celdas (N=20, salida 3R) se reportan como robustez, **no** como
contrastes. Umbral de Bonferroni para dos contrastes: **p < 0,025**.

## 5 · Controles obligatorios

1. **Espejo:** tomar la dirección contraria en cada señal. Si la rotura tiene
   ventaja, desvanecerla debe tener desventaja. Si ambos salen positivos, lo que
   se está midiendo es un artefacto del motor y no una ventaja.
2. **Entrada aleatoria:** mismo número de operaciones, días de entrada al azar,
   idéntica gestión. Cualquier ventaja debe superar a esto.
3. **Comprar y mantener (solo índices):** un sistema largo/corto sobre un activo
   que sube durante seis años puede parecer bueno midiendo únicamente la deriva.
   Si no bate a comprar y mantener, no es una estrategia: es beta con pasos
   intermedios.

## 6 · Criterios, declarados de antemano

Se considera que **funciona** si en T1 o T2:

1. n ≥ 200 operaciones agregadas.
2. Ventaja bruta > 0 con p < 0,05 (se reporta también frente a 0,025).
3. Profit factor neto > 1,0 con el coste principal.
4. El control espejo sale negativo.
5. Supera al control de entrada aleatoria.
6. **Solo para T2:** el rendimiento neto supera a comprar y mantener el índice.

## 7 · Expectativa previa, declarada para que no se lea después como esperada

En divisas, el seguimiento de tendencia se ha deteriorado mucho desde 2008; está
documentado y el periodo 2020-2026 es corto. **Probabilidad de que T1 cumpla
todos los criterios: la estimo en un 25 %.**

En índices espero que las cifras brutas salgan positivas y que aun así **falle el
criterio 6**, porque el NASDAQ y el S&P suben mucho en este periodo y eso
contamina cualquier sistema con sesgo largo. **Probabilidad de que T2 cumpla
todos los criterios, incluido el 6: la estimo en un 15 %.**

Probabilidad de que alguno de los dos pase: en torno a un tercio.

## 8 · Advertencia que ya sé y registro ahora, pase lo que pase

Aunque salga positivo, el seguimiento de tendencia tiene **tasa de acierto baja
(30-40 %) y rachas perdedoras largas**. Eso choca de frente con un reto de fondeo
con pérdida máxima del 10 %. Si T1 o T2 pasan, la siguiente pregunta no es «¿es
rentable?» sino «¿sobrevive a las reglas del reto?», y se responderá con el
mismo Monte Carlo ya construido. Un resultado positivo aquí **no** implica que
sirva para el fondeo, y no se presentará como si lo implicara.

## 9 · Qué se reportará

Las ocho celdas, los tres controles y los dos contrastes primarios, salgan como
salgan. Si sale negativo se dice que sale negativo y se cierra también esta vía.
