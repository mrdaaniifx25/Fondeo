# Resultado · el CRT como contexto: la cascada hacia el objetivo superior

Sale de la clase en vídeo sobre rangos diarios del NASDAQ. Código en
`bt/crt_cascada.py`. Cinco instrumentos, 2020-2026, 6.422 entradas.

## Qué afirma, y por qué esto no estaba medido

    "nos crea un rango alcista un día, 4 horas, 1 hora, M15,
     y nos enfoca hasta el objetivo semanal"
    "yo no tengo por qué esperar que el precio vaya a completar el rango diario"
    "es simplemente esperar los rangos a favor del objetivo"

Esto **no** es lo que ya medí en `RESULTADOS_crt_semanal.md`. Allí el filtro
era la *dirección* de la semana anterior. Aquí hay dos cosas distintas:

1. **El objetivo vive en la temporalidad superior.** El stop lo pone M15 y el
   objetivo lo pone la semana. La vela de entrada no tiene que completarse.
2. **La cascada**: cuántas temporalidades intermedias (D1, H4, H1) están
   alineadas con el rango semanal en el momento de entrar.

Contraste primario declarado antes de mirar: R bruta según el número de
temporalidades alineadas. Es un contraste **interno** — los otros cubos son el
control, no hace falta nulo externo.

## Cómo se construye

Rango de cada temporalidad = vela **anterior ya cerrada**. "Activado" = la vela
en curso ya se llevó uno de los dos extremos (y no los dos). Todo se lee al
cierre de la vela M15 de confirmación; la entrada es en la apertura de la
siguiente. Máximo una operación por día. Horizonte: fin de la semana o 5 días.
z con error estándar agrupado por instrumento-semana.

## El resultado

    alineadas      n    R:R   R BRUTA       z    R NETA
            0   2413  66,63   +0,0451   +0,39   -0,2668
            1   1652  58,61   -0,1918   -1,73   -0,4927
            2   1265  52,61   +0,5230   +2,65   +0,2565
            3   1092  49,57   +0,0287   +0,20   -0,2053
        TODAS   6422  58,90   +0,0755   +1,04   -0,2114

Hay un cubo con z +2,65 y neta positiva. **No vale**, por tres razones que se
ven en la propia tabla:

- **No es monótono.** Si la cascada informara, más alineación sería mejor:
  0 → 1 → 2 → 3. Sale +0,05 / −0,19 / +0,52 / +0,03. Eso es ruido con forma.
- Son 4 cubos. Uno por encima de z=2 entre cuatro es lo esperable.
- El cubo de 3 alineadas —el que la teoría señala como el mejor— es cero.

## Lo que de verdad hace este montaje

Descomponiendo el 6,3 % de operaciones "en verde":

    objetivo semanal tocado       1,92 %   (azar geométrico 3,19 %)
    stop                         93,65 %
    ni uno ni otro, a mercado     4,44 %

**El objetivo semanal se alcanza MENOS que por azar puro.** 1,92 % contra un
3,19 % geométrico. La afirmación de la clase —"vais a ver muchísimos rangos que
se van completando"— es cierta mirando el gráfico hacia atrás y falsa como
apuesta: desde una entrada de M15, el rango semanal se completa la mitad de
veces de lo que daría una moneda con esa misma geometría.

Y el +0,0755 bruto tampoco es lo que parece:

    suma total          +484,8 R sobre 6.422 operaciones
    las 5 mejores       +385,5 R  = 80 % del total
    sin esas 5           +0,0155 R de media
    mediana                -1,000 R
    máximo                     96 R

Ochenta por ciento del resultado en **cinco operaciones de 6.422**. La mediana
es un stop completo. Eso no es una estrategia, es un billete de lotería con
0,08 % de acierto.

## El coste, otra vez

    coste/riesgo      n    R:R   R BRUTA   R NETA
     (0,00-0,05]    230  18,06   +0,1546  +0,1208
     (0,05-0,10]    612  28,99   +0,1354  +0,0584
     (0,10-0,20]   1626  40,81   +0,0848  -0,0660
     (0,20-0,40]   2361  60,95   +0,0088  -0,2757
     (0,40-9,00]   1593  91,73   +0,1304  -0,4161

El stop es una vela de M15: **en 3.954 de 6.422 operaciones el coste se lleva
más del 20 % del riesgo.** Es exactamente el muro de `COSTE_real.md`. Poner el
objetivo lejos no lo arregla, porque el coste no depende del objetivo, depende
del stop.

## Conclusión

**La cascada no aporta nada.** Ni el número de temporalidades alineadas ordena
el resultado, ni el objetivo semanal se alcanza más de lo que da el azar —
se alcanza menos. Bruta global z +1,04, neta −0,21 (z −2,92).

Lo que sí queda confirmado, por enésima vez: mover el objetivo lejos sin mover
el stop no crea ventaja, solo cambia la forma de la distribución.
