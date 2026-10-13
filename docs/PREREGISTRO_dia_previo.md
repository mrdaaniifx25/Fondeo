# Pre-registro · máximo y mínimo del día previo, disparo en M5/M15

Escrito y subido ANTES de medir. 20/09/2026. Idea del usuario:

> «marcar máximo y mínimo del día anterior, y en M15 o M5, si rompe el mínimo y
> vuelve dentro buscar compras, y si rompe el máximo y cierra dentro, ventas»

## Qué hay ya medido y por qué esto no es lo mismo

| ya medido | en qué se diferencia |
|---|---|
| `RESULTADOS_barrido_dia_fibo.md` | mismos niveles, pero la entrada es por retroceso de Fibonacci |
| `RESULTADOS_crt_temporalidad.md` | el nivel y el gatillo son de la **misma** temporalidad |
| `RESULTADOS_barrido_sesion.md` | el gatillo es M5, pero el nivel es de **sesión**, no del día |

Lo de aquí es **nivel de D1 con gatillo de M5/M15**. No está hecho.

## Cómo se mecaniza

- **Niveles**: máximo y mínimo del día natural anterior (día de mercado, UTC).
  Vivos desde las 00:00 del día siguiente hasta las 24:00 de ese mismo día.
- **Disparo**: una vela de M5 (o M15) cuyo **máximo supera el máximo del día
  previo y cuyo cierre vuelve por debajo** → venta. Espejo para compras.
- **Entrada**: al **cierre** de esa vela. La resolución empieza en el minuto
  siguiente.
- **Stop**: el extremo de esa misma vela (su máximo en ventas).
- **Un nivel, una operación**: cada nivel dispara como mucho una vez al día.

## Las 6 celdas, declaradas ahora

| eje | opciones |
|---|---|
| temporalidad del gatillo | **M5** · **M15** |
| objetivo | el **nivel opuesto** del día previo · **1:1** · **1:2** |

Tres instrumentos: EURUSD, oro, DAX. Se publican las 18 combinaciones.

## Cómo se mide

Resolución en M1, **las dos barreras por toque**, empate en el mismo minuto =
pérdida, horizonte 24 horas, agotarlo = pérdida. El objetivo tiene que estar
**por delante** del precio de entrada. Coste: EURUSD 1,43 pips · oro 0,35
unidades · DAX 1,6 puntos.

Lo que se mira es el **exceso sobre el precio justo** (`riesgo/(riesgo+recorrido)`),
no el acierto.

**Nulos** sobre la celda principal (M5, nivel opuesto, EURUSD): lados barajados
e instantes al azar.

## Criterio

1. exceso > 0 con el IC95 sin tocar el cero, **y**
2. neta > 0 con el IC95 sin tocar el cero, **y**
3. el mismo signo en al menos 2 de los 3 instrumentos.

## Predicción

Lo dejo escrito para poder fallar en público — llevo dos seguidas falladas.

- **Exceso entre −2 y +2 puntos** en las 18 celdas. Ninguna cumple el criterio.
- **La neta será mala, y peor en M5 que en M15**, porque el stop es el extremo
  de una vela de 5 minutos: espero un riesgo de **5-10 pips** en EURUSD, o sea
  un coste del **15-30 % del riesgo**. Es exactamente lo que hundió al barrido
  de sesión (coste 25,1 %, neta −0,26).
- **La variante de objetivo 1:2 tendrá el peor acierto** (~33 %) y la del nivel
  opuesto el mejor (~60-70 %), y las dos darán lo mismo en dinero.

Si me equivoco y sale algo, será en M15 y con el objetivo en el nivel opuesto,
que es donde el stop es más ancho.
