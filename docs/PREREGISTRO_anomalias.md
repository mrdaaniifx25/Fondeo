# Preregistro · anomalías de calendario y de horario, de la literatura

Sellado ANTES de medir. Un solo pase. Código en `bt/anomalias.py`.

## Por qué salgo de todo lo que él me ha pasado

Dos meses midiendo métodos de traders (SMC, ICT, CRT, order blocks, rango
asiático, el grupo del NASDAQ) han dado siempre lo mismo: ventaja bruta del
tamaño del coste. Todos esos métodos comparten un defecto: **nadie los ha
publicado con datos**, así que no hay forma de saber si el patrón existía
antes de que alguien lo dibujara en un gráfico.

Aquí pruebo lo contrario: efectos **publicados en revistas académicas, con
décadas de datos y revisión por pares**, que este proyecto no ha tocado nunca.
Si algo tiene que funcionar, es más probable que sea esto.

Las fuentes que fijan las hipótesis:

  · Boyarchenko, Larsen & Whelan, *The Overnight Drift*, Federal Reserve Bank
    of New York Staff Report 917 / Review of Financial Studies 36(9), 2023.
    Casi el 100 % de la prima de riesgo de la bolsa americana se gana entre
    las 02:00 y las 03:00 hora de Nueva York, cuando abre Europa. 3,6 %
    anualizado entre 1998 y 2019.
  · Liberty Street Economics (NY Fed), *The Disappearing Overnight Drift*,
    julio de 2026. Los mismos autores: esa ventana **lleva en cero desde
    2021**.
  · Ariel (1987), Lakonishok & Smidt (1988), McConnell & Xu (2008), y
    revisiones hasta 2025: efecto **cambio de mes**.

## Las cuatro hipótesis, firmadas y con dirección

Instrumentos: NASDAQ, SP500, GER40. Sesión de contado de Nueva York
(09:30-16:00 NY) para los americanos, Fráncfort (09:00-17:30) para el GER40.

### H1 · la noche gana y el día no

`cierre -> apertura siguiente` frente a `apertura -> cierre`.

**Predicción: la noche bate al día en al menos +0,02 % diario, con z ≥ +2 en
el agregado de los tres índices, y el tramo de día es plano o negativo.**

### H2 · la ventana de 02:00-03:00 NY está MUERTA

**Predicción: positiva y significativa en 2020-2021, e indistinguible de cero
en 2022-2026.** Es una predicción EN CONTRA de una estrategia. Si sale viva,
me he equivocado a favor del usuario y hay que decirlo.

### H3 · cambio de mes

Último día de negociación del mes más los tres primeros del siguiente,
frente al resto.

**Predicción: positiva, z ≥ +2 en el agregado.**

### H4 · la noche revierte los desplomes

El mecanismo que documenta el paper es el desequilibrio de órdenes al cierre
americano. La noche que sigue a un día BAJISTA debería rendir más que la que
sigue a un día alcista.

**Predicción: diferencia ≥ +0,05 % diario a favor de la noche post-caída.**

## Placebos

Las mismas cuatro pruebas en **EURUSD** y **XAUUSD**. El mecanismo es de renta
variable: prima de riesgo e inventario de los creadores de mercado al abrir
Europa.

**Predicción: H1 y H4 NO aparecen en divisa ni en oro.** Si aparecen, lo que
estoy midiendo es un artefacto de cómo he definido las sesiones y no vale
nada. Esto es el control, y manda sobre todo lo demás.

## Contabilidad de comparaciones múltiples

4 hipótesis x 3 índices = **12 contrastes**, más 4 agregados. Con 12
contrastes independientes, `E[max |z|] ≈ 2,25`, y `P(algún z ≥ 2,58) = 26 %`.
**Para declarar algo vivo exijo z ≥ 3,0 en el agregado Y el mismo signo en
los tres índices Y ausencia en los dos placebos.** Las tres cosas.

## El coste, que aquí es la trampa

La prima nocturna es, en parte, compensación por financiación. Un CFD largo
paga interés cada noche. Mido el efecto BRUTO y luego le resto la
financiación a tres tipos: 3 %, 6 % y 9 % anual sobre el nocional.

**Si el efecto no sobrevive al 6 %, no es operable en CFD y hay que decirlo.**
