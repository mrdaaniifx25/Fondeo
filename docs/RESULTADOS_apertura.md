# Resultado · barrido de la vela de apertura · EURUSD, GBPUSD, USDJPY

**Es lo primero de todo el proyecto que supera sus propios controles.**

Idea del usuario, no mía: *"mirar la primera vela de M15 que genera la
apertura, marcar máximo y mínimo y buscar un liquidity sweep en 5m"*.

Código en `bt/apertura_eurusd.py`, `bt/apertura_validacion.py`,
`bt/apertura_usdjpy.py`, `bt/apertura_regimen.py`, `bt/apertura_control.py`.

## Las reglas

    la PRIMERA vela de M15 de la apertura marca máximo y mínimo
    se espera que el precio barra uno de los dos extremos en M5 y CIERRE dentro
    confirmación: vela M5 de desplazamiento (cuerpo >= 50 % del rango)
    entrada a mercado en M1, tras el cierre de esa vela M5
    stop 3 pips más allá del extremo barrido
    objetivo 3R
    solo si el sesgo del día anterior va en esa dirección

    dispara 0,31 veces al día — una vez cada tres días
    hora de la apertura: 08:00 Londres (Fráncfort)

## El resultado, tres instrumentos

               mejor z   z>2    R>0    celda ganadora        R neta
    EURUSD      +4,72    6/36   11/36  08:00 buf3 rr3 bias   +0,4024
    GBPUSD      +4,70    6/36   11/36  08:00 buf3 rr3 bias   +0,3994
    USDJPY      +4,11    5/36   12/36  08:00 buf3 rr3 bias   +0,3419

**La misma celda gana en los tres**, y el orden interno se repite: Fráncfort >
Londres > Nueva York, buffer 3 > buffer 1, 3R > 2R, y las seis mejores de cada
par llevan el filtro de sesgo activado.

USDJPY es la réplica que cuenta: EURUSD y GBPUSD correlacionan al 0,85 y son
casi el mismo mercado; el yen no.

## Los controles

### Nulos · 4 rejillas sobre EURUSD con los bloques permutados

    REAL     +4,72     6/36 celdas z>2     11/36 celdas R>0
    nulo 1   +2,27     1/36                 5/36
    nulo 2   +2,02     1/36                 7/36
    nulo 3   +1,41     0/36                 6/36
    nulo 4   +1,77     0/36                 5/36
             media +1,87

Lo real está al doble del mejor nulo. Todo lo demás del proyecto -EMA+Fibo,
la búsqueda con árboles, el barrido asiático, el London sweep- caía DENTRO
del rango de sus nulos.

### Fuera de muestra · ajuste 2020-2023, prueba 2024-2026

    correlación ajuste / fuera de muestra (36 celdas)   +0,935
    la mejor del ajuste (z +3,89)  ->  fuera z +1,85, R +0,2498
    celdas positivas fuera de muestra                   11/36

Comparación con lo que ha muerto en esta misma prueba:

    rotura de canal simétrica     -0,429    elegir por el ajuste llevaba a lo peor
    cortacircuitos del oro        -0,002    información cero
    ESTA                          +0,935

Matices honestos: el z fuera de muestra es **+1,85, no llega a 2** -con dos
años y medio la potencia no da para más-, y la R baja de +0,40 a +0,25, que
es el encogimiento normal al quitar el periodo de ajuste. **Cuenta con
+0,25.**

### Regímenes de volatilidad

Probado a raíz de un vídeo que afirma que la volatilidad MEDIA es el mejor
régimen. En esta estrategia sale lo contrario:

     régimen     n    % del total    R neta       z    acierto
        BAJA   223        50,8 %    +0,5424   +4,06    43,5 %
       MEDIA    75        17,1 %    +0,1360   +0,61    33,3 %
        ALTA   141        32,1 %    +0,3077   +1,88    36,9 %
       TODOS   439       100,0 %    +0,3976   +4,23    39,6 %

