# Pre-registro · carry en divisas

Escrito y subido ANTES de medir. 22/09/2026.

## De dónde sale

`RESULTADOS_momento_largo.md` demostró dos cosas: que a horizonte mensual el
coste se lleva el **1,1 %** del efecto en vez de comérselo entero, y que el
momento temporal, aunque real (t +5,04 sobre 632 meses), lleva **trece años
apagado** (Sharpe 2010s +0,17, 2020s +0,14).

El **carry** es el otro premio grande documentado en divisas, y el que —según
todo lo que se ha publicado— **no se ha degradado igual**. Es el siguiente de la
lista de cuatro.

## El problema de datos, y cómo se resuelve

Carry de manual = diferencial de tipos de interés. **No hay serie de tipos de
interés de 20 países accesible**: la política de red sólo deja pasar GitHub, y
ahí sólo está el bono a 10 años de EE. UU. Ni api.github.com pasa (403).

Lo que sí hay es **inflación anual por país, 1960-2024, Banco Mundial**.

Y eso sirve, por la relación de Fisher: el tipo nominal es aproximadamente el
tipo real más la inflación esperada. **Entre países, la mayor parte de la
diferencia de tipos nominales es diferencia de inflación.** Brasil o Sudáfrica
pagan el 10 % porque tienen el 8 % de inflación; Suiza o Japón pagan el 0 %
porque no la tienen.

**Se declara ahora que es un sustituto, no el dato.** Sus tres defectos:

1. Los tipos reales también difieren entre países, y eso no lo recoge.
2. Es **anual**, no mensual.
3. Donde hay control de capitales, el tipo no refleja la inflación.

Los tres **atenúan** el efecto, no lo fabrican. Si aun así sale, es a pesar del
sustituto, no gracias a él.

## Qué se mide

**Universo**: 20 divisas contra el dólar (las 22 del Fed menos Venezuela, que ya
estaba fuera por hiperinflación, y menos Taiwán, que el Banco Mundial no cubre).
Serie diaria del Fed desde 1971, a cierre mensual. Todas normalizadas a
**«moneda extranjera por dólar»**, de modo que subir = la divisa se debilita.

**La señal**, para el año Y:

```
c_i  =  inflación del país i en el año Y-2  -  inflación de EE. UU. en el año Y-2
```

**Y-2 y no Y-1**: la inflación anual del año Y-1 se publica a principios de Y,
así que usar Y-2 elimina cualquier duda sobre qué se sabía cuándo. Es deliberadamente
conservador.

**El rendimiento mensual** de estar largo en la divisa i, financiado en dólares:

```
r_i  =  c_i/12   -   Δlog(moneda por dólar) × 100
        ───────       ──────────────────────────
        el interés    lo que se deprecia
        que cobras    contra ti
```

Esto es exactamente el contraste de la **paridad descubierta de tipos**: la
teoría dice que la divisa de tipo alto se deprecia justo lo que paga de más, y
que por tanto esto vale cero. El premio del carry documentado es que **se
deprecia menos**. Eso es lo que se mide.

**El contraste PRINCIPAL, declarado ahora**: carry **transversal** — cada mes,
largo el tercio de divisas con mayor `c_i` y corto el tercio con menor `c_i`,
escalado por la volatilidad de 36 meses anteriores, muestra completa.

Secundarios: la versión temporal (signo de `c_i`), y el tercio contra tercio sin
escalar por volatilidad.

### La corrección estadística, igual que antes

Cada mes se promedia en **un solo número de cartera** y el estadístico va sobre
los **meses**, no sobre las filas. Las divisas están correlacionadas entre sí y
sobre las filas el error estándar sale falsamente pequeño.

### Coste, y el recargo del bróker

La señal cambia una vez al año, así que el coste de operar es casi nulo: se
carga igual **0,01 en unidades de ruido por cambio de posición**.

Pero hay un coste que sí importa y que se declara ahora: **un bróker minorista
no te paga el diferencial interbancario.** Le mete un recargo. Se publican dos
versiones: sin recargo, y con **1,5 puntos porcentuales anuales** restados a
cada pata, que es lo que se suele ver en CFD.

### El riesgo que define esta estrategia

El carry es famoso por su forma: gana poco y constante durante años y pierde
mucho de golpe. Por eso se declaran ahora, y se publicarán salga lo que salga:
**asimetría, peor mes, y peor caída acumulada.** Con su límite del 10 %, eso
puede ser más decisivo que la media.

### Placebos

1. señales aleatorias · 2. señal invertida · 3. señales barajadas entre divisas
   dentro del mismo mes

### Partición temporal, fijada antes

**1971-1999 · 2000-2012 · 2013-2026**, los mismos cortes que en el momento.

## Criterio

1. El principal con **t > 2** sobre los meses, **y**
2. positivo en los tres subperiodos, **y**
3. sigue positivo con el recargo de 1,5 puntos, **y**
4. placebos planos, **y**
5. la peor caída, al tamaño que respeta su límite, **no pasa del 10 %**.

El quinto es nuevo y es el que decide si esto le sirve a él o sólo es cierto.

## Predicción

- **El principal saldrá positivo con t entre 3 y 5.** El carry es el premio más
  robusto de divisas y el sustituto de inflación debería recoger el grueso.
- **Aguantará mejor que el momento en 2013-2026**, pero también más flojo que
  en los ochenta y noventa.
- El recargo de 1,5 puntos se llevará **una parte grande**: el diferencial medio
  entre tercios en divisas desarrolladas es de unos 3-4 puntos, así que quitar
  1,5 de cada pata puede dejarlo en la mitad.
- **La asimetría saldrá negativa y el peor mes será feo** — espero entre −3 y
  −6 veces la desviación mensual.
- **El criterio 5 fallará**: al tamaño que da dinero, la caída pasará del 10 %.
  Ésa, y no la media, será la razón por la que esto no le sirva tal cual.

Van once predicciones con errores. Ésta también puede fallar.
