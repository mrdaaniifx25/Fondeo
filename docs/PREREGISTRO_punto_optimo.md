# Pre-registro · ¿existe un punto óptimo de entrada en el CRT?

Firmado **antes** de correr `bt/punto_optimo.py`. Un solo pase.

## La afirmación del usuario, tal cual

> *«Yo pienso que el CRT bien aplicado con constancia y disciplina sí funciona
> pero hay que encontrar el punto óptimo de entrada»*

Es una afirmación **de espacio**, no una hipótesis. No dice «entrar en X
funciona»; dice «existe algún X que funciona». Contestar a eso probando una
variante más no sirve: hay que **recorrer el espacio y medir el mejor hallazgo
contra lo que produce la selección sola**.

Es lo mismo que se hizo en `RESULTADOS_espacio.md` para las variables de
contexto. Esto lo hace para el **instante de entrada**.

## El montaje base: el CRT, sin discusión

Vela M15 que barre un extremo del rango de la vela anterior y **cierra de vuelta
dentro**. Es la definición canónica y es la que él defiende. EURUSD 2021-2026,
oro y DAX 2023-2026. Coste ECN. Horizonte 4 horas.

## Las 220 celdas del espacio de entrada

**Once instantes de entrada:**

| | |
|---|---|
| inmediata | apertura de la vela siguiente al cierre de confirmación |
| retroceso 0,25 / 0,382 / 0,50 / 0,618 / 0,75 | orden límite a ese retroceso del tramo mecha→cierre, válida 8 velas |
| espera 1 / 2 / 3 / 4 / 6 velas | apertura de la vela +N |

**Cuatro stops:** la mecha del barrido · ×1,5 · ×2,0 · el extremo opuesto del rango.

**Cinco objetivos:** R:R 1,0 / 1,5 / 2,0 / 3,0 · el extremo opuesto del rango.

11 × 4 × 5 = **220 celdas**, los tres instrumentos agregados.

Segunda pasada sobre la mejor entrada: **4 tramos horarios × 4 cuartiles de
profundidad del barrido** = 16 celdas más.

## El criterio, declarado antes de mirar

No vale «la mejor celda sale positiva». Con 220 celdas **siempre** sale alguna
positiva. El criterio es:

```
  z de la mejor celda  >  E[máximo de 220 celdas de puro ruido]
```

Ese valor se calcula por simulación **antes** de ver los resultados y se publica
en el documento. Si la mejor celda no lo supera, **el espacio está cerrado**: no
existe un punto óptimo de entrada, porque ninguno de los 220 se distingue de
haber elegido el mejor de 220 monedas.

## Predicción firmada

- **La mejor de las 220 celdas quedará por debajo del umbral de selección.**
- El patrón será reconocible: los stops anchos darán menos coste y más acierto
  pero el mismo neto, porque suben el umbral de equilibrio a la vez.
- Los retrocesos profundos (0,618, 0,75) tendrán **menos** operaciones y mejor
  precio de entrada, y aun así neto cero: es lo que ya salió en
  `RESULTADOS_timing_crt.md`, donde esperar sólo valía algo con la dirección
  dada por el oráculo.
- Ninguna celda con n > 500 pasará de z +2,5.

## Qué me refutaría

Una celda con n > 500 cuya z supere el umbral de selección **y** que mantenga el
signo partiendo la muestra en dos mitades temporales. Eso sería el punto óptimo
que él describe, y lo diría así, con las reglas exactas.

## Sobre la constancia y la disciplina

Conviene dejarlo escrito porque es la otra mitad de su frase. La disciplina
**multiplica** la esperanza por operación; no la crea. Con esperanza bruta medida
en 0,00 y neta en −0,08, la disciplina perfecta da exactamente −0,08 con menos
varianza. Eso no es una opinión: es lo que significa «esperanza».

La disciplina es decisiva **cuando hay ventaja**, porque es lo que impide que la
varianza te saque antes de cobrarla. Sin ventaja, hace las pérdidas más
regulares.

Una sola pasada. Lo que salga se publica.