El grueso de la ventaja está en volatilidad BAJA. No invalida al vídeo -él
hablaba de otra estrategia sobre otro activo- pero sí desmiente que sea una
ley general del scalping.

Aviso: 3 subgrupos son 3 comparaciones. Pendiente de comprobar fuera de
muestra antes de convertirlo en regla operativa.

## Dos fallos míos en este mismo trabajo

1. **El pago con objetivo en el extremo opuesto.** Con rr=0 las ganadoras se
   puntuaban como 0,0 R en vez de su R real, porque el cálculo usaba la
   variable `rr` en vez de la distancia real al objetivo. Doce de las 36
   celdas estaban condenadas por un error de programación.

2. **"USDJPY: sin operaciones" era una unidad mal puesta, no un resultado.**
   `U` estaba fijado a 1e-4 para todos los pares y un pip de USDJPY es 1e-2:
   el filtro `rgo > 40*U` rechazaba cualquier stop mayor de medio pip.
   **Era el fallo más peligroso del día**, porque parecía un resultado
   legítimo y encajaba con la historia de que la del oro tampoco generalizaba.
   Corregido también el coste de GBPUSD, que usaba 1,43 en vez de 1,60 y
   jugaba a favor de la estrategia.

## Lo que falta

    · control positivo (corriendo): comprobar que el motor detecta una
      ventaja inyectada, o sea que no está roto en la otra dirección
    · la R fuera de muestra es +0,25 con z +1,85: consistente, no demostrado
    · sin datos de spread reales del usuario para GBPUSD y USDJPY
    · nunca se ha operado hacia delante: cero evidencia en tiempo real

---

# RETRACTADO · el resultado era una mirada al futuro

**Todo lo de arriba queda anulado.** El filtro de sesgo usaba el cierre diario
del PROPIO día:

    b1 = np.sign(D1.c.diff())        # velas diarias
    sg = int(b1[k])                  # sesgo del dia k

`b1[k]` es el signo del cierre de hoy contra el de ayer. Operando a las 08:00,
ese cierre ocurre **16 horas despues**. Comprobado con fechas reales:

    k= 500   el cierre usado termina  2021-12-03 00:00
             pero se opera a las      2021-12-02 08:00

5 de 5 comprobaciones miran al futuro. Y era la pieza central: **las seis
mejores celdas de los tres instrumentos llevaban el sesgo activado.**

## El resultado con el sesgo corregido

Sesgo = signo(cierre[k-1] − cierre[k-2]), los dos cerrados antes de que
empiece el dia k. Codigo en `bt/apertura_v2.py`.

     apert   buf   rr   bias      n    R neta       z
     09:00   3.0    3   True    549   -0.2298   -3.13
     09:00   3.0    2   True    566   -0.1948   -3.26
     08:00   3.0    2   True    596   -0.1957   -3.36
     08:00   3.0    2  False   1126   -0.1481   -3.46
     08:00   3.0    3   True    570   -0.2502   -3.51

     mejor z -3.13  ·  celdas z>2: 0/24  ·  celdas R>0: 0/24

**Las 24 negativas.** Y las celdas SIN filtro de sesgo tambien pierden, asi
que el barrido de la vela de apertura no tiene nada por si solo.

## Queda anulado

    el z +4,72 de EURUSD
    la replica en GBPUSD (+4,70) y USDJPY (+4,11)
    la correlacion ajuste/fuera de muestra de +0,935
    los cuatro nulos superados
    el analisis por regimen de volatilidad
    la cartera de siete instrumentos

Todo eso validaba una estrategia que incluia el fallo. El metodo era correcto;
lo que validaba, no.

## Por que se encontro tarde

Se reviso por adelantado la mirada al futuro en la vela de entrada y en el
momento de la confirmacion. **No se reviso la causalidad del filtro de
sesgo**, que es donde estaba. Aparecio al repasar el codigo para contestar a
la pregunta "¿que porcentaje de validacion lleva?".

Cuatro horas presentado como el hallazgo del proyecto.
