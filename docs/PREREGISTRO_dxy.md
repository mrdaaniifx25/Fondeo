# Pre-registro · EUR/USD y DXY: confluencia, adelanto y divergencia

Firmado **antes** de correr `bt/dxy_eurusd.py`. Un solo pase.

## La objeción estructural, declarada antes de medir

El DXY **es** EUR/USD en un 57,6 %. Por construcción:

```
  DXY ∝ (EUR/USD)^-0,576 · (USD/JPY)^0,136 · (GBP/USD)^-0,119
      · (USD/CAD)^0,091 · (USD/SEK)^0,042 · (USD/CHF)^0,036
```

En logaritmos y con todas las series como «divisa por dólar»:

```
  Δlog DXY  =  -0,576 · Δlog EURUSD  +  0,424 · Δ NOEUR
```

Donde NOEUR es la cesta de yen, libra, dólar canadiense, corona sueca y franco.

**Eso significa que «mirar la confluencia EURUSD-DXY» es, en más de la mitad,
mirar EUR/USD dos veces.** Un filtro que exija «DXY bajando y EURUSD subiendo»
está pidiendo sobre todo que EUR/USD suba, que es la variable que ya está medida
y no lleva información.

La parte que **no** es tautológica es el 42,4 % restante: **NOEUR**. Ahí sí hay
información distinta, porque viene de otras cinco divisas. Toda la investigación
seria de esta idea consiste en aislar ese residuo.

## Datos

Las seis componentes del DXY, series diarias de la Reserva Federal
(`data/ext/fx_daily.csv`), **1999-2026**, 7.225 días para el euro. Se reconstruye
el DXY con sus pesos oficiales.

**Limitación declarada**: no tengo DXY intradía, sólo EUR/USD, oro y DAX en M1.
Así que esto se mide en **diario**, que es la prueba *generosa*: el muro de coste
en diario es 0,0226 contra 0,1076 en una hora (`RESULTADOS_muro_horizonte.md`).
Si no hay nada donde el muro es veinte veces más bajo, en intradía no lo hay.

## Las siete pruebas

1. **La identidad mecánica**: correlación y R² de Δlog EURUSD contra Δlog DXY.
   Cuánto de DXY *es* EUR/USD.
2. **Adelanto-retraso**: correlación cruzada de Δlog EURUSD en t+k contra
   Δlog DXY en t, para k de −10 a +10 días.
3. **El residuo**: `res = Δlog DXY + 0,576·Δlog EURUSD` (= 0,424·ΔNOEUR).
   ¿Predice el movimiento futuro de EUR/USD a 1, 5 y 20 días?
4. **La cesta NOEUR directamente**: su momento a 1, 5, 20 y 60 días, ¿predice
   EUR/USD?
5. **Divergencia SMT en diario**: EUR/USD hace máximo de 20 días y DXY **no**
   hace mínimo de 20 días (y al revés). Rendimiento posterior.
6. **Reversión del diferencial**: z del residuo acumulado, ¿vuelve a la media
   más de lo que cuesta esperarlo?
7. **Operable**: la mejor señal de 3-6 convertida en reglas con coste real, y
   partición 1999-2012 / 2013-2026.

## Método, para no repetir mis errores

- **Rendimientos futuros a k días SIN solape**: se muestrea un día de cada k.
  Es el error que cometí en `RESULTADOS_espacio.md` y que infló t de +0,89 a
  +3,57.
- **Todo desplazado**: ninguna señal usa el dato del día que predice.
- **Control proporcional** en la prueba 5, no contra cero
  (`RESULTADOS_reloj.md`).
- **Placebo de etiquetas barajadas** en cada prueba con señal.

## Contraste PRINCIPAL, declarado antes de mirar

**Prueba 3**: t del residuo de DXY (la parte no-euro) prediciendo el rendimiento
de EUR/USD a 5 días, sin solape, muestra completa.

## Predicción firmada

- **Prueba 1**: correlación entre −0,93 y −0,99. R² por encima de 0,88.
- **Prueba 2**: todos los coeficientes de adelanto ≈ 0, |t| < 2 en los veinte.
- **PRINCIPAL (prueba 3)**: **t entre −2 y +2. No significativo.**
- **Prueba 4**: la cesta NOEUR tampoco predice; |t| < 2 en los cuatro plazos.
- **Prueba 5**: la divergencia no supera su control proporcional.
- **Prueba 6**: el residuo acumulado será casi un paseo aleatorio; la reversión
  que haya no cubrirá el coste.

## Qué me refutaría

|t| > 2 en el contraste principal **con el mismo signo en las dos mitades
temporales** y superando el placebo barajado. Eso sería una fuente de
información genuinamente distinta y lo diría así.

Una sola pasada. Lo que salga se publica.
