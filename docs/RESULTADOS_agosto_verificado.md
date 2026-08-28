# Verificación de agosto · CORREGIDO

> **Aviso de corrección (2026-08-28, posterior).** Con las 9 fichas que faltaban
> —del 3 al 11 de agosto— la muestra sube a 25 y sale a la luz un fallo de mi
> método: para resolver cada operación yo tomaba **el primer momento en que el
> precio tocaba su entrada a partir de las 08:00**. Con stops de 3 pips ese
> precio se toca muchas veces en una mañana, y cada toque da un resultado
> distinto. Sobre las 14 verificables:
>
> | supongo que entra a partir de | n | %TP | R bruta |
> |---|---|---|---|
> | 08:00 | 14 | 28,6 % | −0,142 |
> | 09:00 | 13 | 38,5 % | +0,157 |
> | **09:30** | 13 | **69,2 %** | **+1,082** |
> | 10:00 | 10 | 70,0 % | +1,107 |
> | 11:00 | 8 | 25,0 % | −0,250 |
>
> El resultado lo decide mi suposición, no los datos. Y en cuatro casos —T18,
> T19, T22 y T23— mi resolución dice SL o «sin resolver» donde **su propia
> herramienta declara TP**, siempre en el sentido de que yo entro demasiado
> pronto.
>
> **Todo lo que sigue queda en suspenso** hasta tener la hora de entrada de cada
> operación. Con ella la resolución es exacta y no hay nada que suponer.

# Lo que se calculó (con el método defectuoso)

Fecha: 2026-08-28. Datos: `data/eurusd_m1_2026_08.parquet` (2 al 21 de agosto).
Fichas: `data/agosto_operaciones.csv`, leídas de las capturas de la herramienta
de posición, con precios exactos y fecha visible.

## Lo verificable

7 de las 16 caen dentro de los datos publicados. Las otras 9 son del 24 al 28 y
HistData todavía no las ha publicado.

| id | fecha | dir | entrada | stop | TP | riesgo | entra | resultado |
|---|---|---|---|---|---|---|---|---|
| T01 | 14 ago | compra | 1,15476 | 1,15438 | 1,15552 | 3,8 p | 09:38 | **TP** en 31 min |
| T02 | 17 ago | compra | 1,15919 | 1,15822 | 1,16114 | 9,7 p | 08:29 | **TP** en 73 min |
| T03 | 18 ago | compra | 1,15714 | 1,15678 | 1,15786 | 3,6 p | 08:01 | SL en 3 min |
| T04 | 18 ago | compra | 1,15705 | 1,15677 | 1,15762 | 2,8 p | 08:01 | SL en 3 min |
| T05 | 19 ago | compra | 1,15948 | 1,15883 | 1,16078 | 6,5 p | 08:19 | **TP** en 211 min |
| T06 | 20 ago | compra | 1,16928 | 1,16853 | 1,17078 | 7,5 p | 09:42 | **TP** en 99 min |
| T07 | 20 ago | venta | 1,16831 | 1,16899 | 1,16704 | 6,8 p | 08:45 | SL en 56 min |

**4 TP, 3 SL.** 57,1 % contra una geometría de 33,3 %. R bruta media **+0,716**,
neta **+0,470** con 1,2 pips de diferencial. En euros, con 150 € por operación:
**+752 € bruto, +493 € neto** en siete operaciones.

**Significación: p = 0,173.** Cuatro aciertos de siete con una tasa base de un
tercio salen por azar una de cada seis veces. Es un buen dato, no una prueba.

## El sobre, abierto

Sellado en el commit `d510090` antes de recibir ninguna captura: la regla
mecánica que llevo probando todo el proyecto —cierre más allá del nivel de Asia,
envolvente, entrada al cierre de la envolvente, 1:2— sobre esos días de agosto.

```
n 13 · TP 1 · SL 12 · %TP 7,7 % · bruta −0,769 · neta −1,192
```

Y en los cuatro días en que ambos operaron:

| día | la regla mecánica | él |
|---|---|---|
| 14 ago | **venta** 1,15446 → SL | **compra** 1,15476 → TP |
| 17 ago | **venta** 1,15944 → SL | **compra** 1,15919 → TP |
| 19 ago | **venta** 1,15896 → SL | **compra** 1,15948 → TP |
| 20 ago | **venta** 1,16872 → SL | **compra** 1,16928 → TP |

**Dirección opuesta los cuatro días. La regla perdió 4 de 4; él ganó 4 de 4.**

## Lo que eso significa, y es el hallazgo

Colocando cada entrada respecto al rango de Asia de su día, el reparto es limpio:

| dónde entra | n | resultado |
|---|---|---|
| **por encima del alto de Asia**, comprando (2,7 a 9,1 p por encima) | 4 | **4 TP, 0 SL** |
| **dentro del rango de Asia** | 3 | 0 TP, **3 SL** |

Toda la estrategia que he probado y cerrado estos días **desvanece** la ruptura:
el precio se pasa del nivel y se vende esperando la vuelta. Sus ganadoras hacen
lo contrario: **el precio rompe el alto de Asia y compra la continuación.**

Es la estrategia inversa a la que llevo semanas midiendo. Eso explica a la vez
por qué mis pruebas salían negativas y por qué sus resultados no cuadraban con
ellas: no estábamos midiendo lo mismo, estábamos midiendo lo contrario.

## Tres reservas, que no son pequeñas

1. **Faltan días.** De las 22 capturas anteriores identifiqué operaciones el 4,
   el 10 y tres entre el 11 y el 13 de agosto. Ninguno de esos días aparece en
   las 16 fichas. Si esas operaciones existieron y no están, la muestra está
   incompleta y 4 de 7 puede ser el resto que sobrevivió.
2. **T03 y T04 no son dos operaciones.** Mismo día, ambas entran a las 08:01,
   con entradas separadas por un pip, y ambas saltan a los 3 minutos. Es una
   sola operación con doble tamaño —300 € de riesgo a la vez—, y cuenta como una.
   La muestra efectiva son seis.
3. **El reparto ruptura/rango lo encontré mirando.** Sale limpio, pero es una
   partición elegida después de ver los resultados. Necesita su propia prueba.

## Lo que toca ahora

Pre-registrar «seguir la ruptura del nivel de Asia» y probarla en todo el
histórico, que es donde hay potencia. La especificación exacta de entrada y stop
la tiene que dar él: en sus cuatro ganadoras entra entre 2,7 y 9,1 pips por
encima del alto, y el stop cae a veces por encima y a veces por debajo de ese
alto. Esa diferencia, con stops de 4 a 10 pips, decide el resultado.

Y para las nueve del 24 al 28: cuando HistData publique el mes completo.

## Ficheros

```
data/agosto_operaciones.csv     las 16 fichas leídas de las capturas
data/agosto_verificacion.csv    el resultado de cada una
data/asia_agosto_mecanica.csv   el sobre, sellado antes
```
