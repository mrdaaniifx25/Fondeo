# Resultados · doble barrido con el stop en el barrido de 4h

Pre-registro `cd653c2`, escrito antes de medir. Código en
`bt/doble_barrido_stop.py`. Idéntico a la prueba anterior salvo el stop.

## La tabla

| par | entra | n | acierto | riesgo | coste %R | R bruta | **R neta** | IC95 | z |
|---|---|---|---|---|---|---|---|---|---|
| **12h+4h** | **M15** | 3.966 | 37,5 % | 16,3 | 8,2 % | +0,1241 | **+0,0133** | [−0,040, +0,067] | +0,49 |
| 12h+4h | M5 | 11.689 | 35,9 % | 15,1 | 8,9 % | +0,0759 | −0,0516 | [−0,091, −0,012] | −2,57 |
| 8h+4h | M15 | 5.553 | 35,7 % | 15,8 | 8,2 % | +0,0724 | −0,0365 | [−0,081, +0,008] | −1,59 |
| 8h+4h | M5 | 16.367 | 35,7 % | 14,3 | 9,1 % | +0,0701 | −0,0591 | [−0,092, −0,026] | −3,49 |
| 4h+2h | M15 | 6.423 | 35,1 % | 11,1 | 11,5 % | +0,0542 | −0,1000 | [−0,138, −0,062] | −5,17 |
| 4h+2h | M5 | 18.256 | 37,1 % | 9,9 | 13,1 % | +0,1127 | −0,0733 | [−0,100, −0,046] | −5,32 |

**El criterio no se cumple.** El intervalo de la celda principal incluye el cero.

## Las tres predicciones

| | predicción | resultado |
|---|---|---|
| 1 | el coste bajará por debajo del 10 % | ✔ del 19,6 % al **8,2 %** |
| 2 | la bruta en R **bajará** | **✘ y esto es lo interesante** |
| 3 | la neta quedará entre −0,05 y +0,05 | ✔ +0,0133 |

**La predicción 2 falló, y falló a favor.** Al triplicar el ancho del stop —de
6,8 a 16,3 pips— la ventaja bruta **no se movió**: +0,1228 antes, +0,1241 ahora.

Eso significa que el patrón **no depende de la escala**. No estaba capturando un
tirón de seis pips: la ventaja sigue ahí cuando le das al precio tres veces más
sitio. Es lo que hacía falta para que el ensanchamiento del stop sirviera de algo,
y es un resultado con contenido propio.

Y por primera vez en todo el proyecto, **una neta agregada sale positiva**:
+0,0133.

## Por qué no basta, y hay que decirlo entero

**1 · Es indistinguible de cero.** z +0,49. El intervalo va de −0,040 a +0,067.

**2 · No hay forma de resolverlo con estos datos.** Para que +0,0133 llegue a
z = 2 harían falta **38.467 operaciones**. Hay 3.966. Son diez veces más datos de
los que existen en el barrido entero de 2020-2026.

**3 · Todo el positivo lo pone un instrumento.**

```
celda principal        n 3.966    neta +0,0133
sin NAS100             n 3.484    neta -0,0085    z -0,29
```

NAS100 aporta +0,1704 con 482 operaciones. Quitándolo, el agregado se vuelve
negativo. Es exactamente el patrón que hundió a la familia EMA+Fibo+estocástico
en agosto: un efecto que vive en un instrumento y desaparece en los demás.

## Y en EURUSD, que es lo que él preguntó

```
EURUSD    n 1.001    acierto 36,6 %    riesgo 13,0 p    coste 11,0 %
          bruta +0,0969    NETA -0,0450    z -0,83    IC95 [-0,152, +0,062]
```

**Negativa.** Con la ventaja bruta intacta (+0,0969) pero un stop más estrecho
que el de los demás —13 pips frente a los 18,9 de GBPUSD o los 41,6 de NAS100—,
el peaje sube al 11 % y se lleva la ventaja.

Por instrumento, la celda principal:

| instrumento | n | riesgo | coste %R | R bruta | R neta |
|---|---|---|---|---|---|
| NAS100 | 482 | 41,6 | 3,6 % | +0,2199 | **+0,1704** |
| USDJPY | 875 | 17,2 | 8,7 % | +0,1417 | +0,0203 |
| GBPUSD | 1.000 | 18,9 | 8,5 % | +0,1250 | +0,0141 |
| SPX500 | 608 | 9,4 | 6,4 % | +0,0658 | −0,0269 |
| **EURUSD** | 1.001 | 13,0 | 11,0 % | +0,0969 | **−0,0450** |

El orden de la columna de la neta es casi exactamente el orden inverso del coste.
Otra vez la misma división.

## Veredicto

Por el criterio escrito de antemano: **no se cumple**. La familia del doble
barrido se cierra como estrategia operable.

Lo que deja, y no es poco:

- **La mayor ventaja bruta medida en el proyecto** (+0,124), y estable al
  triplicar el stop, o sea que es un efecto de escala amplia y no un artefacto de
  seis pips.
- **La confirmación de que el doble barrido anidado selecciona**, con gradiente:
  cuanto más separadas las temporalidades, más ventaja.
- Y la confirmación, por enésima vez, de que **el coste decide**: los tres
  instrumentos con stop ancho salen positivos y los dos con stop estrecho,
  negativos. EURUSD está entre los segundos.
