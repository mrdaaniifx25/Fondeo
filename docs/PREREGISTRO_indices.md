# Pre-registro · CRT+DOL y confluencia de barrido sobre índices

**Escrito ANTES de recibir los datos de NSXUSD y SPXUSD.**

---

## 1 · Por qué esta prueba es más fuerte que las anteriores

Todos los parámetros del modelo quedaron fijados sobre EURUSD y **no se van a
tocar**. Por tanto el conjunto entero de índices es fuera de muestra por
construcción: no hay partición entrenamiento/reserva porque no hay nada que
entrenar.

**Compromiso explícito: cero reajuste.** Si el modelo con los parámetros de
EURUSD no funciona en índices, el resultado es negativo. No se buscará la
combinación de parámetros que sí funcione — eso convertiría la prueba en el
mismo ejercicio de sobreajuste que llevamos toda la investigación evitando.

## 2 · Parámetros congelados

| Parámetro | Valor fijado en EURUSD |
|---|---|
| Rejilla HTF | H4 anclada a las 01:00 UTC−4 |
| Confirmación | turtle soup en H4 + H1 |
| Disparador | order block en M15 |
| Filtro de dirección | DOL diario, umbral estricto k = 0,5 |
| Objetivo | 3R fijo |
| Stop | extremo del barrido + 1 unidad de colchón |
| Horario | 06:30 – 16:00 UTC |
| Vida máxima | 168 h |
| Una por rango | sí |

Única adaptación admitida, por ser aritmética y no discrecional: el "pip" pasa
a ser el punto del índice, y el colchón del stop se expresa en la misma unidad.

## 3 · Coste

El coste es el eje de toda la hipótesis, así que se declara así:

- Si el usuario aporta el spread real de su bróker, ese es el caso principal.
- En su defecto, caso principal **1,5 puntos** ida y vuelta en NAS100 y
  **0,6 puntos** en SP500, con sensibilidad reportada de 1 a 4 puntos.
- Se reportará siempre la ventaja **bruta**, que no depende del coste, junto a
  la neta. Es la cifra que permite comparar con EURUSD (+0,2584 R/op).

## 4 · Pruebas. Son CUATRO. No se añadirán más.

| # | Prueba | Instrumento |
|---|---|---|
| P1 | CRT+DOL con parámetros congelados | NAS100 |
| P2 | CRT+DOL con parámetros congelados | SP500 |
| P3 | H3a · confluencia de barrido: NAS100 barre a la vez que SP500 | NAS100 |
| P4 | H1a · divergencia: NAS100 barre y SP500 no (control de P3) | NAS100 |

P3 y P4 son complementarios exactos, igual que en EURUSD. Se ejecutan juntos
porque su comparación es una sola estadística.

## 5 · Criterios, declarados de antemano

**El modelo se considera que TRANSFIERE si** en P1 o P2:

1. n ≥ 200 operaciones.
2. Ventaja bruta > 0 con p < 0,05.
3. Profit factor neto > 1,0 con el coste principal.

**La confluencia se considera REPLICADA si** en P3 frente a P4:

4. El signo de la diferencia es el mismo que en EURUSD (confluencia mejor que
   divergencia).
5. p < 0,05 en la diferencia.

Con solo cuatro contrastes, el umbral de Bonferroni es **p < 0,0125**. Se
reportará el resultado frente a los dos umbrales.

## 6 · Qué se reportará pase lo que pase

Las cuatro pruebas con sus números, incluidas las negativas. Si el modelo no
transfiere, se cierra la línea de investigación y se dice así.

## 7 · Expectativa previa, declarada

Espero que la ventaja **bruta** en índices sea similar o algo menor que en
EURUSD, porque el mecanismo (barrido de liquidez en extremos de rango) no
depende del instrumento. Y espero que la **neta** sea claramente mejor, porque
el coste relativo cae de un 6,5 % del riesgo a un 2 % aproximado.

La transferencia del mecanismo es lo que de verdad está en juego. Si la ventaja
bruta desaparece en índices, entonces lo medido en EURUSD era probablemente
ruido afortunado, y la conclusión de toda la investigación pasa a ser negativa
en firme.

Probabilidad previa de que P1 o P2 cumplan los tres criterios: la estimo en
torno a un tercio. Se registra aquí para que el resultado no se lea después
como si se hubiera esperado.
