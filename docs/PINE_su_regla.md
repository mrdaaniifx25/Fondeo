# El indicador de su regla · qué dibuja y cómo se ha verificado

`pine/su_regla_historico.pine`. Marca **todas** las señales de su regla en el
histórico, sin filtrar nada por defecto.

## La regla, exacta

Es la que está medida en `bt/su_regla_instrumentos.py`, sin cambiar una coma:

```
cuerpo de la ÚLTIMA vela de M5 cerrada  ->  min(apertura, cierre) y max(apertura, cierre)
cierre de una M1 por encima del cuerpo  ->  compra
cierre de una M1 por debajo del cuerpo  ->  venta
stop      = extremo de los últimos 10 minutos, incluida la vela de entrada
objetivo  = 1:2
no se repite señal del mismo lado antes de 4 minutos
ventana   = 08:00-11:30 hora de Madrid
lo que no resuelve dentro de la ventana se cierra a mercado
```

## La auditoría

Esta rama se llama `pine-script-zero-trades-audit` por algo: aquí ya ha habido
scripts que salían con cero señales y nadie se enteraba. Así que la lógica se
reimplementó **barra a barra, con el mismo estado `var` y el mismo orden de
ejecución que usa Pine**, y se diffeó contra el backtest sobre agosto de 2026.

```
referencia (bt/su_regla_instrumentos.py)    734 señales
simulación del script                       734 señales
faltan 0 · sobran 0
coinciden en día, hora, lado, entrada y stop:  729 de 734
```

Las 5 diferencias son **sólo de stop** y todas caen en 08:05-08:07. El backtest
recorta la mirada de 10 minutos al inicio de la ventana; el script usa
`ta.lowest`/`ta.highest`, que ven los diez minutos reales incluidos los previos
a las 08:00. El script es el que coincide con lo que se ve en pantalla.

Dos errores encontrados y corregidos durante la revisión, por si vuelven a
aparecer en otro script:

1. **El bloque que resolvía las operaciones estaba antes del que las crea**, así
   que una señal podía cerrarse contra su propia vela de entrada. Es mirar al
   futuro. Ahora se resuelve primero y se crea después, igual que el backtest
   empieza a buscar en `k+1`.
2. Sentencias encadenadas con coma (`a := 1, b := 2`), `+=`, y llamadas de
   método sobre `box`/`line`. Sintaxis que no compila.

## Lo que se ve al ponerlo

**La regla dispara unas 35 veces al día. Usted toma de una a tres.**

Esa es la lectura, y no aparece en ninguna tabla del repositorio. Su operativa
no es la regla: es **su selección sobre la regla**, y eso sigue sin medirse
(`PREREGISTRO_criterio.md`, escrito y nunca ejecutado).

Los números de la regla a ciegas, EURUSD 2020-2026, ventana 08:00-11:30:

| | n | acierto | geometría | bruta | coste | neta |
|---|---|---|---|---|---|---|
| todas | 70.381 | 31,3 % | 33,3 % | −0,060 | 0,386 R | **−0,446** |
| stop ≥ 15 p | 987 | 26,6 % | 33,3 % | −0,201 | 0,078 R | **−0,279** |

Stop mediano 4,6 pips; el coste se lleva el 38,6 % del riesgo.

## Sobre el deslizador de stop mínimo

Está puesto en 0 por defecto, a propósito.

Le recomendé un mínimo de 15 pips antes de comprobar qué le hacía eso a **esta**
regla en concreto. Lo que le hace es esto: sobrevive el **2,4 %** de las señales
—2.055 de 85.883— y el acierto cae del 31,3 % al 26,6 %. En los cuatro días de
agosto verificables al minuto, de 197 señales no pasa **ninguna**.

Baja el peaje del 38,6 % al 7,8 %, sí, pero la bruta empeora más de lo que el
coste mejora. **No hay ningún valor del deslizador que cruce el cero**, y eso es
justo lo que hay que ver moviéndolo.

La corrección era mía y estaba mal planteada: el problema del stop estrecho es
real, pero no se arregla poniendo un mínimo sobre una regla cuya ventaja bruta
ya es negativa. Un stop más ancho reduce una fuga; no fabrica ventaja.
