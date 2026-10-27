# Lo simple. Una página. Sin alternativas.

Números detrás: `docs/RESULTADOS_lo_simple.md`. Indicador: `pine/crt_londres_asia.pine`.

---

## El plan

```
  INSTRUMENTO   EUR/USD. Sólo. Nada más.
  CUÁNDO        Sesión de Londres. El indicador te la marca.
  ENTRADA       Lo que marca pine/crt_londres_asia.pine. Si no marca, no operas.
  STOP          1,5 x ATR.  (NO la mecha: medido, -0,02 vs -0,12)
  OBJETIVO      2R. Fijo. No se mueve.
  RIESGO        0,50 % por operación.  = 50 EUR en la cuenta de 10.000
  TOPE DEL DÍA  3 operaciones. A la tercera cierras la plataforma.
  SI FONDEAS    retiras el 50 % del beneficio, no el 100 %.
```

Eso es todo. No hay más reglas porque **las demás reglas están medidas y no
sirven**: parar tras la primera pérdida baja la aprobación del 35,5 % al
30,4 %. Si necesitas una regla para tu cabeza, «paro el día tras la primera
ganancia» no cuesta nada. Pero no la necesitas.

## La única regla de tamaño que importa

`operaciones del día × riesgo` **nunca por encima del 2 %**.

Con 0,50 % × 3 vas al 1,50 %. Tienes margen. Si un día te pasas a 4
operaciones no pasa nada; si te pones a 1 % × 3 = 3 % **la probabilidad de
aprobar se cae del 35 % al 4 %**. Ese es el acantilado y es el único error que
no se perdona.

## Lo que esto vale, en honesto

```
  pasar las DOS fases                    35,8 %
  perder la cuenta                       64,2 %
  tiempo mediano si pasas                ~92 días hábiles
```

Suponiendo que la entrada **no tiene ventaja**, que es lo que mide este
repositorio. Si tiene aunque sea +0,02 R, sube al 46,3 %.

La cuenta te salió gratis en un sorteo. **Con 35,8 % y coste cero, intentarlo
es correcto.** No es una apuesta tonta: es la única jugada con valor esperado
positivo que hay encima de la mesa.

## Lo que NO te va a dar

Si pasas y te fondean, y la entrada sigue sin tener ventaja, esa cuenta de
10.000 te pagará **unos 850 € en total, repartidos en meses, y luego
reventará.** Eso no es pesimismo: es el teorema del muestreo opcional y está
comprobado en seis configuraciones distintas en `RESULTADOS_lo_simple.md`.

Para 300 €/mes de verdad, sostenidos, sobre 10.000 € harían falta **+0,149 R
por operación** — 41,6 % de acierto a 1:2. Lo mejor que he medido en tres meses
es 0,00.

**Tu objetivo no es imposible. Es imposible sobre 10.000 €.** Sobre una cuenta
fondeada de 100.000 los mismos 300 €/mes necesitan +0,015 R. Diez veces menos.

## Tu trabajo de verdad durante estos 92 días

No es acertar. Es **generar los datos que no tengo.**

Apunta cada operación en una hoja **antes de saber el resultado**: fecha, hora,
dirección, precio de entrada, stop, objetivo, y una línea de por qué entraste.
Cuando lleves **100 operaciones apuntadas así**, me las pasas.

Con 100 operaciones puedo separar dos cosas que hasta ahora no he podido
separar: si tu criterio al elegir *cuáles* de las señales tomar aporta algo por
encima de tomarlas todas. Eso es lo único que podría encontrar la ventaja de
+0,149, porque el patrón mecánico ya está medido y no la tiene.

**Si apruebas: bien, y con datos. Si no apruebas: no has perdido nada y
tenemos 100 operaciones tuyas que medir.** Es la única forma de que estos 92
días no se tiren a la basura en ninguno de los dos casos.
