# Pre-registro · el CRT en 12 horas, sobre instrumentos nunca vistos

**Escrito el 2026-08-27, antes de tener los datos.** Ese es el punto: la
predicción queda fijada mientras los ficheros todavía no existen en el
repositorio, así que no hay forma de ajustarla al resultado.

## De dónde sale la hipótesis

`RESULTADOS_crt_tf_partido.md`: H12 es la única temporalidad con neto positivo
en las dos mitades del tiempo (+0,085 en 2020-2023, +0,055 en 2024-2026). Débil
—z +1,32, el intervalo incluye el cero— y sostenida sobre todo por SPX500.

El mecanismo propuesto es una división, no un patrón: **el coste en unidades de
R es `coste_fijo / riesgo`**. La ventaja bruta del CRT es plana en todas las
temporalidades (Q = 7,75 con 6 gl), pero el riesgo crece con el marco, así que
el coste pesa menos arriba. En EURUSD el coste que dejaría la neta en cero es de
0,44 pips en H1 y de 1,92 pips en H12.

**Si el mecanismo es cierto, tiene que cumplirse en instrumentos que nunca hemos
tocado. Si es sobreajuste, no.**

## Qué se va a correr, exactamente

Sin margen de decisión posterior. El mismo código que produjo
`RESULTADOS_crt_temporalidad.md`, sin tocar:

```
CRT desnudo, liquidez simple (k = 1)
objetivo   = extremo opuesto de la vela base
stop       = extremo barrido
anclaje    = ancla_ny = 1        (el mismo de siempre)
barrido de temporalidades  H1 · H2 · H4 · H8 · H12 · D1
```

**Celda principal, declarada ahora: H12.** Las demás son secundarias y se
reportan enteras.

## Las predicciones

1. **La ventaja bruta en H12 será positiva**, entre **+0,05 y +0,15 R**.
2. **El coste será menos del 4 % del riesgo** en H12, en todos los instrumentos
   nuevos.
3. **La neta en H12 será positiva.**
4. **La bruta será plana entre H1 y D1**, sin tendencia (prueba de
   heterogeneidad de Cochran no significativa).
5. **La neta en H1 será negativa** en todos los instrumentos nuevos, sin
   excepción. Esta es la predicción que más me juego: si algún instrumento nuevo
   sale positivo en H1, el mecanismo del coste está mal planteado.

## Qué cuenta como éxito

Con el error estándar del **bootstrap por bloques** (`BC_08` §3), no el ingenuo:

```
la neta de H12, agrupando los instrumentos nuevos, con el intervalo
del 95 % excluyendo el cero POR ARRIBA
```

Seis temporalidades por instrumento. Con dos instrumentos nuevos son doce
celdas: umbral de Bonferroni |z| > 2,87, y por el factor 1,1 de `BC_08`,
**|z| > 3,2** para cualquier celda distinta de la principal. La principal, H12,
se juzga por su intervalo, que está declarado de antemano.

## Qué cuenta como fracaso, y qué haremos entonces

Que el intervalo de H12 incluya el cero. En ese caso **el CRT se cierra**: se
habrán probado la especificación completa de bctrades, cuatro temporalidades de
ejecución, el reinicio, las confluencias, los horarios, la liquidez múltiple, y
el mecanismo del coste sobre instrumentos ciegos. No quedaría nada por mirar que
no fuera buscar hasta encontrar.

## Cuántos datos hacen falta

En H12 el CRT desnudo da **94 operaciones por instrumento y año**.

| efecto a detectar | z que se busca | n | instrumento-años |
|---|---|---|---|
| +0,10 R | 2,0 | 576 | **6,1** |
| +0,10 R | 2,5 | 900 | 9,6 |
| +0,08 R | 2,0 | 900 | 9,6 |

**El mínimo útil son 6 instrumento-años.** Un instrumento con seis años, o dos
con tres. Por debajo de eso la prueba no puede concluir nada y no vale la pena
hacerla.

## Qué instrumentos, y por qué esos

Se piden **dos**, elegidos para que se parezcan lo menos posible a los cinco que
ya están gastados:

- **XAUUSD (oro).** No es ni un par de divisas ni un índice de acciones. Rango
  grande respecto al spread, que es justo el régimen donde la aritmética del
  coste dice que el CRT debería vivir.
- **GRXEUR (DAX) o UKXGBP (FTSE).** Un índice que no sea estadounidense, para
  que la sesión que lo mueve sea otra.

Fuente: HistData, ficheros anuales de M1, 2020 a 2025.

**Estos dos instrumentos quedan reservados desde ahora.** No se miran, no se
grafican, no se exploran. Se corre el barrido una vez y se reporta.

---

# Enmienda · 2026-08-27, todavía sin datos

Se fija el alcance definitivo y los parámetros que aún quedaban sueltos. **Se
escribe antes de que los ficheros existan en el repositorio**, que es lo único
que hace que esto valga.

## Alcance

```
XAUUSD   2023 · 2024 · 2025
GRXEUR   2023 · 2024 · 2025      (DAX)
```

Seis instrumento-años, seis ficheros anuales de HistData. Potencia: n ≈ 564, el
intervalo del 95 % saldrá de ±0,099 R. Con un efecto verdadero de +0,10 R eso da
z ≈ 2,0. Es el mínimo que permite concluir, y se acepta de antemano que un
resultado de z entre 1,5 y 2,0 se reportará como **no concluyente**, no como
éxito.

## Conversión horaria — la misma que ya está validada

HistData entrega las marcas de tiempo en hora de Nueva York. `bt/check_tz.py`
comprobó empíricamente sobre EURUSD que llevan **horario de verano**, no EST
fijo. Se usa la misma conversión de `bt/load_pares.py`, sin excepciones:

```python
idx.tz_localize("America/New_York").tz_convert("UTC").tz_localize(None)
```

Si los ficheros nuevos no pasan la comprobación del hueco semanal, se dice y se
para. No se prueba otra conversión «a ver si sale mejor».

## Costes, declarados ahora

El coste es la variable de la que depende todo el resultado, así que no puede
elegirse después. Se fijan **por lo alto**, en contra de la hipótesis:

| instrumento | unidad | coste ida y vuelta | equivale a |
|---|---|---|---|
| XAUUSD | 0,01 USD | **35 unidades** | 0,35 USD de spread |
| GRXEUR | 1 punto | **2,0 puntos** | 2 puntos de spread |

Los dos están en el extremo caro de lo que cobra un bróker retail decente. Si
sale positivo con estos costes, saldría más positivo con los reales.

Junto a la neta se reportará el **coste que dejaría cada celda en cero**, que no
depende de esta elección y permite a cualquiera comparar con lo que pague.

## Qué está escrito y no se toca

- El anclaje: `ancla_ny = 1`, el mismo de todo el proyecto.
- La celda principal: **H12**.
- Una sola pasada. El resultado se publica entero, salgan las seis
  temporalidades como salgan.
- 2026 no entra. Si se descarga, se guarda cerrado para después.
