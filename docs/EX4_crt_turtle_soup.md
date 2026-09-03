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
