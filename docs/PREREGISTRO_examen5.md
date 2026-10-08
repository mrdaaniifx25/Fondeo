# Preregistro · quinto bloque: los descartes

50 sesiones nuevas, cero solapamiento con las 114 anteriores.

## Por qué el indicador no es el cambio que importa

Él propone meter el indicador en el examen «a ver si aparece el patrón». El
indicador enseña lo que ya está medido; no genera información nueva sobre por qué
elige unas velas y no otras.

Lo que falta es otra cosa. El modelo predice **dónde** entra con AUC 0,800
comparando sus 150 entradas contra 3.400 velas cualesquiera. Lo que no predice es
**cuál** de las velas candidatas toma: sobre las velas que él también eligió, la
regla acierta el 55,9 %; sobre todas, el 34,7 %. Esos veinte puntos son el hueco.

Y para atacarlos hace falta el grupo de control correcto, que **no** son 3.400
velas al azar: son **las velas que él miró y descartó**. Esas ya pasaron su filtro
grueso, y la diferencia entre tomarla y no tomarla es exactamente lo que no sé
medir.

**La página lleva cuatro bloques tirando ese dato.** `cancela()` borra la caja y
no guarda nada. Es el error de diseño más caro del proyecto.

## Los tres cambios

**1 · Los descartes se registran, y sin fricción.** El botón «Cancelar» se
convierte en cuatro botones que cancelan *y* dicen por qué de un solo toque:

```
no me convence · falta confirmación · voy tarde · me he equivocado
```

Tiene que pulsar uno para cerrar la caja igualmente. No hay panel extra, no hay
paso adicional, no se puede olvidar como se olvidaron las etiquetas del bloque 4.

**2 · La confianza, también de un toque.** El botón «Confirmar entrada» se
convierte en tres:

```
Entro dudando · Entro normal · Entro claro
```

Si su confianza predice el resultado, es un filtro utilizable mañana mismo: se
opera solo lo claro, o se arriesga menos en lo dudoso.

**3 · El indicador, sorteado por sesión.** La mitad de las sesiones lo llevan y la
mitad no, echado a suertes con semilla fija y decidido antes de empezar. Así se
mide si ayuda en vez de suponerlo. Va declarado como secundario porque con 25
sesiones por rama solo detectaría un efecto grande.

## Contraste principal

**Sus entradas contra sus descartes, resueltos igual que si los hubiera tomado.**

Cada descarte se resuelve con el precio real: entrada al cierre de esa vela, stop
donde lo tenía puesto, objetivo 1:2, corte a las 11:30.

```
si sus tomadas ganan mas que sus descartadas   ->  su seleccion es real y esta
                                                   en algo que el ve y yo no
si empatan                                     ->  la seleccion no aporta; lo que
                                                   funciona es donde mira, no cual elige
si sus descartadas ganan mas                   ->  se esta filtrando en contra
```

Umbral: **z > +1,96** a una cola en la diferencia de acierto.

**Aviso de potencia, dicho antes**: para detectar 21 puntos de diferencia con un
80 % de potencia hacen falta unas 85 operaciones por grupo. Si descarta a un ritmo
parecido al que entra, 50 sesiones darán unos 65 de cada. **Es probable que este
bloque no baste solo** y haya que juntarlo con un sexto. Se dice ahora para que no
parezca una excusa después.

## Declarados de antemano como secundarios

1. Confianza contra resultado, en tres niveles.
2. El indicador contra el no indicador: acierto, R neta, número de operaciones.
3. El tamaño del cuerpo, **replicado hacia delante**: es el primer hallazgo del
   proyecto que separa sus ganadoras de sus perdedoras (50,0 % contra 78,0 %,
   p = 0,0006) y hasta ahora solo está confirmado hacia atrás.
4. Los tres umbrales de siempre —acierto, R neta, contra la regla— por continuidad.
5. Las cuentas de 10.000, que sigue.

## Predicción firmada

1. Descartará **entre 0,5 y 1,5 veces por sesión**, o sea entre 25 y 75 descartes.
2. Sus tomadas batirán a sus descartadas, **entre 10 y 25 puntos de acierto**,
   pero **sin llegar al umbral** por falta de muestra. z entre +1,0 y +1,9.
3. **La confianza sí separará**: lo que marque «claro» acertará entre 8 y 20
   puntos más que lo que marque «dudando».
4. **El indicador no cambiará su acierto** de forma apreciable —menos de 5 puntos
   de diferencia entre ramas— pero **reducirá el número de operaciones**, porque
   verá el aviso del cuerpo lleno y se saltará algunas.
5. **El hallazgo del cuerpo se replicará**: cuerpo lleno por debajo del 60 % de
   acierto, cuerpo normal por encima del 70 %.

La 5 es la que más me importa. Es la única cosa de este proyecto que ha separado
sus ganadoras de sus perdedoras, y hasta que no se replique en datos nuevos no es
una ley.

## Qué contaría como hallazgo

El principal, con z > +1,96. Y la 5, replicada. Cualquier otra cosa se reporta
como secundaria y exploratoria.
