# Pre-registro · las familias clásicas de indicadores, en el panel largo

Firmado **antes** de correr `bt/indicadores.py`. Un solo pase.

## De dónde sale

Del final del curso de CRT, palabras del propio autor:

> *«todos los mejores traders, los que ganan la Robbins Cup Trading
> Championship, no utilizan ninguno de ellos métodos como este. Utilizan
> métodos más algorítmicos, más con indicadores, medias móviles, RSIs,
> MACDs, ATRs»*

El usuario pregunta lo obvio: **¿y montar una estrategia con eso?**

## Por qué no está contestado ya

Hay dos documentos cerca y ninguno responde:

- `RESULTADOS_ema_rsi.md` — EMA50 + RSI14 en H4/M15. Es **intradía**, donde el
  muro de coste es 0,1076 en EURUSD. Ahí no puede vivir nada.
- `RESULTADOS_tendencia.md` — ruptura Donchian, pero sobre **5 instrumentos** y
  con n = 86 y n = 50. Sin potencia para distinguir nada.

Lo que falta es lo evidente: las familias clásicas, **en diario, sobre el panel
de 26 series y 55 años**, que es donde el muro de coste baja de 0,1076 a 0,0226
(`RESULTADOS_muro_horizonte.md`). Es el único sitio donde la pregunta tiene
sentido, y es el mismo panel donde momento + carry sí midió positivo.

## Las doce señales, con parámetros de libro y sin tocar

Ninguna se ajusta. Son los valores por defecto de cada indicador.

| familia | regla |
|---|---|
| MM 50/200 | largo si SMA50 > SMA200 |
| MM 20/100 | largo si SMA20 > SMA100 |
| MM 10/50 | largo si SMA10 > SMA50 |
| MACD 12/26/9 | largo si línea MACD > señal |
| MACD 12/26 | largo si línea MACD > 0 |
| RSI 14 reversión | largo bajo 30, corto sobre 70, hasta cruzar 50 |
| RSI 14 momento | largo sobre 50, corto bajo 50 |
| Donchian 20 | largo al romper máximo de 20 días |
| Donchian 55 | Turtle: largo al romper máximo de 55 días |
| Canal ATR (Keltner) | EMA20 ± 2×ATR20 |
| **ROC 250** | referencia: momento a 12 meses, lo que ya funciona |
| ROC 20 | momento a 1 mes |

Panel: 22 divisas (Fed, desde 1971), oro, WTI, Brent, gas natural, S&P 500.
Rendimientos normalizados por volatilidad ex-ante de 36 días, sólo pasado.
Cartera = media diaria entre series vivas. **El estadístico va sobre los MESES**,
no sobre los días, para no inflar la n.

Coste: **0,02 unidades de ruido diario por cambio de posición**, que es el muro
diario medido en EURUSD (0,0226). Se informa también a 0,01 y 0,04.

## Contraste PRINCIPAL, declarado antes de mirar

**Efecto mensual NETO de cada una de las once familias clásicas**, y si alguna
supera a ROC 250 en neto. t sobre los meses.

## Predicción firmada

- Las **lentas** (MM 50/200, MM 20/100, Donchian 55, ROC 250) saldrán positivas
  en bruto, con t entre +2 y +5.
- Las **rápidas** (MACD, RSI momento, Donchian 20, ROC 20, canal ATR) saldrán
  cerca de cero en bruto y **negativas en neto**, por rotación.
- **RSI reversión** saldrá ≤ 0.
- **Ninguna superará a ROC 250 en neto.**
- Y la razón de fondo: **las lentas son momento con otro nombre.** Predigo
  correlación de señal > 0,6 entre MM 50/200 y ROC 250.

## Qué me refutaría

Que alguna familia clásica dé efecto neto positivo con t > +2 **y** correlación
de señal < 0,4 con ROC 250. Eso sería una fuente de ventaja distinta de la que
ya tenemos, y lo diría así.

## Controles obligatorios

1. **Placebo**: signos al azar con la misma rotación media.
2. **Comprar y mantener**: siempre largo, misma cartera.
3. **Rotación** (cambios por año) de cada familia, publicada junto al efecto.
4. **Correlación de señal** de cada familia con ROC 250.
5. Partición temporal 1971-1999 / 2000-2012 / 2013-2026.

Una sola pasada. Lo que salga se publica.
