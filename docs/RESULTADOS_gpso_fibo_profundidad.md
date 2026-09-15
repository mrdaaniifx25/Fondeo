# La clase de Fibonacci · su preferencia está invertida

De la clase 12 de su formación gratuita salen dos cosas que cambian el análisis:

> *«Cuanto más profundo sea el retroceso, **peor**… le costará más subir»* — prefiere
> el 38 % al 50 % y el 50 % al 60 %.
>
> *«El RR siempre voy a buscar el **1:1**… el 80-90 % de las veces cierro el 100 %
> de la operación en el 1:1»* · *«el win rate está entre el 70-80 %»*

**Su sistema real es 1:1, no 1:2.** Todo lo medido hasta aquí usaba 1:2 porque es
lo que decía el material escrito. Con 1:1 el listón del azar no es el 33,3 % sino
el **50 %**, y con su stop el punto de equilibrio sube al **60,5 %**.

## La prueba, con su configuración: fibo 38/50/60, filtro de invalidez al 75 %

R bruta media, cuatro instrumentos:

| objetivo | fibo 0,382 | fibo 0,500 | fibo 0,618 |
|---|---|---|---|
| **1:1** | **−0,081** | −0,071 | **−0,061** |
| 1:1,5 | −0,061 | −0,049 | −0,027 |
| 1:2 | −0,061 | −0,027 | **−0,003** |

**Monótono en las tres filas y en la dirección contraria a la suya: cuanto más
profundo el retroceso, mejor.** Su regla explícita está exactamente invertida.

## Y a su ratio de 1:1, la regla no llega ni a cara o cruz

| fibo | acierto | R bruta | R neta |
|---|---|---|---|
| 0,382 | **45,7 %** | −0,081 | −0,156 |
| 0,500 | 46,2 % | −0,071 | −0,162 |
| 0,618 | **46,9 %** | −0,061 | −0,176 |

```
  azar geométrico a 1:1 ............ 50,0 %
  la regla mecánica da ............. 45,7 - 46,9 %
  punto de equilibrio con coste .... 60,5 %
  lo que él declara ................ 70 - 80 %
```

**Está por debajo de tirar una moneda**, y a 24-34 puntos de lo que declara.
Cero de doce celdas con R neta positiva.

## Balance de las cuatro transcripciones

| regla suya | veredicto |
|---|---|
| exige manipulación (barrido con vuelta dentro) | ✅ sostiene |
| la hora a la que se formó el nivel importa | ✅ sostiene (z +3,09, 4/4) |
| horas válidas de Asia: 2, 3 y 4 | ❌ el bloque que descarta es mejor |
| «que se quede cercano a la zona» | ❌ nada |
| entrada al cierre de H1 sin manipulación | ❌ nada |
| break-even a 1R | ❌ nada |
| parciales del 80 % a 2R | ❌ empeora |
| CRT: H4 y H1 cerrando a la vez | ❌ no replica |
| confirmación por envolvente/martillo en M5 | ❌ quitarla mejora |
| **retroceso superficial mejor que profundo** | ❌ **invertida** |

**Dos de diez.**

## Reproducir

`TF=60 COLCHON=0.10 FIBS=0.382,0.50,0.618 RATIO=1 python3 bt/barrido_dia_fibo.py`
