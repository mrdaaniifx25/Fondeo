# El indicador · cómo ponerlo y cómo configurar la alerta

Archivo: `pine/mean_reversion_m15.pine` · Pine v6 · 215 líneas.
Reglas: `docs/MEAN_REVERSION_REGLAS.md`.

---

## Ponerlo

```
  1  TradingView -> EURUSD -> temporalidad 15 minutos
  2  Abajo, pestaña "Editor Pine"
  3  Borra lo que haya, pega el archivo entero, "Guardar" y "Añadir al gráfico"
```

Te dibuja la EMA 20 (naranja), las dos bandas (gris), un triangulito en cada
vela de señal, una etiqueta **C** o **V** en la vela de entrada, y las tres
líneas de la operación viva: entrada (azul), stop (rojo), objetivo (verde).

Arriba a la derecha, una tabla con el estado, **las pérdidas seguidas de hoy**,
las operaciones del día, los tres niveles y **los lotes ya calculados**.

Cuando llevas 2 pérdidas seguidas, **el fondo del gráfico se pone rojo**. Eso
significa: cierra la plataforma hasta mañana.

## La alerta

```
  1  Botón del reloj (Alertas) -> "Crear alerta"
  2  Condición: "Reversion a la media · M15"
  3  Elige una:
       "COMPRA · reversion a la media"
       "VENTA · reversion a la media"
       "COMPRA o VENTA"          <- la que yo pondría, una sola alerta
  4  >>> Frecuencia: "Una vez por barra"  <<<
       NO pongas "Una vez por cierre de barra".
  5  Notificaciones: app del móvil, y correo si quieres.
```

### Por qué «una vez por barra» y no «al cierre»

Porque **la entrada es en la apertura de la vela**. La señal ya está decidida
cuando esa vela abre —se calcula con la vela anterior, que está cerrada— así
que el aviso tiene que llegarte al abrir, no 15 minutos después. Si pones
«al cierre de la barra» llegas tarde a todas.

### Si quieres los niveles en el mensaje

En el paso 2, en vez de elegir una condición, elige **«Cualquier llamada a la
función alert()»**. Entonces el aviso llega así:

```
  COMPRA EURUSD  entrada 1.08432  stop 1.08282  objetivo 1.08610 (17.8 pips)  lotes 0.78
```

Y además te avisa cuando el día se cierra por las 2 pérdidas.

## Dos cosas que tiene dentro y no se ven

**1 · La corrección de la desviación típica.** `ta.stdev` de Pine usa la
desviación **poblacional**; mi backtest usa la **muestral** (pandas, ddof=1). Sin
corregirlo las bandas salen un **2,6 % más estrechas** y las señales no son las
mismas que medí. El script multiplica por `sqrt(n/(n-1))`. Si alguna vez lo
comparas con un Bollinger normal de TradingView, verás que el mío va un pelo
más ancho: es a propósito.

**2 · No repinta.** Todo se decide con `[1]`, o sea con la vela ya cerrada, y la
entrada es el `open` de la actual. No hay ni un dato del futuro. Los empates de
stop y objetivo en la misma vela se resuelven como **pérdida**, igual que en el
backtest, para no inflar nada.

## Ajustes que puedes tocar

Todo está en la rueda de configuración. Los que importan:

```
  Stop (pips)                     15      medido. No lo bajes a 8 ni lo subas a 30.
  Parar el dia tras N perdidas     2      la regla que vale 41 puntos. No la quites.
  Riesgo por operacion (%)       1,00     a 1,50 % el 94,8 % de las cuentas mueren.
  Capital de la cuenta          10000     cámbialo y los lotes se recalculan solos.
  Valor del pip por lote           10     en EURUSD con cuenta en dólares.
  Tamaño del pip               0,0001     0,01 si algún día lo usas en un par con yen.
```

## Lo que el indicador NO hace

- **No abre operaciones.** Te avisa y te da los niveles; las metes tú.
- **No sabe tu coste real.** Mide el tuyo antes de operar: abre una compra
  mínima, ciérrala al instante, apunta la pérdida en pips, cinco veces a
  distintas horas. Por encima de 0,7 pips esto pierde dinero.
- **No tiene ventaja.** Neto medido −0,090 pips por operación. Lo que aporta es
  la gestión: 38,1 % de pasar las dos fases con 0,0 % de muerte por límite
  diario. No lo operes creyendo otra cosa.

## Si da error al compilar

No tengo TradingView en este entorno, así que el script está revisado a mano y
comprobado mecánicamente (paréntesis, ámbitos, orden de bloques), pero no
compilado. Si sale un error, **pásame el texto exacto y la línea** y te lo
arreglo en el momento.
