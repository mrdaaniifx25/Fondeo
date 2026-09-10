# Resultados · el order block de M5 y la vela de M1

Preregistrado en `docs/PREREGISTRO_ob.md`. 223 entradas suyas contra 4.965 velas
de M5 de los mismos 164 días en las que tenía las manos libres.

## 1 · El order block: entra dentro de uno MENOS que el azar

| zona | sus entradas | control | z | p |
|---|---|---|---|---|
| completa (mínimo-máximo) | 46,6 % | 55,5 % | **−2,61** | 0,009 |
| solo el cuerpo | 29,1 % | 36,3 % | −2,18 | 0,030 |

Y en su **misma dirección**, solo el **20,6 %** de sus entradas. Además no separa
nada: dentro de un OB a favor acierta el 66,7 % (n=46) y fuera el 64,3 % (n=177),
p = 0,86.

**Aviso importante, y va en mi contra**: mi definición de OB dispara en el 55 %
de todas las velas. Eso no puede ser el order block del que él habla — un
concepto que se cumple en la mitad de las velas no selecciona nada. Le falta al
menos una condición que yo no he puesto: que el impulso **rompa estructura**
(se lleve por delante un máximo o mínimo previo), y probablemente que el OB esté
**sin mitigar**. Con esas dos, el número de OB caería mucho y la medición podría
cambiar de signo.

Así que lo correcto no es «el OB no le sirve», sino: **con la definición laxa, no
aparece. Hace falta la definición suya para decidirlo.**

## 2 · La vela de M1: aquí sí hay algo

Los patrones se habían medido siempre sobre la vela de **M5**. Él ejecuta en
**M1**. Es la primera vez que se mira la vela en la que de verdad entra.

| | n | acierto | R neta |
|---|---|---|---|
| **envolvente de M1 a su favor** | **26** | **84,0 %** | **+1,228** |
| el resto | 197 | 62,2 % | +0,610 |

Fisher **p = 0,0433**. No pasa el Bonferroni de este informe (0,008), pero **es
lo primero de su propio vocabulario que separa sus ganadoras de sus perdedoras**.
Y va en la misma dirección en los dos grupos:

```
bloques 1-4   envolvente 19 ops  88,9 %   ·   resto 131 ops  62,9 %
bloque 5      envolvente  7 ops  71,4 %   ·   resto  66 ops  60,9 %
```

El cuerpo de la vela de M1, además, va **al revés que en M5**:

| cuerpo de la vela de M1 | n | acierto | R neta |
|---|---|---|---|
| 0-40 % | 31 | 46,7 % | +0,169 |
| 40-60 % | 33 | 51,6 % | +0,328 |
| **60-80 %** | **64** | **80,3 %** | **+1,110** |
| 80-100 % | 95 | 64,8 % | +0,685 |

No es contradictorio con el hallazgo de M5, encaja: **en M5 una vela toda cuerpo
es un impulso ya hecho y es mala. En M1 una vela decidida es el gatillo y es
buena.** Es exactamente lo que él dice —M5 marca, M1 ejecuta— medido por primera
vez en la temporalidad correcta.

## 3 · Cuántas de sus 223 cumplen su propia descripción

Su descripción: *H4 sweep · M15 misma dirección · OB en M5 · envolvente o rotura
en M1*.

| | de 223 | acierto |
|---|---|---|
| rompe el extremo de la vela de M1 anterior | 202 (**90,6 %**) | 66,8 % |
| dentro de un OB de M5 a su favor | 44 (19,7 %) | 65,1 % |
| envolvente de M1 a su favor | 26 (11,7 %) | 84,0 % |
| **las tres a la vez** | **7 (3,1 %)** | — |

**Siete de doscientas veintitrés.** La predicción 5 decía «menos del 25 %» y se
queda en el 3 %.

La pieza que cubre casi todo —romper el extremo de la vela anterior de M1, el
90,6 %— no selecciona nada: es simplemente «entro cuando el precio se mueve».

## Lo que esto significa, dicho sin rodeos

**No es que no se vea su patrón. Es que el patrón que describe no es el que
opera.** Sus entradas se predicen con AUC 0,800; hace algo estable y repetible.
Pero las palabras con las que lo cuenta describen el 3 % de lo que hace.

Eso no es un defecto suyo ni una mentira: es lo normal cuando una destreza se
aprende mirando y no leyendo. La descripción es la teoría con la que aprendió; lo
que ejecuta es otra cosa que se le ha ido afinando encima.

## Lo que sí se lleva de aquí

1. **La envolvente de M1 es el primer candidato real** que sale de su propio
   vocabulario. 26 operaciones, 84 %, +1,228 R neta. Va preregistrada para el
   bloque 6.
2. **El cuerpo de M1 entre el 60 % y el 80 %** es su mejor tramo. También va.
3. **El OB hay que volver a medirlo** con su definición, no con la mía.
