# Los dos `.ex4` de «CRT Turtle Soup»

Le llegan en una formación gratuita, con la petición de verificarlos y de tener
la versión para TradingView.

## Qué son, exactamente

```
CRT_Turtle_Soup_v7.ex4   174.233 bytes   md5 9e21cee6a3d40b27f4d03f11b43dae87
CRT_Turtle_Soup_v8.ex4   171.927 bytes   md5 cc8f1751c889ea813d8f6f7fa3630fd0
cabecera  45 58 2d 04   ->  "EX-" formato .ex4 moderno (MT4 build 600+)
entropía  7,99 bits/byte  ->  cuerpo comprimido/cifrado
```

**No son de MT5.** `.ex4` es MetaTrader **4**; MT5 usa `.ex5`. En MT5 no cargan.

Lo único legible en los dos ficheros son dos cadenas idénticas:

```
Copyright 2026, https://www.youtube.com/tradingforextv
https://www.youtube.com/tradingforextv
```

Todo lo demás está comprimido. **No se puede leer la lógica**, ni por mí ni por
nadie sin un descompilador —que además va contra los términos de MetaQuotes—.

Lo que sí se puede decir:

- **No aparecen importaciones de DLL en claro** (`kernel32`, `wininet`, `urlmon`,
  `user32`, `shell32`: cero apariciones), ni más URLs, ni cadenas de licencia o
  caducidad. **Pero eso no certifica nada**: con el cuerpo comprimido, la ausencia
  de esas cadenas en claro no prueba que no estén dentro.
- **v7 y v8 comparten el 0,8 % de los bytes.** Son compilaciones distintas y no
  se puede saber qué cambió entre una y otra.

### Se intentó abrirlos, y no se puede

Por si alguna sección estuviera solo comprimida y no cifrada, se buscaron
cabeceras de zlib, gzip, bz2 y lzma en los dos ficheros y se intentó
descomprimir desde cada una. Salen 18-19 candidatas y cinco descomprimen, pero
lo que sale es **relleno de ceros**: el bloque de 65.664 bytes tiene 47.006
ceros y ni una sola cadena de texto. No hay ninguna sección legible.

El cuerpo del `.ex4` de build 600+ va **cifrado**, no solo comprimido, y la clave
vive en el propio terminal de MetaTrader. Sin MT4 no hay forma de leerlo, y con
MT4 tampoco sin un descompilador —que para este formato no existe de forma
fiable y además iría contra los términos de MetaQuotes—.

**Recomendación de uso**: terminal de MT4 aparte, cuenta demo, y «Permitir
trading automático» desactivado. Un indicador de MQL4 puede mandar órdenes si se
le deja. Nunca en la cuenta del reto.

## Lo que sí se puede verificar: el patrón

El nombre lo dice: *Turtle Soup* es barrer el extremo de una referencia y cerrar
de vuelta dentro. Eso está medido en este proyecto cuatro veces:

| dónde | muestra | resultado |
|---|---|---|
| barrido del nivel de Asia en M5, fuera de muestra 2020-2026 | 1.473 ops | **34,7 %** a 1:2 · R neta −0,459 · z −12,31 |
| barrido diario, 7 instrumentos | 1.444 ops | **−2,5 puntos por debajo** de la geometría · z −3,17 |
| CRT en H4 con el stop en la mecha | — | +2,9 pt sobre la geometría, y aun así neta negativa |
| el CRT como contexto de sus 150 operaciones | 150 ops | ninguno de **ocho** contrastes llega al umbral |

Y el detalle que más importa: en el barrido diario, **ir en contra del barrido
pierde de forma significativa**, pero ir a favor tampoco se puede cobrar, porque
el coste se resta en las dos direcciones y se lleva 0,063 R de los 0,083
disponibles.

**El patrón existe y el dibujo es correcto. Operado a ciegas no paga el coste.**

## La versión de TradingView

`pine/crt_turtle_soup.pine`. No es una traducción de su código —que no se puede
leer— sino el patrón implementado desde su definición:

- **Tres referencias**: la vela anterior ya cerrada de otra temporalidad, el
  máximo/mínimo de N velas, o el alto y bajo de Asia.
- **Dos definiciones de barrido**: estricta (el cierre vuelve dentro del *cuerpo*
  de la referencia, que es la del proyecto) o laxa (dentro del rango).
- Mínimo de mecha sobresaliente, ventana horaria opcional, y descarte de las
  velas que barren los dos extremos a la vez.
