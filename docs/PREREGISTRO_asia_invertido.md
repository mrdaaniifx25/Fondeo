# Preregistro · dar la vuelta a los disparos con el contexto en contra

Escrito el 28 de agosto de 2026, antes de ejecutar. Una sola pasada.

## De dónde sale

Del resultado preregistrado del contexto (`docs/RESULTADOS_asia_contexto.md`):

```
2020-2025            n      %TP     R/op
  M15 y H1 a favor  1.454   34,9%   +0,071
  el resto            626   21,2%   -0,355     PF neto 0,24
```

Los 626 disparos con el contexto en contra pierden mucho más de lo que la
geometría permite: 21,2 % cuando un 1:2 al azar da 33,3 %. Hasta ahora sólo los
hemos **descartado**. La pregunta natural, y la única que queda sin probar en
esta familia, es si conviene **tomarlos del revés**.

Ojo con lo que significa mecánicamente: si la regla compra en el alto de Asia
mientras H1 baja, darle la vuelta es **vender en el alto de Asia con H1 bajando**
— o sea, operar a favor de H1 en el nivel. No es una rareza estadística, es una
operación con sentido.

**No es automático.** Perder el 79 % de las veces con un 1:2 no implica que el
contrario gane el 79 %: la operación invertida tiene su propio stop, su propio
objetivo y su propia geometría de 1/3. Hay que medirlo.

## Especificación

Sobre la muestra ya fijada de `bt/asia_nivel.py`, subconjunto `~(favM15 & favH1)`.
No se genera ningún disparo nuevo.

- **Lado**: el contrario al de la regla.
- **Entrada**: el mismo precio y el mismo instante.
- **Stop**: la misma distancia en pips que el original, al otro lado.
- **Objetivo**: 2 veces esa distancia, en el nuevo sentido.
- **Horizonte**: hasta las 22:00 del mismo día. **Coste**: 1,43 pips.
- **Unidad**: el día, y se informan las dos métricas — media diaria y **suma
  diaria**, que es la que se cobra.

**Contraste principal, uno solo:** suma neta por día de la versión invertida,
en 2020-2025.

**Predicción firmada: será positiva.**

**Muestra secundaria:** enero-mayo de 2026, sin tocar.

**Umbral:** un solo contraste con dirección firmada, |z| >= 1,96 con el signo
predicho. Si sale al revés o sin fuerza, la idea cae y se dice.

## Lo que no arregla aunque salga

Sigue siendo un subconjunto de los 626, o sea unos 100 disparos al año. Aunque
salga rentable, hay que mirar cuánto da en euros antes de llamarlo estrategia.
