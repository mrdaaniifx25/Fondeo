# Preregistro · el examen de las roturas

Escrito antes de que lo haga. Es el experimento invertido: en vez de que él busque
entradas, se le enseñan las que su propia regla genera y solo dice **entro / no
entro**.

## Por qué

Su regla —el cuerpo de la última vela de M5 cerrada, roto por el cierre de una
vela de M1— cubre el **83 %** de sus 223 entradas. Pero genera **38 roturas por
sesión** y él toma **1,36**: una de cada 28. Operada a ciegas da **31-38 %**; sus
elegidas dan **64,8 %**.

**Los veintisiete puntos de diferencia son la selección**, y en cinco bloques no
he conseguido medirla, porque para medirla hacen falta sus rechazos y solo
consigo sus aceptaciones. En el bloque 5 pedí que marcara los descartes y salieron
tres.

Esto lo arregla por construcción: cada rotura que se le enseña es un rechazo o una
aceptación, quiera o no.

## Diseño

- **10 sesiones nuevas**, sin solapamiento con las 164 anteriores.
- Su regla genera 49,6 roturas por sesión. Se **submuestrean 25 al azar** con
  semilla fija —sin filtrar por nada— para que sean 250 decisiones y no 496.
- De cada rotura se le enseña el gráfico **congelado en ese minuto**: H4, M15, M5
  y M1, los niveles de Asia, y el cuerpo de la vela de M5 que se acaba de romper.
- La dirección **la da la rotura**, no él. Él solo dice entro o no entro.
- El stop es el suyo medido —el extremo de los últimos diez minutos, 1,3 pips de
  error— y el objetivo 1:2. Así cada decisión es **un solo toque**.
- Se le enseña el desenlace después de decidir, como en los bloques anteriores y
  como en la vida real.

**Caveat declarado**: ver el desenlace le deja aprender dentro de la sesión. Se
acepta porque así opera de verdad, y porque quitarlo cambiaría la tarea.

## Contraste principal

**El acierto de las roturas que acepta contra el de las que rechaza.**

```
si las que acepta ganan mas   ->  su seleccion es real y esta medida por fin
si empatan                    ->  la seleccion no aporta nada, y sus 223 fueron
                                  una racha muy larga o un artefacto del formato
```

Umbral: **z > +1,96** a una cola en la diferencia de acierto.

**Potencia**: la regla acierta el 27,6 % sobre estas 250. Si acepta unas 25 y
acierta el 60 %, contra el 25 % de las 225 rechazadas, sale z ≈ +3,5. Con 15
aceptadas todavía sale z ≈ +2,7. **Está bien dimensionado incluso si es muy
selectivo.**

## Un sesgo del material, declarado antes de verlo

Las 250 roturas tienen un **stop mediano de 4,2 pips** y el 47 % está por debajo
de 4. Sus 223 entradas reales tienen 5,6 de mediana. Es decir: **las roturas que
su regla genera son más estrechas que las que él acaba tomando.**

No se filtran. Si rechaza sistemáticamente las de stop pegado, *eso es el
hallazgo* y hay que poder verlo. Queda declarado como candidato:

```
la anchura del stop es un discriminador posible entre sus aceptadas y sus
rechazadas, y se mira antes que ninguna otra variable.
```

Con todo, la anchura no puede ser la explicación entera: a 4,2 pips el equilibrio
está en el 44,6 % y a 5,6 en el 41,3 %. Son tres puntos. Él saca veintisiete.

## Declarados de antemano como secundarios

1. Cuántas acepta: se espera entre el 4 % y el 15 %.
2. Si acepta más al principio de cada sesión que al final.
3. Qué distingue a las aceptadas de las rechazadas en las variables ya medidas
   —hora, distancia al nivel de Asia, cuerpo de la vela de M5, cuerpo de la de
   M1, envolvente— ahora con el grupo de control correcto.
4. La envolvente de M1, que en las 223 dio 84,0 % contra 62,2 % con p = 0,043.

## Predicción firmada

1. Aceptará **entre 20 y 45** de las 250.
2. Las aceptadas acertarán **entre el 45 % y el 65 %**, contra el 27,6 % de la
   regla. Pasará el umbral.
3. Pero **por debajo de su 64,8 % habitual**, porque aquí no elige el momento:
   se lo dan hecho, y parte de lo suyo puede estar en *cuándo mira*, no solo en
   *qué elige*.
4. **La hora será lo que más separe** a las aceptadas de las rechazadas, como en
   todo lo anterior.
5. La envolvente de M1 **volverá a aparecer más en las aceptadas** que en las
   rechazadas.

Si la 2 falla —si acepta y rechaza con el mismo acierto— es el resultado más
importante del proyecto, y significa que sus 223 operaciones no venían de una
selección sino de otra cosa que el formato del examen le daba.
