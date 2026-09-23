# Resultados · carry en divisas, y la mezcla con el momento

Pre-registro: `docs/PREREGISTRO_carry.md`, subido en `f108653` **antes** de
medir. Código: `bt/carry.py` y `bt/cartera_mixta.py`. **20 divisas, 623 meses,
1971-2026.**

## Veredicto

El carry **cumple el criterio principal**, y es el **segundo** resultado del
proyecto que lo hace. Lo importante no es eso: es que **el carry y el momento
se hunden en momentos distintos**, y juntos dan algo que ninguno da por separado.

## El contraste principal, declarado antes

```
  sin recargo                     meses 623  efecto +0.0352 [+0.0137,+0.0567]  t +3.21  Sharpe +0.45
  con recargo de 1,5 puntos/año   meses 623  efecto +0.0324 [+0.0109,+0.0539]  t +2.95  Sharpe +0.41
```

El recargo del bróker se lleva el **8 %**, no la mitad como predije.

Placebos, limpios:

```
  1 · señales aleatorias                efecto -0.0092   t -0.99    plano
  2 · señal invertida                   efecto -0.0359   t -3.27    espejo
  3 · señales barajadas entre divisas   efecto -0.0023   t -0.27    plano
```

El tercero es el que importa: barajar **qué** divisa recibe cada señal mata el
efecto entero. O sea que esto no es un factor común, es **elegir la divisa
correcta**.

## Y aquí está la sorpresa

```
                     carry              momento (de RESULTADOS_momento_largo)
  1971-1999   t +0.72  Sharpe +0.14        t +5.23  Sharpe +1.03
  2000-2012   t +4.11  Sharpe +1.14        t +1.76  Sharpe +0.49
  2013-2026   t +2.51  Sharpe +0.70        t +0.91  Sharpe +0.25
```

**Están invertidos.** El momento funcionó hasta 1999 y se apagó; el carry no
funcionaba entonces y funciona ahora. El carry con recargo en 2013-2026 da
**t +2,46**: es lo primero en todo el proyecto que es significativo en el
periodo reciente.

## La forma del riesgo, que es lo que casi lo mata

```
  asimetría -5.14   peor mes -3.867 (-14.1 desviaciones)   peor caída -6.44
```

**Menos catorce desviaciones en un mes.** Los cinco peores:

```
    1994-01   -14.1 σ     1991-07    -4.0 σ
    1976-11    -4.6 σ     1984-07    -3.8 σ
```

Enero de 1994 es la **devaluación administrada del yuan**: China movió el tipo
de 5,8 a 8,7 de un día para otro. No es una caída de mercado, es un decreto. Y
no era operable por un minorista.

### Sólo el G10 — esto NO estaba pre-registrado, es exploratorio

Las diez divisas que él sí puede operar en una cuenta fondeada:

```
  G10 · completa, con recargo   t +2.79  Sharpe +0.39   asimetría -0.92   peor mes -6.4σ
  G10 · 1971-1999               t +0.74
  G10 · 2000-2012               t +3.15
  G10 · 2013-2026               t +1.19        <- ya no llega
  G10 · placebo barajado        t +0.92        limpio
```

La asimetría pasa de −5,14 a **−0,92** y el peor mes de −14,1σ a −6,4σ: quitando
las divisas con anclaje, el carry deja de ser una bomba. Pero **la fuerza del
periodo reciente se va con ellas**: en el G10, los últimos trece años dan t +1,19.

## Lo que de verdad importa: los dos juntos

Mitad y mitad. **Sin optimizar nada** — no hay ningún parámetro que elegir, son
las dos series ya medidas a igual peso.

```
  correlación entre momento y carry: -0.28

                    t      Sharpe   asimetría   peor mes   peor caída   €/mes
  momento solo    +5.11    +0.71      +0.04      -5.5 σ      -5.70       +94
  carry solo      +2.95    +0.41      -5.14     -14.1 σ      -6.44       +25
  MEZCLA 50/50    +6.70    +0.93      -0.31      -4.2 σ      -1.60      +219
```

Mira la columna de la peor caída: **de −5,70 y −6,44 a −1,60**. No es que la
mezcla gane más por operación — es que **no se hunden a la vez**, así que la
caída conjunta es una cuarta parte, y eso permite operar cuatro veces más grande
con el mismo límite del 10 %.

Y la asimetría de −5,14 del carry se queda en **−0,31**: la pata de momento
gana justo en las crisis en las que el carry revienta. Es el resultado clásico y
aparece limpio.

```
  mezcla 1971-1999   t +5.77   Sharpe +1.13   ->  +332 €/mes
  mezcla 2000-2012   t +3.37   Sharpe +0.93   ->  +244 €/mes
  mezcla 2013-2026   t +1.88   Sharpe +0.52   ->  +120 €/mes
```

Los euros son sobre **50.000 €**, escalando para que **la peor caída de la
historia sea exactamente el 10 %**.

**Advertencia de dimensionado**: la peor caída futura casi siempre supera a la
peor caída pasada. Lo prudente es la mitad de esa escala, y entonces la muestra
completa da **110 €/mes** y el tramo reciente **60 €/mes**.

## Contra el criterio pre-registrado

| criterio | resultado |
|---|---|
| 1. principal con t > 2 | **SÍ**, t +3,21 |
| 2. positivo en los tres subperiodos | **SÍ**: +0,013 · +0,076 · +0,038 |
| 3. sigue positivo con el recargo | **SÍ**, t +2,95 |
| 4. placebos planos | **SÍ**, los tres |
| 5. la peor caída no pasa del 10 % al tamaño que da dinero | **NO**, como predije |

El quinto falla para el carry solo. **Para la mezcla, deja de fallar**: a la
escala del 10 % da 219 €/mes, y ese 10 % es el límite, no una estimación.

## Récord de predicciones

Tres de cinco.

| predicción | resultado |
|---|---|
| principal positivo con t entre 3 y 5 | t +3,21 ✔ |
| aguantará mejor que el momento en 2013-2026 | +2,51 contra +0,91 ✔ |
| el recargo se llevará la mitad | se lleva el 8 % ✘ |
| peor mes entre −3 y −6 desviaciones | −14,1 σ ✘ (y es un decreto, no un mercado) |
| el criterio 5 fallará | falla ✔ |

## Dónde deja esto el proyecto

Tres meses midiendo patrones de gráfico intradía: **cero**, y ahora se sabe por
qué — ahí el peaje vale lo mismo que el premio.

Dos semanas en el horizonte mensual: **dos efectos reales, medidos, con placebos
limpios, que se complementan.** t +6,70 sobre 623 meses.

Y el número que importa: al tamaño que respeta su límite del 10 %, esto da
**entre 110 y 219 € al mes sobre 50.000 €**. No son 750.

La diferencia ya no es la estrategia. Es el capital: **para 750 € al mes harían
falta entre 170.000 y 340.000 € fondeados**, según se use la muestra completa o
sólo los últimos trece años.

Eso es una conversación distinta a la de los tres meses anteriores, y es la
primera que se puede tener con números.
