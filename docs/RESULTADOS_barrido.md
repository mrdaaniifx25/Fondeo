# Resultado · el barrido de liquidez

Ejecutado el 28 de agosto de 2026 según `docs/PREREGISTRO_barrido.md`.
Una sola pasada, con el arreglo de la mirada al futuro ya dentro.

## Los dos contrastes fallan

```
ASIA · 1.284 barridos en 2020-2025
  stop de la mecha (4,5p)   %TP 35,9 %   R/op +0,080   bruta/d +0,080 (z +1,99)
                                                       NETA/d  -0,289 (z -7,11)   PF 0,67

LONDRES del día anterior · 721 barridos
  stop de la mecha (4,9p)   %TP 32,6 %   R/op -0,020   bruta/d -0,020 (z -0,38)
                                                       NETA/d  -0,345 (z -6,61)   PF 0,61
```

La predicción firmada era que las dos sumas netas serían positivas. Salen
**−0,289 y −0,345**. Cae la familia entera.

Descriptivo, no preregistrado: con stop mínimo de 10 pips el neto de Asia sube
a −0,082 y el de Londres a −0,183. Mejor, y sigue en negativo.

En 2026 enero-julio el barrido de Londres da +0,301 bruto y +0,159 neto con
stop de 10, pero son **63 operaciones** y z +0,85. No es evidencia.

## Lo único positivo: el barrido de Asia tiene ventaja bruta

35,9 % de acierto contra el 33,3 % geométrico, R bruta +0,080 por operación,
z +1,99 sobre 1.284 operaciones. No cruza el umbral de Bonferroni de 2,24 con
dos contrastes, así que ni siquiera eso se puede dar por bueno. Pero apunta en
la misma dirección que todo lo demás.

## El resumen del proyecto entero, en una tabla

Cada familia probada, la ventaja bruta traducida a pips, y lo que cuesta:

```
  familia                          R bruta/op    stop   ventaja   coste   balance
  gatillo de continuación (2.080)      -0,057    7,0p    -0,40p   1,43p    -1,83p
  con filtro de contexto (938)         -0,023    7,0p    -0,16p   1,43p    -1,59p
  invertido del resto (1.142)          +0,109    4,8p    +0,52p   1,43p    -0,91p
  barrido de Asia (1.284)              +0,080    4,5p    +0,36p   1,43p    -1,07p
  barrido de Londres (721)             -0,020    4,9p    -0,10p   1,43p    -1,53p
```

**La ventaja, donde existe, vale entre 0,36 y 0,52 pips por operación. Operar
cuesta 1,43.** No es que no haya nada en los niveles de Asia: es que lo que hay
es tres o cuatro veces más pequeño que la fricción.

## La consecuencia, y es la única salida que queda

Para que 0,36 pips de ventaja paguen 1,43 de coste hay que **multiplicar el
tamaño de la operación por cuatro**: la misma ventaja en R, pero sobre stops de
18-20 pips en vez de 4-5.

Todo este proyecto se ha hecho en M5, donde los barridos dejan mechas de 4 pips.
La misma idea en M15 o M30, o en un instrumento con más recorrido por unidad de
spread, tendría el mismo R y una fracción del coste.

**Eso no está probado.** Es lo único de esta familia que queda sin mirar.
