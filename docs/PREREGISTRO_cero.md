# Pre-registro · Empezar de cero

**Escrito antes de generar una sola variable ni mirar un solo resultado.**

---

## 1 · Por qué esto es distinto de todo lo anterior

Las siete estrategias probadas hasta ahora tienen algo en común que las
condenaba de antemano: **todas fueron diseñadas por una persona mirando un
gráfico**. Ese proceso selecciona patrones que resultan convincentes a la vista,
no patrones que tengan información. Son dos cosas distintas y por eso todas
dieron cero.

Aquí se invierte la dirección. No se parte de una idea para ver si funciona. Se
parte de los datos y se pregunta qué contienen, sin saber de antemano qué
debería aparecer.

Eso tiene una ventaja y un peligro:

- **Ventaja:** ninguna variable entra porque «tiene sentido». Entran todas por
  igual, incluidas las que a un humano no se le ocurrirían.
- **Peligro:** con suficientes variables SIEMPRE se encuentra algo. Es el mismo
  mecanismo que fabricó el +0,4885 de EURUSD que luego no replicó. Con 500
  contrastes al 5 %, salen 25 falsos positivos por pura aritmética.

Todo el protocolo existe para neutralizar ese peligro.

## 2 · Los dos conjuntos de datos

| | qué | para qué |
|---|---|---|
| **Descubrimiento** | EURUSD, GBPUSD, USDJPY, NAS100, SP500 · 2020-2026 | buscar |
| **Confirmación** | instrumentos NUEVOS, aún no descargados | confirmar, una sola vez |

**El conjunto de descubrimiento está quemado y se asume así.** Llevamos una
semana mirándolo. Cualquier cosa que aparezca ahí es sospechosa por
construcción, y por eso no vale como resultado: solo vale como candidata.

**El conjunto de confirmación tiene que ser nuevo.** Instrumentos que nunca
hemos tocado, descargados después de fijar las candidatas. Es la única forma de
que la confirmación signifique algo.

Compromiso: **no se mira el conjunto de confirmación hasta que las candidatas
estén cerradas y escritas.** Y se abre **una sola vez**.

## 3 · Las variables: mecánicas, no interpretadas

Se generan por combinación sistemática, sin criterio narrativo. Familias:

1. **Retornos** a 1, 2, 4, 8, 12, 24, 48, 96 y 192 velas
2. **Volatilidad** — rango real, desviación, y su cociente entre ventanas
3. **Posición** — dónde está el precio dentro del rango de las últimas N velas
4. **Tiempo** — hora del día, día de la semana, día del mes, sesión
5. **Distancias** a máximos y mínimos de N velas, en unidades de volatilidad
6. **Forma de la vela** — cuerpo, mechas, y sus proporciones
7. **Cruzadas** — las mismas medidas en los otros instrumentos, alineadas

Ninguna lleva nombre de metodología. No hay «barrido», ni «FVG», ni «order
block». Si alguno de esos conceptos tiene información, aparecerá reflejado en
alguna de estas medidas.

Objetivo a predecir: **el retorno de las siguientes N velas dividido por la
volatilidad**, para N en 4, 12 y 48. Normalizado para que sea comparable.

## 4 · El cribado y su corrección

Para cada variable se mide su capacidad predictiva con el estadístico declarado
de antemano: **correlación de rangos de Spearman** entre la variable y el
objetivo, más el retorno medio del decil superior menos el del inferior.

Tres capas de protección, todas obligatorias:

1. **Nulo por permutación.** Se repite el cribado ENTERO sobre el objetivo
   barajado, 200 veces. Eso da la distribución de «la mejor variable posible
   cuando no hay nada». Una variable real tiene que superar el percentil 99 de
   esa distribución. **Este es el filtro principal**, porque absorbe
   automáticamente el número de contrastes, la correlación entre variables y la
   autocorrelación de la serie.
2. **Tasa de falso descubrimiento** (Benjamini-Hochberg) al 10 %.
3. **Estabilidad temporal**: el signo debe mantenerse en al menos 5 de los 7 años.

Una variable que no pase las tres, no pasa. No hay «casi».

## 5 · Qué se hace con lo que sobreviva

Nada de operarlo. Se construye la operativa mínima —entrada, stop por
volatilidad, objetivo— y se mide **coste sobre riesgo** antes que ninguna otra
cosa, porque es lo que ha matado todo lo anterior:

```
CRT                     6,5 %  del riesgo
liquidez de sesiones   12,7 %
vídeo de fondeo        17,0 %
```

**Regla dura declarada ahora: si el coste supera el 8 % del riesgo, se descarta
sin más análisis.** Esto obliga a stops amplios desde el principio y evita
repetir el error de perseguir señales de stop apretado.

## 6 · Criterios de éxito, escritos de antemano

Se considera que hay un hallazgo si, y solo si:

1. Supera el percentil 99 del nulo por permutación en descubrimiento
2. Mantiene el signo en 5 de 7 años
3. El coste no pasa del 8 % del riesgo
4. **Y replica en el conjunto de confirmación**, con el mismo signo y al menos
   la mitad de la magnitud

Si nada llega al punto 4, la conclusión es negativa y se dice así.

## 7 · Expectativa previa, declarada

Después de siete estrategias en cero, sería deshonesto anunciar optimismo.
**Estimo la probabilidad de que algo llegue al punto 4 en un 15-20 %.**

Lo que sí cambia respecto a antes: si esta vez sale algo, será algo que nadie
puso ahí. Y si no sale nada, la respuesta será mucho más definitiva que
«esas siete estrategias concretas no funcionan», porque el cribado no depende
de que a alguien se le ocurriera la idea correcta.

## 8 · Lo que hace falta para empezar

Los instrumentos de confirmación, que deben ser nuevos. De HistData, mismo
formato ASCII M1 que los anteriores. Cuantos más, mejor, pero con cuatro basta:

```
AUDUSD    USDCAD    USDCHF    EURGBP    NZDUSD    XAUUSD (oro)
```

Hasta tenerlos, se puede avanzar con el descubrimiento, pero **no se cierra
nada** sin la confirmación.
