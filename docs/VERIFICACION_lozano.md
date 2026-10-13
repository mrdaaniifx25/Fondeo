# Verificación · sus propios números contra los míos

Cinco vídeos del mismo operador (Lozano, «programa Focus»), aportados por el
usuario. Todo el contenido técnico ya está medido y cerrado
(`RESULTADOS_smt.md` cierra la lista completa).

Este documento no mide nada nuevo. Sólo compara **lo que él dice** con **lo que
está medido**, y cuenta las operaciones que enseña en pantalla.

## 1 · El SMT: damos el mismo número

Él lo dice dos veces, literal:

> *«las ventas tienen un 51 % de probabilidad»*
> *«esto me da un 51 %, vamos a llamarlo así, de posibilidades»*

Medición de `RESULTADOS_smt.md`, 6.122 operaciones, seis combinaciones de
instrumento y socio: **+0,82 puntos** sobre el azar. El azar direccional es
50,0 %, así que la medición dice **50,8 %**.

**Él dice 51. Yo mido 50,8. No hay discrepancia ninguna.**

La discrepancia está en qué vale ese número. Con su geometría:

```
  stop 4 pips · coste 1,43 pips · R:R 2

  acierto necesario para empatar .......... 45,2 %
  lo que da el azar ....................... 33,3 %
  lo que aporta un 51 % direccional ....... +0,8  ->  34,1 %
                                            ──────────────────
  sigue faltando .......................... +11,1 puntos
```

Un 51 % es real y es lo que hay. Sencillamente **no llega**, porque el stop
diminuto hace que el coste valga el 36 % del riesgo.

## 2 · Sus propias cuentas, contadas de su pantalla

En el vídeo del 11/12 repasa el historial de dos cuentas leyéndolo en voz alta
mientras lo enseña:

> **Wall Street**: *«stop, TP, break even, retiro. Break even, stop, stop, stop,
> TP, retiro, TP, retiro, stop, stop, stop, TP, retiro. Y ahora mismo llevamos
> uno, dos, tres stops encadenados»*
>
> **FundedNext**: *«stop, stop, stop, TP parcial, stop, stop, TP parcial, TP,
> stop, TP»*

Contando:

```
  Wall Street (desde 22/07)    TP  4   stop 10   BE 2   acierto 28,6 %
  FundedNext (desde 02/09)     TP  4   stop  6   BE 0   acierto 40,0 %
  ──────────────────────────────────────────────────────────────────────
  LAS DOS JUNTAS               TP  8   stop 16          acierto 33,3 %  ±18,9
```

**33,3 % exacto.** El precio justo de un 1:2, clavado.

**El límite hay que decirlo**: son 24 operaciones y el intervalo es de ±18,9
puntos. Esto **no demuestra** que esté en el precio justo. Pero es la única
medición directa que existe de su acierto real, sale en el centro exacto del
azar, y coincide con lo medido sobre 30.000 operaciones de la misma familia.

## 3 · Y aun así cobra, que es lo que confunde

De la cuenta de Wall Street retiró **7.639 $** con un 28,6 % de acierto. No es
contradictorio: es exactamente el mecanismo que mide `RESULTADOS_payouts.md`.

En una cuenta fondeada **retiras las ganancias y la pérdida está limitada** al
saldo de la cuenta y a la cuota. Con acierto en el precio justo, eso produce
payouts reales y frecuentes. Él mismo lo enseña sin querer: esa cuenta acabó en
**−4,5 %** y la empresa se la canceló.

Y la de FundedNext llegó a **−7 %** antes del primer cobro de 500 $.

## 4 · Lo que él atribuye a la gestión, y tiene razón a medias

> *«no soy el trader más técnico del mundo, no soy el trader que sabe más
> conceptos del mundo… pero mi gestión de riesgo es impoluta y eso me hace tener
> los resultados que tengo»*

Es exacto, y está más cerca de la verdad de lo que él cree. Sus resultados **no
vienen de la lectura del gráfico** —que mide en el precio justo, según sus
propios números y los míos— sino de **la estructura de la cuenta fondeada**:
retirar pronto, arriesgar poco por operación, y que la pérdida esté acotada.

Eso es real y es replicable. Lo que no es replicable es la parte que vende.

## 5 · Lo que enseña la sesión en directo

Es el material más valioso de los cinco vídeos, porque no está seleccionado.

- **Sesión de Londres del jueves**: una sola operación en toda la sesión.
  Stop *«al pip»*. Cierra sin más operaciones.
- **Sesión de Nueva York del 11/12**: compra *«lo más arriba que se puede
  comprar en la vida»*, la sesión acaba en **break even** —*«commission trade»*,
  en sus palabras— tras casi tres horas.

Dos sesiones grabadas enteras, sin editar: **un stop y un break even**.

No es una crítica. Es lo que predice todo lo medido.

## Qué queda cerrado con esto

Los tres operadores que ha traído el usuario —Benjamin, Orion, Lozano— usan la
misma familia de nueve ideas. Las nueve están medidas y todas valen cero antes
de costes. Y en los dos casos donde hay números propios que contrastar
(`VERIFICACION_benjamin_real.md` y este documento), **los números de ellos y los
míos coinciden**.
