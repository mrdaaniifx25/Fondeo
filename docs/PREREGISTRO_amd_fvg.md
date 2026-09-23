# Pre-registro · AMD + FVG

Escrito antes de medir. Idea suya del 19-09-2026: juntar las dos cosas medidas.

## Por qué tiene sentido juntarlas

No es "apilar filtros hasta que salga". El FVG después de la manipulación es
**evidencia de que el giro tuvo fuerza**: si el precio se da la vuelta y deja un
hueco, se ha movido lo bastante rápido como para no dejar negociar a todo el
mundo por el camino. Eso no se ha exigido nunca en este proyecto.

## La regla

    A   rango apretado: n velas dentro de 0,90 x ATR x raiz(n)
    M   el precio sale del rango y CIERRA de vuelta dentro
    F   en las 5 velas siguientes se forma un FVG a favor del giro
        (bajista si barrió arriba, alcista si barrió abajo)
    D   cierre más allá del extremo contrario del rango

Entrada al cierre de la vela que completa el FVG. Stop en el extremo del
barrido. Objetivo, el extremo contrario del rango.

## Lo que se compara, declarado ahora

    CON FVG   contra   SIN FVG      sobre las mismas manipulaciones

Las dos ramas se informan siempre. Si la rama CON no supera a la SIN, la
combinación no aporta y se dice.

## Instrumentos y marcos

EURUSD, oro y DAX. M15 y H1. **Tres instrumentos es el requisito**: un hallazgo
que solo aparece en uno se descarta, como pasó con la afirmación 4 del FVG.

## Las dos preguntas

**1 · ¿Sube la tasa de completar?** Contra el listón de la geometría, como en el
estudio del AMD: `a/(a+b)` desde donde queda el precio.

**2 · ¿Da dinero?** R bruta y R neta. Coste 1,43 pips en EURUSD.

## El criterio

Para que merezca la pena seguir construyendo sobre esto:

1. la rama CON FVG tiene que **superar a la SIN FVG** en los tres instrumentos
2. su R **bruta** tiene que ser positiva con el IC95 entero por encima de cero
3. tienen que quedar al menos **200 operaciones** por instrumento

Las tres. Si falla una, se para aquí y no se añade nada más.

## Lo que se informa pase lo que pase

Las dos ramas, los tres instrumentos, los dos marcos, el número de operaciones y
el reparto del riesgo.

## El prior, dicho antes de mirar

El AMD solo dio bruta -0,04 (cero). El FVG aporta +2,4 puntos en otra pregunta
distinta. **Juntar dos casi-ceros no suele dar un positivo.** Si sale, será
sorpresa; si no sale, no será noticia.
