# Resultado · el patrón de sus capturas de demo, medido sobre 5 años

El usuario mandó seis operaciones en demo (EUR/USD M15, 6-13 octubre 2026) y
pidió medirlas. Sus datos son posteriores a mi histórico, así que **no se pueden
verificar esas seis**; lo que sí se puede es medir **el patrón** sobre
2021-2026. Código: `bt/su_patron_londres.py` y `bt/su_patron_controles.py`.

Sesiones tomadas literalmente de su gráfico —*«Sesiones Europe/Madrid 0000 0800
1400 2300»* y *«0800-1100 1300-1600»*—: **rango de Asia 00:00-08:00 Madrid**,
killzone de **Londres 08:00-11:00** y de **Nueva York 13:00-16:00**.

**El patrón**: dentro de la killzone, una vela M15 barre un extremo del rango de
Asia y cierra de vuelta dentro → se opera contra el barrido, stop tras la mecha,
objetivo en R. Coste ECN 0,70 pips.

---

## 1 · Londres, su ventana

```
                                 n  acierto   geom  exceso    BRUTA  z bru     NETA  z net
  SU PATRÓN · stop ATR        1281    35,8%  33,3%    +2,5  +0,0835  +2,12  -0,0208  -0,53
  SU PATRÓN · stop mecha      1281    35,1%  33,3%    +1,8  +0,0734  +1,86  -0,1236  -3,06
  CONTROL ciego               2942    34,4%  33,3%    +1,0  +0,0347  +1,92  -0,0921  -5,08
    ciego solo cortos         1471    33,9%  33,3%    +0,5  +0,0184  +0,50  -0,1084  -2,93
    ciego solo largos         1471    34,9%  33,3%    +1,5  +0,0510  +1,37  -0,0758  -2,03
```

**Lo bueno, y es la primera vez que puedo decirlo de algo suyo: la bruta es
positiva, con z +2,12.**

**Lo que lo mata: el control ciego también.** Entrar en la primera vela de las
08:00 sin mirar ningún nivel da bruta +0,0347 con z +1,92.

```
  DIFERENCIA patrón - ciego:  bruta +0,0489  (z +0,86)   ·   acierto +1,5 pp  (z +0,92)
```

**El barrido del rango de Asia aporta +1,5 puntos de acierto con z +0,9.** Ruido.

Lo que sí parece tener algo es **la ventana horaria en sí**: las 08:00-11:00 de
Madrid dan bruta positiva con o sin condición. Pero es +0,035 bruta contra un
coste del 12,7 %: no llega.

## 2 · El hallazgo accionable: su stop es demasiado estrecho

```
  stop en la mecha del barrido  ->  riesgo 5,2 pips  ->  coste 19,7 % del riesgo  ->  neta -0,1236
  stop en 1,5 x ATR(14)         ->  riesgo 7,1 pips  ->  coste 10,4 % del riesgo  ->  neta -0,0208
```

**Ensanchar el stop de la mecha a 1,5×ATR mejora el neto seis veces.** De −0,124
a −0,021. Sigue sin ser positivo, pero es la única palanca que mueve de verdad
el resultado, y es gratis: no requiere acertar más, sólo pagar menos horquilla.

Es el mismo resultado que salió en las 220 celdas de
`RESULTADOS_punto_optimo.md`: los stops anchos ganan de forma monótona.

## 3 · Nueva York: ahí no

```
                                 n  acierto   geom    BRUTA     NETA      z
  SU PATRÓN · stop ATR · NY    862    29,2%  33,3%  -0,0464  -0,1137  -2,60
  SU PATRÓN · stop mecha · NY  862    28,9%  33,3%  -0,0777  -0,2451  -5,12
  CONTROL ciego · NY          2936    29,4%  33,3%  -0,0552  -0,1206  -6,76
```

**La bruta es negativa en Nueva York**, y el acierto queda 4 puntos por debajo
del nulo geométrico. Su instinto de operar Londres está respaldado por los datos;
el mismo patrón en NY es claramente peor.

## 4 · Y aquí está la explicación de sus seis operaciones

Partiendo las 1.281 por **cuánto se movió la semana en la dirección de la
operación**:

```
  tramo                                  n  acierto    BRUTA     NETA
  semana >80 pips A FAVOR del lado     167    47,9%  +0,4491  +0,3514
  semana 0-80 pips a favor             413    39,0%  +0,1816  +0,0740
  semana EN CONTRA del lado            701    31,1%  -0,0613  -0,1653
```

**En semanas que se mueven 80+ pips a favor, el patrón da 47,9 % de acierto y
+0,35 de R neta por operación.** Es un resultado enorme.

Su semana: EUR/USD cayó de 1,1275 a 1,1155, **120 pips**, y cinco de sus seis
operaciones eran cortos. **Está exactamente en la primera fila.**

Esas seis operaciones son reales y están bien ejecutadas. Lo que no son es
evidencia de ventaja, porque **el patrón paga +0,35 en esas semanas y −0,17 en
las demás**, y no hay forma de saber de antemano en cuál está. La media de las
tres filas es el −0,0208 de la tabla 1.

## 5 · «Puedo demostrarlo con más ejemplos»

En las 1.281 operaciones del patrón, con su acierto neto real del 34,9 %:

```
  rachas de 6 ganadas seguidas  :  5 ventanas de 1.276
  racha máxima                  :  8 ganadas seguidas
  esperadas por azar            :  2,3
```

**Seis ganadas seguidas ocurrieron cinco veces en cinco años operando esto.** No
es raro: es lo esperable. Y una racha de ocho también apareció.

Por eso más capturas no resuelven nada. Lo que resuelve es el **registro
completo**: todas las operaciones, anotadas antes del resultado, incluidas las
perdedoras y las que vio y no tomó. Con cien de ésas se separa el timing de la
dirección de la semana. Con seis no.

## Lo que se lleva de aquí, en concreto

1. **Ensanche el stop** de la mecha a 1,5×ATR(14). Mejora el neto **seis veces**
   (−0,124 → −0,021). Es lo único medido que mueve el resultado.
2. **Quédese en Londres 08:00-11:00 y deje Nueva York.** La bruta es positiva en
   una y negativa en la otra.
3. **Lo que no aporta es el barrido del rango de Asia**: +1,5 puntos de acierto
   con z +0,9. Lo que aporta, si algo, es la hora.
4. **Y nada de esto lo pone en positivo.** La mejor celda es −0,0208 con z −0,53:
   indistinguible de cero, no por encima.
