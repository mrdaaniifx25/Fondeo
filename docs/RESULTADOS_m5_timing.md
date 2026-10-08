# Resultados · ¿afina M5/M15 la entrada de AMD+FVG?

Pre-registro: `docs/PREREGISTRO_m5_timing.md` (subido antes de medir).
Código: `bt/m5_timing.py`. EURUSD, 2021-2026, resolución en M1.

## Respuesta

**No.** Ni M5 ni M15 añaden nada. Las dos caen exactamente en su precio justo,
y en neta salen peor que H1 porque el coste se come un stop más corto.

| | n | acierto | azar | exceso | R:R | riesgo | coste | bruta | neta |
|---|---|---|---|---|---|---|---|---|---|
| A · base H1 | 367 | 65,1 % | 64,2 % | **+1,0** | 0,55 | 19,9 p | 7,2 % | +0,045 [−0,053, +0,143] | −0,036 |
| B · FVG de M5 | 1 672 | 33,9 % | 33,9 % | **+0,0** | 2,37 | 9,2 p | 15,5 % | −0,007 [−0,093, +0,078] | **−0,203** |
| C · FVG de M15 | 1 434 | 43,8 % | 43,8 % | **+0,0** | 1,47 | 12,9 p | 11,1 % | −0,018 [−0,088, +0,052] | **−0,150** |
| D · filtro M5 | 359 | 65,5 % | 64,7 % | +0,7 | 0,54 | 20,0 p | 7,1 % | +0,035 [−0,062, +0,132] | −0,045 |
| P2 · vela M5 al azar | 1 547 | 33,1 % | 32,3 % | +0,8 | 2,82 | 8,8 p | 16,3 % | +0,084 | −0,319 |
| P3 · FVG de M5 al revés | 1 614 | 24,8 % | 24,5 % | +0,3 | 4,45 | 5,2 p | 27,5 % | +0,045 | −0,803 |

El exceso de B (+0,0) es idéntico al de entrar en una vela **al azar** (+0,8) y
al de usar el FVG **al revés** (+0,3). El disparo de M5 no aporta información.

Y la neta baja justo como se predijo: el stop pasa de 19,9 a 9,2 pips, el coste
fijo de 1,43 pips pasa de pesar el 7 % al 15 % del riesgo, y la neta cae de
−0,036 a −0,203. **Afinar la entrada no te da un mejor precio: te da el mismo
precio con menos margen para pagar el coste.**

## La variante que sí probaba algo, y tampoco

D es la importante: misma entrada, mismo stop y mismo objetivo que A, tomando
sólo las operaciones en las que además existía un FVG de M5 *antes* de entrar.
Es la única forma en que una temporalidad menor puede sumar: como **filtro**,
no como mejora de precio.

Diferencia emparejada D − A sobre las 359 operaciones en que existen las dos:
**+0,0000 en bruta, en neta y en exceso.** Cero exacto. El FVG de M5 existe
prácticamente siempre dentro de una vela de H1 que ya trae FVG, así que no
filtra nada. Quita 8 operaciones de 367.

## La predicción del pre-registro

Se escribió antes. Las tres se cumplieron:

- «B y C peores en neta que A» → sí (−0,203 y −0,150 frente a −0,036).
- «B y C con bruta parecida a A» → sí (todas pegadas a cero).
- «D indistinguible de A» → sí, cero exacto.

## Dos errores encontrados por el camino

**1. La primera versión de esta medición miraba el futuro.** Pedía que hubiera
un FVG de H1 en las 5 velas siguientes a la finta y aun así entraba en B/C
antes de que esa vela cerrara — en el **100 %** de los casos. Daba +23,9 de
exceso y bruta +0,78. Se cazó con los placebos: entrar en una vela al azar daba
+16,9 y el FVG al revés daba +16,6. Cuando el disparo falso rinde igual que el
bueno, el resultado no es del disparo.

El nulo puro (entradas en minutos al azar de todo el histórico, mismas
distancias, misma función de resolución) daba −1,1 / +0,1 / −1,1 de exceso, o
sea limpio. Eso descartó el resolutor y dejó el fallo en la construcción.

**2. La medición base admitía entradas con el objetivo ya rebasado.** Es la
corrección grande, y tiene documento propio:
`docs/CORRECCION_objetivo_rebasado.md`. Tumba el resultado de AMD+FVG.

## Nota metodológica

La tabla de diferencias emparejadas B−A y C−A que imprime el script **no es
válida** y no se usa aquí. Emparejar exige quedarse con los casos en que existe
A, y «existe A» significa que apareció un FVG de H1 *después* de que B ya
hubiera entrado. Es el mismo futuro por otra puerta. Sólo D es emparejable,
porque comparte instante de entrada con A.

## Qué queda contestado

La intuición de partida era buena: si algo pasa en H1, pasa también en M5. Es
verdad — un vela de H1 son doce de M5, es el mismo hecho con más detalle. Lo
que no se sigue es que mirar el detalle sirva para decidir mejor. Aquí el
detalle da exactamente la misma información y cuesta más caro.
