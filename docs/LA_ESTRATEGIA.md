# LA ESTRATEGIA. Cero decisiones. Sin agujeros.

Esto sustituye a `docs/JUEGO_JUSTO.md`, que te dejaba a ti la dirección. Eso
fue un error mío: la pieza que faltaba era justo la que no debía dejarte.

Números: `docs/RESULTADOS_juego_justo.md` y `docs/RESULTADOS_cual_sigo.md`.
Código: `bt/version_final.py`.

---

## Las reglas

```
  INSTRUMENTOS   EUR/USD · oro · DAX
  UNA POSICIÓN   por instrumento. Si ya tienes una abierta en oro, hoy no
                 abres otra en oro. Esperas a que cierre.

  CUÁNDO         08:00 Madrid, en los instrumentos que tengas libres.

  DIRECCIÓN      ¿la vela DIARIA DE AYER cerró por encima de su apertura?
                   SÍ  -> COMPRAS
                   NO  -> VENDES
                 Se mira en ese instrumento. Tarda cinco segundos.
                 No hay nada que interpretar y no admite opinión.

  STOP           1,0 x ATR(14) de la temporalidad DIARIA
  OBJETIVO       2 x el stop
  RIESGO         0,75 % = 75 € por operación
  SALIDA         stop, objetivo, o a los 5 días a mercado. Lo que llegue antes.
                 No se mueve el stop. No se cierra antes. No se mira.
```

Eso es la estrategia completa. **No hay ni una decisión que tomar.** Si ayer
cerró en verde, compras. Si cerró en rojo, vendes. Punto.

Salen **unas 190 operaciones al año**, unas 16 al mes, 0,75 al día. Casi todos
los días tienes algo que hacer, y muchos días tienes algo abierto (99 % de los
días).

## El tamaño, calculado

```
  EUR/USD   ATR diaria ~71 pips     stop 71 pips      0,105 lotes
  oro       ATR ~28 USD             stop 28 USD       0,027 lotes
  DAX       ATR ~200 puntos         stop 200 puntos   0,37 contratos
```

Fórmula: `tamaño = 75 € / (stop en unidades × valor de la unidad)`

## Por qué 0,75 % y no 0,50 ni 1,00

No es un número elegido a ojo ni ajustado. Sale del **peor día realmente
observado** en 5,7 años con esta estrategia: **−3,72 R**.

```
  riesgo 0,75 %  ->  peor día observado = -2,79 %   (límite: -3,00 %)  ✔
  riesgo 1,00 %  ->  peor día observado = -3,72 %   ELIMINADO          ✘
```

Y se confirma en la simulación: a 1,00 % el límite diario mata al **25,5 %** de
las cuentas; a 0,75 %, al **0,0 %**.

**0,75 % es el riesgo más alto que sobrevive al peor día que ha pasado de
verdad.** Por eso ése y no otro.

## Lo que vale, honestamente

El juego es justo. Por operación, con el coste puesto:

```
  EUR/USD   n 359   neto +0,0728   z +1,11
  oro       n 242   neto +0,0737   z +0,92
  DAX       n 246   neto -0,1018   z -1,33
```

Tres instrumentos, ninguno se separa de cero. Esperanza ≈ **0**.

Probabilidad de pasar las dos fases: **entre el 10 % y el 35 %.**

Ese rango ancho es honesto y te explico por qué: el estimador con los caminos
reales y tope de 300 días da **8,9 %**; el estimador paramétrico sin tope da
**35,8 %**. El primero se queda corto porque el tope de tiempo trunca; el
segundo se pasa porque supone operaciones independientes y las rachas se
apelotonan. **Con 5,7 años de datos no puedo estrecharlo más.**

> **Mira en tu cuenta de FundingPips si el examen tiene límite de días.** Si no
> lo tiene, estás en la parte alta del rango. Es el dato que más mueve tu
> probabilidad y lo tienes tú, no yo.

### Corrección a lo que te dije ayer

Ayer te di **35,8 %** como la cifra. Era optimista: salía de un modelo que
supone que las operaciones son independientes. Con los caminos diarios reales
—donde los días malos van juntos— baja. La cifra honesta es el rango de
arriba, no el 35,8 % solo.

## Las rachas, para que no te pille

```
  días en verde           48 %
  racha de días en rojo   mediana 1 · p90 4 · peor observada 13
  acierto por operación   ~44 %   (objetivo 2R)
```

Trece días seguidos en rojo pasaron una vez en 5,7 años. Van a volver a pasar.
**La racha está en el plan.**

## Lo que no te va a dar, y no te lo voy a esconder

300 €/mes. Para eso harían falta +0,149 R por operación y aquí la esperanza es
cero; con esta muestra una ventaja así habría salido a z 6,8.

Lo que te da: **operar casi todos los días sin estar perdiendo dinero**, una
tirada real a una cuenta que te salió gratis, y las cien operaciones apuntadas
que hacen falta para medir lo único que queda sin medir.

## Las dos hojas que tienes que llevar

**1 · El registro.** Antes de saber el resultado:

```
  fecha · hora · instrumento · dirección · entrada · stop · objetivo
```

Esto es para comprobar que estás ejecutando las reglas y no improvisando. Es
aburrido y es el 90 % del trabajo.

**2 · La hoja de las veces que NO seguiste la regla.** Cuando mires el gráfico
y pienses «hoy la regla dice comprar pero esto se va abajo», **no operes en
contra: apúntalo** —fecha, instrumento, qué decía la regla, qué pensabas tú— y
luego ejecuta la regla.

Al llegar a 100 apuntes compruebo si tu intuición acertaba. Si acertaba, la
metemos en las reglas con un número delante. Si no, lo sabrás y dejará de
costarte dinero y cabeza.

**Ésa es la única variable del proyecto que sigue sin medir, y es la tuya.**
