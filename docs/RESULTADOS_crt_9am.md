# Resultado · el modelo "9 a.m. CR" y las dos reglas mecánicas de Brad Gould

Código en `bt/crt_9am.py`. Cinco instrumentos, 2020-2026, 386.606 filas
(24 combinaciones por señal). z con error estándar agrupado por
instrumento-día.

## Qué se midió

Del vídeo de backtesting del modelo de las 9:00:

    "the 8 a.m. candle range high and low on the 1 hour, and the 9:00 a.m.
     candle range high and low on the 15 minute. these are the two steps"
    "you target the 1 hour high ... partials at the midpoint"

Esto sí era nuevo: **el ancla horaria fija**. Todos los CRT anteriores de este
repositorio usaban rangos rodantes vela a vela. Aquí el rango es siempre el
mismo par de velas de reloj.

Del vídeo de Brad Gould, sus dos únicas afirmaciones mecánicas (el resto
—order blocks "gruesos y pesados", trades "A+"— no es especificable):

    stop encima de la VELA DE LIQUIDACIÓN, no encima del extremo del rango
    agresiva = entrar al cierre de vuelta dentro
    conservadora = esperar el retroceso al 50 % de la vela de liquidación

**Celda primaria declarada antes de mirar:** ancla 09, rango M15, entrada
agresiva, stop en la vela de liquidación, objetivo el extremo opuesto del H1.

**Control de detección:** el mismo modelo anclado a otras horas de Nueva York.
Si las 9:00 tienen algo, el ancla 09 tiene que separarse de las demás.

## 1 · La celda primaria es exactamente el azar

    n 5.746   R:R 3,31   acierto 37,3 %   geométrico 37,4 %
    R BRUTA +0,0146 (z +0,61)     R NETA -0,2053

Y los tres objetivos, cada uno clavado en su propia línea de azar:

    objetivo     n    R:R  acierto  geométrico   R BRUTA       z
          3R  6064   3,00   28,3 %      25,0 %   -0,0073   -0,35
         50%  3687   1,96   48,4 %      48,8 %   -0,0023   -0,10
          CR  5746   3,31   37,3 %      37,4 %   +0,0146   +0,61

Esto es el teorema de barrera dibujado: cambias la geometría y el acierto se
mueve con ella, punto por punto, sin dejar residuo.

## 2 · El control de detección tumba la hora

    ancla NY     n    R:R  acierto   R BRUTA       z    R NETA
       3:00   6142   2,92   39,3 %   +0,0779   +3,27   -0,1601
       6:00   5491   2,74   38,7 %   -0,0057   -0,26   -0,2717
       9:00   5746   3,31   37,3 %   +0,0146   +0,61   -0,2053   <- el modelo
      12:00   5540   3,54   34,9 %   +0,0025   +0,10   -0,2432
      15:00   4471   3,21   37,3 %   -0,0257   -1,08   -0,2861

**Las 9:00 de Nueva York son la tercera de cinco.** El ancla que gana es la de
las 03:00 NY, que es la **apertura de Londres** — y gana por un margen que no
se parece al de las demás: z +3,27, positiva en **5 de 5 instrumentos** y en
**6 de 7 años**.

    instr        BRUTA       z   |    año     BRUTA       z
    EURUSD     +0,0457   +0,94   |   2020   +0,1045   +1,74
    GBPUSD     +0,0953   +1,78   |   2021   -0,0320   -0,59
    NAS100     +0,0797   +1,43   |   2022   +0,0633   +1,13
    SPX500     +0,0680   +1,42   |   2023   +0,1029   +1,66
    USDJPY     +0,0957   +1,79   |   2024   +0,0874   +1,46
                                 |   2025   +0,0429   +0,65
                                 |   2026   +0,2476   +2,60

Es coherente con todo lo demás del repositorio (SMC-71, barrido de Londres):
la estructura que existe está en la apertura de Londres, no en la de Nueva
York. Y también acaba igual: **neta −0,1601.** El coste se la come.

Conviene decirlo con precisión: el ancla 03 era un **control**, no una
hipótesis. Son 5 comparaciones, así que z +3,27 sigue siendo notable
(p ≈ 0,003 tras corregir), pero no es un hallazgo preregistrado y no cambia
nada operable, porque la neta es negativa.

## 3 · Las dos reglas de Brad: una acierta y la otra al revés

**El stop.** 20 parejas (5 anclas × 2 rangos × 2 modelos de entrada),
comparando stop en la vela de liquidación contra stop en el extremo del rango:

    la vela de liquidación gana en 19 de 20   (prueba de signos p ≈ 4·10⁻⁵)

**Tenía razón.** Y se puede decir por qué, midiendo el exceso sobre el azar
geométrico (acierto real menos 1/(1+R:R)):

    stop                entrada        n    R:R  acierto   geom   exceso
    liquidación        agresiva    54766   3,20   32,9 %  35,7 %   -2,8 %
    liquidación    conservadora    37443   6,15   16,5 %  18,9 %   -2,4 %
    rango              agresiva    29691   6,25   23,1 %  24,3 %   -1,3 %
    rango          conservadora    13947   7,88   13,6 %  17,7 %   -4,1 %

El stop pegado al extremo del rango es más estrecho, así que da mejor R:R —
pero lo saltan por debajo de lo que la geometría compensa. Su recomendación
("based on data, not vibes") es correcta.

**La entrada.** Mismas 20 parejas:

    la agresiva gana en 19 de 20   (prueba de signos p ≈ 4·10⁻⁵)

**Esperar el retroceso al 50 % de la vela de liquidación empeora el
resultado**, de forma sistemática y en todas las combinaciones. Y la razón no
es el precio de entrada, que es mejor: es la **selección**. Los días en que el
precio vuelve a buscarte son los días en que el movimiento no iba a ir. Te
quedas con el subconjunto malo.

Esto contradice el marco del vídeo, que presenta agresiva y conservadora como
cuestión de tolerancia al riesgo. No lo son: una es medible y peor.

## Conclusión

- El modelo de las 9:00 **no tiene ventaja**: +0,0146 bruto, z +0,61, y los
  tres objetivos clavados en su línea de azar. Neta −0,21.
- **La hora no es esa.** Su propio control de detección señala la apertura de
  Londres, que también muere en el coste.
- De las dos reglas mecánicas de Brad Gould, **la del stop es correcta** y
  replica 19/20; **la de la entrada conservadora es incorrecta** y replica
  19/20 en contra.

Las dos reglas del stop y la entrada no crean ventaja: deciden cuánto se
conserva de la línea de azar. Son las primeras piezas de todo el material de
vídeo que se han medido correctas y reproducibles, y siguen sin ser una
estrategia.
