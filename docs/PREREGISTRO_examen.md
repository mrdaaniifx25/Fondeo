# Preregistro · el examen de Londres

Escrito **antes** de que él haga una sola sesión. Es la tercera vez que se le
mide a él y no a una regla, y la primera con sus reglas ya escritas.

## Qué se le da

Veinte mañanas de EURUSD, 08:00-11:30 hora de Madrid, elegidas con semilla
`20260901` sobre **1.661 días laborables elegibles** de 2020 a 2026. Sin filtrar
por resultado, por volatilidad ni por nada.

En pantalla: **H4, M15, M5 y M1** a la vez, con el alto y el bajo de Asia
marcados. Avanza minuto a minuto. Cuando entra, **coloca él el stop** y el
objetivo se pone solo al 1:2.

**Garantía de que no hay futuro.** El fichero se corta en el minuto 210 (11:30) y
solo lleva M1 de la sesión: las velas de M5, M15 y H4 se construyen en el
navegador desde M1 hasta el minuto actual. La vela en formación es real y no
existe en el fichero ni un dato posterior al cursor.

**Sí ve el resultado de cada operación**, a diferencia del simulador anterior. Lo
necesita para poder aplicar su propia regla de parar tras dos pérdidas.

## Métrica principal

**R neta por operación**, con coste de 1,43 pips, y su z contra cero.

Y la comparación que da sentido a todo esto: **él contra la regla mecánica en
esos mismos veinte días**. La regla es la de `REGLA_asia_nivel.md` con el stop en
el extremo de la vela de M5, que es la que él confirmó el 31 de agosto.

```
si él ≈ la regla   ->  su criterio no añade nada, y el asunto está cerrado
si él < la regla   ->  su criterio resta
si él > la regla   ->  hay algo en su selección, y es lo primero en dos meses
```

## Secundarias declaradas

- acierto contra el 33,3 % geométrico
- reparto por anchura de stop, por hora, por dirección, y según el nivel sea el
  alto o el mínimo de Asia
- sesiones sin operar, y qué tenían
- cuántas veces respeta sus propias reglas: ventana, dos pérdidas, 1:2

## Lo que este examen puede y no puede decidir

Con 1,43 pips de coste, el punto de equilibrio depende del stop que ponga:

```
stop  5 p -> 42,9 %      stop 10 p -> 38,1 %
stop  7 p -> 40,1 %      stop 15 p -> 36,5 %
```

Y la potencia, según cuántas operaciones salgan:

| operaciones | error típico | acierto para superar el azar | ¿detectaría su agosto? |
|---|---|---|---|
| 20 | 10,5 % | 54,0 % | sí, z +2,8 |
| 30 | 8,6 % | 50,2 % | sí, z +3,4 |
| 40 | 7,5 % | 47,9 % | sí, z +3,9 |

**Sirve para detectar un efecto del tamaño de su agosto** —62,5 % verificado— y
no sirve para detectar uno pequeño. Si sale un 40 %, no se podrá decir ni que sí
ni que no.

## Predicción firmada

1. Hará **entre 20 y 40 operaciones** en las veinte sesiones.
2. Su acierto quedará **entre el 30 % y el 45 %**, sin separarse del 33,3 % por
   encima de |z| = 1,96.
3. Su R neta será **negativa**, entre −0,2 y −0,5.
4. **No batirá a la regla mecánica** de forma significativa en esos mismos días.
5. Pondrá stops **más anchos que en agosto** —7 pips o más de mediana— porque
   ahora conoce la tabla del coste. Y eso, por sí solo, le mejorará la neta.

La 5 es la que más me interesa: si acierta, será la primera vez que algo medido
en este proyecto cambie por haberlo entendido.

## Qué contaría como hallazgo

R neta positiva con **z > +1,96**, o una diferencia contra la regla mecánica con
**z > +1,96** a su favor. Nada más cuenta.

## Ficheros

```
bt/examen_datos.py         genera las sesiones
data/examen_sesiones.json  lo que ve él, cortado en las 11:30
data/examen_dias.json      las fechas, que él no ve
paginas/examen.html        la página
```
