# La regla, escrita · verificada en las 16 de agosto

Fecha: 2026-08-28. De las 16 explicaciones que el usuario escribió caso por caso
en `docs/velas_ruptura.html`, más la verificación mecánica contra las velas.

## Lo que dice, unificado

Escribió dieciséis explicaciones y todas dicen lo mismo con distintas palabras.
No hay «unas veces desvanece y otras sigue»: **la dirección nunca se elige, la da
la vela.**

```
NIVEL       el alto y el mínimo de Asia (00:00 - 08:00, hora de Madrid)
VENTANA     Londres. En la práctica, de 08:00 a 11:20

GATILLO     en M5, una vela que cumpla A o B:

  A   su CUERPO entero queda a un lado del nivel y la vela va en ese sentido
      · alcista con el cuerpo por encima  ->  COMPRA
      · bajista con el cuerpo por debajo  ->  VENTA

  B   (el que usa cuando llega tarde) cierra más allá del CUERPO de la última
      vela contraria, yendo en ese sentido

ENTRADA     al cierre de esa vela
STOP        al otro lado — sin regla derivada, ver abajo
OBJETIVO    1:2 fijo
REENTRADA   si a las dos velas el precio se da la vuelta, entra al contrario
            con el mismo esquema
```

**El gatillo B es la «vela envolvente» que describió hace semanas.** Estaba en lo
cierto desde el principio; lo que faltaba era que hay **dos** gatillos y que el
segundo es el de las entradas tardías.

Verificación: tolerando ±1 vela —porque unas veces da la hora de apertura de la
vela y otras la de cierre— **el gatillo se cumple en las 16 de 16**.

| | casos |
|---|---|
| cumple A y B a la vez | 9 |
| sólo A | 2 |
| sólo B | 5 |
| ninguno | **0** |

## Lo que faltaba, y era lo importante

El gatillo por sí solo **no selecciona nada**. Contando cuántas veces salta entre
las 08:00 y las 12:00, sobre los dos niveles y en las dos direcciones:

| | veces por mañana |
|---|---|
| gatillo A | 46,1 |
| gatillo B | 59,2 |
| A o B | **74,5** |

Él toma **1,6 al día**. O sea que el gatillo describe *cuándo se puede entrar*,
no *cuándo entra*. Lo que decide es otra cosa.

Y esa otra cosa aparece al añadir una condición que se deduce de cómo opera —
mira un nivel, entra una vez, y no vuelve hasta que el precio se aleja y regresa:

```
ARMADO   el nivel está armado mientras el precio no esté pegado a él.
         Dispara sólo cuando una vela TOCA el nivel y cumple A o B.
         Tras disparar se desarma, y se rearma cuando el precio se aleja.
```

Con eso: **1,1 disparos por mañana**, contra sus 1,6. El resto lo explican las
reentradas. Del orden correcto, y ya es una regla mecánica.

## Lo único que sigue sin regla: el stop

Su stop **no está** en ningún punto estructural. Comparado con los tres
candidatos naturales, y siempre **por dentro** de los tres:

| el stop queda, respecto a… | mediana | a menos de 1 pip |
|---|---|---|
| el extremo de la vela del gatillo | **2,7 p por dentro** | 0 de 16 |
| el extremo de la vela anterior | 1,5 p por dentro | 6 de 16 |
| el propio nivel de Asia | 1,4 p por dentro | 4 de 16 |

Es decir: pone el stop **más ajustado que la estructura**, a ojo. Eso no se puede
derivar, y es justo lo que fija el lote y por tanto qué fracción del riesgo se
lleva el diferencial. Hace falta que lo diga él.

## Estado

- Gatillo: **escrito y verificado** en 16 de 16.
- Selección: **escrita** (armado por visita al nivel), da 1,1/mañana contra 1,6.
- Stop: **sin regla**. Es lo que falta para poder pre-registrar y correr los
  ~1.400 días de 2020-2026.

Una advertencia para cuando se corra: el ajuste 16 de 16 usa una tolerancia de
±1 vela. En un backtest no hay tolerancia — la regla dispara donde dispara —, así
que **no reproducirá sus entradas exactas**, y no debe esperarse que lo haga.