- Stop en la mecha del barrido y objetivo 1:R, o el **objetivo estructural** del
  CRT canónico —el extremo contrario de la referencia—, que en este proyecto
  salió peor que el 1:2 fijo.
- La tabla lleva escrito el 34,7 % al lado, para que no se lea como una señal.

Sin compilar en TradingView: escrito aquí sin poder probarlo.

## Y la comprobación que de verdad contesta «¿funciona?»

El indicador deja elegir la referencia. Se mide el patrón con **todas**,
ejecutando en M5 que es donde él opera, stop en la mecha del barrido y 1:2:

| referencia | n | stop mediano | coste/riesgo | ventaja que hace falta | la que tiene | R neta | z |
|---|---|---|---|---|---|---|---|
| M15 | 22.105 | 3,1 p | 46,1 % | **+15,4 pt** | **+0,1 pt** | −0,488 | −50,69 |
| H1 | 11.854 | 3,6 p | 39,7 % | **+13,2 pt** | **0,0 pt** | −0,433 | −33,03 |
| H4 | 4.297 | 4,3 p | 33,3 % | **+11,1 pt** | **−0,7 pt** | −0,397 | −18,32 |
| D1 | 555 | 6,2 p | 23,1 % | **+7,7 pt** | **0,0 pt** | −0,279 | −4,63 |

`ventaja que hace falta = (coste/stop)/(1+k)`, los puntos sobre el 33,3 %
geométrico que hay que sacar solo para empatar.

**38.811 operaciones y el acierto cae en el 33,3 % geométrico con una décima de
punto de margen, cuatro veces seguidas.** El patrón no es bueno ni malo: es
exactamente una moneda. Y hacen falta entre 8 y 15 puntos.

Lo importante para él: **da igual qué referencia le ponga al indicador.** Cambiar
M15 por H4 o por diario no cambia nada, porque el stop sigue siendo la mecha del
barrido en M5 —tres a seis pips— y ahí el coste se lleva entre el 23 % y el 46 %
del riesgo.

Para que el barrido tuviera alguna opción habría que ejecutarlo en la
temporalidad de la referencia, no en M5. Eso es lo que se midió en
`RESULTADOS_escala_diaria.md`: con stop de 64 pips el muro baja a +0,8 puntos, y
allí el barrido diario sacó **−2,5**.

## Cómo se mide SU código, y no una reimplementación

Un indicador **no se backtestea**: el Strategy Tester de MT4 solo prueba Expert
Advisors. Para medir el suyo hace falta un EA que lea sus buffers con
`iCustom()` y opere lo que marquen. Eso es `mql4/CRT_TS_Test.mq4`.

Va en dos pasadas:

```
1 · DIAGNOSTICO   ModoDiagnostico = true, un mes por el Tester.
                  En el Diario sale, por cada vela con señal, que buffer se ha
                  encendido y con que valor. Asi se sabe cual es la compra y
                  cual la venta, sin necesidad de leer su codigo.

2 · MEDICION      ModoDiagnostico = false, se meten esos numeros de buffer,
                  y se pasa por los años que se quieran.
```

El EA calcula el lotaje desde el riesgo elegido y el stop real de cada señal,
descarta las señales ambiguas —los dos buffers encendidos a la vez—, respeta el
`STOPLEVEL` del broker y permite stop en la mecha de la vela de señal o fijo en
pips.

**Lo que hay que vigilar en el Tester**, porque es donde se falsean casi todos
los backtests que circulan:

- Modelado **«Cada tick»**. Con «Solo precios de apertura» en M5 el resultado no
  vale nada.
- **Calidad del modelado** al acabar: por debajo del 90 % no es fiable.
- **Spread real** del broker, no el de por defecto. Con stops de 3 a 6 pips el
  spread decide el resultado entero.
- Y antes de nada, **la prueba del repintado**: si el indicador cambia sus marcas
  al recargar el histórico, ningún backtest de este EA significa nada, porque en
  directo no habría marcado eso.

## Lo que no se puede hacer desde aquí

Ejecutar el binario. Necesita MetaTrader 4 sobre Windows, y este entorno no tiene
MT4 ni salida a internet salvo a GitHub. Tampoco se puede reimplementar su código
exacto: está comprimido.

Lo que sí se ha hecho es medir **el patrón** con todas las configuraciones que el
indicador plausiblemente ofrece —cuatro referencias, 38.811 operaciones— y el
resultado está arriba: el acierto cae en la geometría, y hacen falta entre 8 y 15
puntos por encima.
