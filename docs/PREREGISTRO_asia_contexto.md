# Preregistro · el contexto de M15 y H1

Escrito el 28 de agosto de 2026, antes de ejecutar nada. Una sola pasada.

## De dónde sale

El usuario lo ha dicho tres veces, la última sin que se lo preguntara:

> «hay que ver un poco del contexto hacia dónde va y hacia dónde está yendo el
> precio, y no entrar simplemente con eso, sino mirar de acompañar al precio por
> el contexto y temporalidades mayores, ya sea M15 o H1» (N09)

Y antes, en T05: *«podría ser que la parte bajista forme parte de un pequeño
retroceso dentro de un movimiento alcista, eso también hay que tenerlo en
cuenta»*.

Es la única de sus tres hipótesis que no se ha probado.

## La variable

Sobre la muestra ya fijada de `bt/asia_nivel.py`. No se genera ninguna
operación nueva.

- `dirH1` = signo de (cierre de la última vela H1 cerrada − cierre de la vela H1
  cuatro barras antes). Cuatro horas de dirección.
- `dirM15` = lo mismo con cuatro velas de M15. Una hora de dirección.
- `a favor` = el lado de la operación coincide con el signo.

## Contrastes: tres, y ya está

1. M15 a favor menos M15 en contra.
2. H1 a favor menos H1 en contra.
3. Las dos a favor menos el resto.

**Predicción firmada: las tres diferencias serán positivas.**

Con tres contrastes, Bonferroni pide |z| >= 2,39 para dar por bueno cualquiera.

**Datos.** Principal: 2020-2025. Secundaria: enero-mayo de 2026. Agosto no
cuenta. Unidad: el día. Coste 1,43 pips.
