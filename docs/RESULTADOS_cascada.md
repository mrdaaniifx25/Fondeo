# Resultado · la cascada de sesiones

Ejecutado el 28 de agosto de 2026 según `docs/PREREGISTRO_cascada.md`.
Una sola pasada. `bt/cascada.py`.

## El contraste principal falla

```
M15 · una por día · 2020-2025
  1.421 operaciones · stop mediano 5,2 p · acierto 35,5 %
  R/op +0,096 · bruta/día +0,096 (z +2,53) · NETA/día -0,230 (z -5,99) · PF 0,72
```

La predicción firmada era neta positiva. Sale **−0,230**. M30 igual: −0,210.

## Y mi razón para esperar el cambio era falsa

Escribí en el preregistro: *«en M15 el stop pasa de 4-5 pips a 10-14 por
escala»*. No pasa:

```
  M5  (barrido de Asia)   stop mediano 4,5 p
  M15 (cascada)           stop mediano 5,2 p
```

**La mecha que asoma por encima del nivel no escala con la temporalidad.** La
fija la microestructura del barrido, no el tamaño de la vela. Eso cierra la vía
de «lo mismo en una temporalidad mayor», que era la última que quedaba.

## Su idea sí aparece en los datos

Los dos cortes que declaré de antemano salen en la dirección que él decía:

```
  por sesión                    n     %TP     R/op   z bruta
    Asia                      458   34,3%   +0,034    +0,51
    Londres                   697   37,3%   +0,129    +2,34
    NY                        266   33,1%   +0,118    +1,38

  por antigüedad del nivel      n     %TP     R/op   z bruta    c*
    de la sesión anterior   1.055   34,9%   +0,067    +1,53   0,45p
    2 a 4 sesiones            279   38,4%   +0,190    +2,19   0,99p
    5 o más                    87   34,5%   +0,142    +0,93   0,73p
```

**Los niveles viejos van mejor que los recientes**, que es exactamente lo que él
describía: el precio va a buscar liquidez que quedó sin mitigar hace sesiones,
no la de hace una hora.

## El corte que casi llega, y por qué no vale

Cruzando los dos — Londres **y** niveles de 2 a 4 sesiones — salen 150
operaciones con **42,7 % de acierto**, R/op +0,298 y **coste de equilibrio 1,54
pips**, por encima del coste real de 1,43. Binomial contra el 33,3 %: p = 0,011.

**Ese cruce no estaba declarado.** Y no aguanta:

```
  2020-2025      150 operaciones · 42,7 % · neta/día +0,021 · z +0,18 · PF 1,03
  2026 ene-jul    11 operaciones · 18,2 % · neta/día -0,783 · z -2,14 · PF 0,28
```

Ni siquiera dentro de la muestra donde lo he encontrado es significativo en neto
(z +0,18), son 25 operaciones al año, y fuera de muestra se cae. No hay nada que
operar aquí.

## El resumen de todo el proyecto

Cada familia probada, con la ventaja bruta traducida a pips:

```
  familia                          R bruta/op    stop   ventaja   coste   balance
  gatillo de continuación (2.080)      -0,057    7,0p    -0,40p   1,43p    -1,83p
  con filtro de contexto (938)         -0,023    7,0p    -0,16p   1,43p    -1,59p
  invertido del resto (1.142)          +0,109    4,8p    +0,52p   1,43p    -0,91p
  barrido de Asia M5 (1.284)           +0,080    4,5p    +0,36p   1,43p    -1,07p
  barrido de Londres M5 (721)          -0,020    4,9p    -0,10p   1,43p    -1,53p
  cascada M15 (1.421)                  +0,096    5,2p    +0,50p   1,43p    -0,93p
  cascada M15, niveles 2-4 (279)       +0,190    6,4p    +1,22p   1,43p    -0,21p
```

**La ventaja existe y se repite: entre 0,36 y 1,22 pips por operación.** El stop
se queda entre 4,5 y 6,4 pips en todas, porque lo fija el barrido y no la
temporalidad. Y operar cuesta 1,43.

No es que no haya patrón en los niveles de sesión. Es que **el patrón vale
alrededor de un pip y recogerlo cuesta pipa y media**.

## La única palanca que queda no es la estrategia

Es el coste. Los costes de equilibrio medidos:

```
  todo M15                        0,42p
  sólo Londres                    0,60p
  niveles de 2-4 sesiones         0,99p
```

Con un coste total de 0,6 pips —spread raw de 0,2 más 3,5 $/lote de comisión,
que es lo normal en una cuenta directa— varios de estos cortes cruzan el cero.
Con los 1,43 de la cuenta de fondeo, ninguno.

Aviso: esos coste de equilibrio salen de cortes hechos dentro de la muestra. No
son una promesa. Pero sí señalan dónde está el problema, y no está en la idea.
