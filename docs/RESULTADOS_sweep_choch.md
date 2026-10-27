# Resultados · barrido en H4/H1 con cambio de estructura en M15/M5

Pre-registro `docs/PREREGISTRO_sweep_choch.md`, escrito antes de medir.
Código en `bt/sweep_choch.py`. EURUSD 2020-2026.

## La celda principal

    H4 + M15   n 1.016   1,27 operaciones al día
               acierto 27,5 %   (necesita 36,6 %)
               riesgo 14,7 p    coste 9,7 % del riesgo
               BRUTA -0,1762 (z -4,19)      NETA -0,3018
               IC95 [-0,385, -0,219]        z -7,13

**El criterio no se cumple.** Y esta vez el intervalo está lejos del cero.

La secundaria, H1 + M5: n 2.994, acierto 31,0 %, bruta −0,0711 (z −2,81), neta
−0,3064. Lo mismo.

## Lo que sí acertó, y no es poco

**Su idea del stop arregla el problema del coste.** Poniéndolo en el último
pivote de estructura en vez de en el extremo del barrido:

    riesgo mediano    14,7 pips
    coste             9,7 % del riesgo

Es **el mejor cociente coste/riesgo de cualquier regla escrita a mano** del
proyecto, y cae justo en la banda de 10 a 20 pips donde el modelo había dicho que
vive la ventaja. Esa pieza es buena y hay que quedársela.

Y la frecuencia, 1,27 al día, coincide con la suya. La traducción es fiel.

## Pero el gatillo pierde, y pierde de verdad

    bruta  -0,1762   z -4,19

Esto no es "cero". Es **significativamente negativo**. Con objetivo 2R el acierto
de equilibrio en bruto es 33,3 % y la regla da **27,5 %**: casi seis puntos por
debajo del azar geométrico, sobre mil operaciones.

Entrar al cierre de la vela que rompe la estructura, después de un barrido, es
**peor que entrar al azar** con ese mismo stop y ese mismo objetivo.

Ningún año se salva: de −0,05 a −0,34 en bruta, los siete negativos.

## Dónde queda esto frente a lo anterior

| variante | bruta | coste %R | neta |
|---|---|---|---|
| modelo con 200.000 filas (decil sup.) | **+0,048** | 9 % | −0,064 |
| barrido de sesión + confirmación | −0,017 | 24 % | −0,307 |
| **barrido H4 + estructura M15** | **−0,176** | **9,7 %** | −0,302 |

Las dos últimas dan la misma neta por caminos opuestos: una tiene el peaje
disparado y la bruta en cero; ésta tiene el peaje resuelto y la bruta hundida.

Y el listón declarado antes de medir era bruta **+0,095**. Salió −0,176.

## Lo que deja

- **El stop en el pivote de estructura vale.** 9,7 % de coste con una regla
  escrita a mano es lo mejor que hemos conseguido sin un modelo.
- **El cambio de estructura como gatillo, no.** Resta 0,18 R frente al azar.
- Y otra vez lo mismo, por si hacía falta más evidencia: **el momento de entrar
  no es lo que decide**; esperar a la confirmación de estructura empeora la bruta
  tanto como la espera mejoraba el coste.
