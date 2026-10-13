# Resultado · ¿qué diferencia al CRT que gana del que pierde?

Pregunta del usuario: *"no hay manera de encontrar el punto en el cual ese
ganador se diferencie de los otros? un patrón, un orderblock, fvg, patrón de
vela...? algo tiene que existir que los diferencie."*

Código en `bt/crt_que_diferencia.py`. **19.553 setups CRT en H4, seis
instrumentos.** Acierto global 42,2 %, R neta media −0,0815.

Probar las cosas de una en una es débil: cada una por separado puede no verse y
aun así haber señal en la combinación. Así que se le dan **30 variables a la
vez** a un modelo de árboles, con validación hacia delante (entrena solo con
los años anteriores) y nulo.

## Lo que preguntaba, una a una

Diferencia en R neta entre el quintil alto y el bajo de cada variable:

              variable  quintil bajo  quintil alto       dif
       hay FVG a favor       -0,0715       -0,0947    -0,0232
        tamaño del FVG       -0,0715       -0,1025    -0,0310
         FVG en contra       -0,0894       -0,0528    +0,0366
    tamaño order block       -0,1204       -0,0923    +0,0281
             OB grueso       -0,0862       -0,1008    -0,0146
       distancia al OB       -0,0694       -0,1053    -0,0359
     cuerpo de la vela       -0,0940       -0,0897    +0,0043
        mecha superior       -0,0818       -0,0601    +0,0217
        mecha inferior       -0,0853       -0,0943    -0,0090
            envolvente       -0,0725       -0,1267    -0,0542

**Todas negativas en los dos extremos.** Ninguna separa ganadores de
perdedores: separan *pérdidas grandes* de *pérdidas algo menores*. Y varias van
al revés de lo que dice la teoría: tener un FVG a favor es **peor** (−0,0232),
un order block grueso es **peor** (−0,0146), y la vela envolvente es la peor de
todas (−0,0542).

Eso incluye la afirmación de Brad Gould sobre el order block "grueso y pesado":
medida aquí, no se sostiene.

## Las 30 juntas, con un modelo

    n fuera de muestra                          16.822
    correlación predicción-resultado (IC)      +0,0268
    R neta del quintil que el modelo prefiere  -0,0676
    R neta de todas                            -0,0880
    mejora                                     +0,0204

    nulos (mismo proceso, resultado barajado por meses):
      IC      de -0,0059 a +0,0057
      mejora  de -0,0122 a +0,0193

El IC sí supera a los nulos: hay **algo** de información. Pero es tan poca que
**el mejor quintil que el modelo sabe elegir sigue perdiendo 0,0676 R por
operación**, y la mejora (+0,0204) cae dentro del rango que el mismo modelo
consigue sobre datos barajados (+0,0193).

Con 30 variables y un modelo que busca cualquier combinación, no hay forma de
separarlos. Si existiera un patrón, un order block o una vela que lo hiciera,
el modelo lo habría encontrado: para eso está.

## Lo único que sí ordena el resultado, y no es un patrón

    coste/riesgo      n   coste medio   R BRUTA    R NETA
      1 muy bajo   3911         2,1 %   +0,0125   -0,0083
               2   3910         4,5 %   +0,0071   -0,0374
               3   3911         7,1 %   +0,0297   -0,0409
               4   3919        11,0 %   -0,0112   -0,1210
       5 muy alto   3902        24,9 %   +0,0489   -0,2003

La columna bruta no ordena nada —va dando tumbos entre +0,007 y +0,049— y la
neta cae en escalera perfecta con el coste. **Lo que distingue una operación
buena de una mala no es su forma: es cuánto se lleva el coste de su riesgo.**

Y aun así el mejor quintil, el de coste 2,1 %, se queda en **−0,0083**: casi
cero, todavía negativo.

## El fallo, y la lección que vale más que el resultado

La primera versión dio **IC +0,2725 contra nulos de ±0,01** — veinte veces la
separación. Era una mirada al futuro: la posición del cierre dentro del rango
del día se calculaba con el rango **completo** del día, velas posteriores a la
entrada incluidas.

Lo importante es **por qué el nulo no lo detectó**:

> Un nulo que baraja el RESULTADO no puede detectar una fuga metida en una
> VARIABLE. Si la variable ve el futuro, con el resultado barajado tampoco
> predice nada, así que el nulo sale limpio y la fuga pasa.

Se detectó mirando la tabla de variables sueltas y viendo que `pos_dia` movía
+0,12 R, que era demasiado para lo que esa variable puede saber. **Las
variables hay que auditarlas una a una; el nulo no las cubre.**

Corregido a máximo y mínimo acumulados dentro del día en curso, el IC baja de
+0,2725 a +0,0268.
