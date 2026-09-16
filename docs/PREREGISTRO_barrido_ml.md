# Pre-registro · ¿se puede mecanizar la elección de la entrada?

Escrito **antes** de construir el conjunto y antes de entrenar nada.

## Por qué ahora sí y antes no

Su objeción, literal: *"sabiendo esta info... no me digas que no se puede
mecanizar o encontrar el patrón"*. Tiene razón en empujar, porque el material
disponible ha cambiado.

Hasta hoy se probaban **reglas escritas a mano**. Ahora existe lo que hacía falta
para el problema de verdad: para cada uno de los **16.219 barridos** y cada una de
las **13 velas** en las que se puede entrar, se sabe si esa entrada llegaba al
objetivo o se comía el stop. Son unas **200.000 filas etiquetadas**.

Eso es un problema de aprendizaje supervisado bien planteado, y no se ha
intentado a esta escala. Merece intentarse en serio antes de decir que no.

## La pregunta exacta

No es "¿gana el barrido?". Es:

> Dadas las velas hasta este minuto, **¿merece la pena abrir aquí?**

## Los datos

Todos los barridos de EURUSD 2020-2026, Londres y Nueva York, tal y como los
define `bt/barrido_sesion_v2.py`. Para cada barrido, las 13 velas de M5
siguientes. Etiqueta: R neta de entrar en esa vela, con coste 1,43 pips.

## Las variables, todas causales

Se calculan **solo con lo ocurrido hasta el cierre de la vela de entrada**. Es el
punto donde el proyecto ya se pilló una fuga en agosto, así que van auditadas una
a una y se declara aquí la lista:

- velas transcurridas desde el barrido
- riesgo en pips hasta el extremo del barrido, y el coste como % de ese riesgo
- profundidad del barrido: cuánto se pasó del nivel
- cuerpo y mechas de la vela del barrido
- a qué distancia del nivel está el precio ahora
- recorrido disponible hasta el extremo opuesto de la sesión de referencia
- ancho del rango de referencia, y ATR de M5 y de H1
- sesión, hora, día de la semana, lado
- rentabilidad de las últimas 3, 6 y 12 velas
- si ya hubo otro barrido del mismo nivel ese día, y cuántos
- si el precio ha cerrado más allá del extremo de la vela del barrido

## El método

Bosque de árboles con gradiente (`sklearn`), objetivo la R neta.

**Validación hacia delante, sin excepción.** Se entrena con los años anteriores y
se predice el siguiente: entrenar 2020-21 y predecir 2022, entrenar 2020-22 y
predecir 2023, y así hasta 2026. Nunca se usa el futuro.

**Nulo:** el mismo proceso completo con las etiquetas barajadas dentro de cada
mes, 20 repeticiones. Da el rango de lo que este método consigue sobre datos sin
señal.

**Y una auditoría de fuga**, porque el nulo no la detecta: cada variable por
separado, mirando si alguna mueve la R más de lo que puede saber.

## El criterio, fijado ahora

Se selecciona el **decil superior** de la predicción, fuera de muestra.

**Se considera que se puede mecanizar si se cumplen las tres:**

1. la R neta del decil elegido tiene su **IC95 entero por encima de cero**
2. esa mejora **supera el rango de los 20 nulos**
3. quedan **al menos 300 operaciones** en los cinco años fuera de muestra

Las tres. Si sale positivo pero deja 40 operaciones, no sirve para operar y se
dirá así.

## Lo que se informa pase lo que pase

La curva completa de decil a decil, no sólo el mejor. La importancia de cada
variable. El resultado por año. Y el recuento de operaciones de cada corte.

## Lo que ya sabemos y acota la esperanza

Entrar en cualquier vela fija da entre −0,83 y −1,31 de R neta. Para que el decil
superior cruce cero, el modelo tiene que encontrar **casi una R entera** de
diferencia. Es mucho. Pero el sitio donde buscarla existe: en un barrido típico
ganan 2 de 13 velas, así que la información, si está, está en cuál de las dos.
