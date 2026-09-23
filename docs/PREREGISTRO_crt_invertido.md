# Preregistro · el CRT al revés

Escrito el 28 de agosto de 2026, antes de ejecutar. Una sola pasada.

## Por qué este sí merece la prueba y el de la cascada no

La regla general es que darle la vuelta a una estrategia sólo funciona si su
ventaja bruta es **más negativa que el coste**. En la cascada la bruta era
**+0,096** con un coste de 0,326 R: invertirla no podía salir.

El CRT es el único caso del proyecto donde eso no está claro de antemano:

```
  R bruta/op   -0,0686
  coste/op      0,0778 R   (stop mediano 19,3 pips, el mejor del proyecto)
```

La bruta es negativa, y el coste es pequeño porque los stops son cuatro veces
mayores que en todo lo demás. Está en el filo: −0,0686 contra −0,0778. Por eso
hay que medirlo en vez de razonarlo.

## Especificación

Sobre las 1.343 operaciones ya fijadas de `data/trades_crt_base.csv`. No se
genera ninguna señal nueva.

- **Entrada**: el mismo precio y el mismo instante.
- **Lado**: el contrario.
- **Stop**: espejo del original respecto a la entrada, misma distancia en pips.
- **Objetivo**: espejo del original, mismo rr.
- **Horizonte**: 5 días naturales desde la entrada. Se informa lo que no resuelva.
- **Coste**: 1,43 pips. **Unidad**: el día, con suma diaria.

## Contraste, uno solo

Suma neta por día de la versión invertida, 2020-2025.

**Predicción firmada: será negativa.** Es decir, predigo que **no** funciona,
porque −0,0686 no es más negativo que −0,0778. Si sale positiva y con fuerza,
me he equivocado y hay que mirarlo en serio.

**Muestra secundaria**: 2026 enero-julio.
