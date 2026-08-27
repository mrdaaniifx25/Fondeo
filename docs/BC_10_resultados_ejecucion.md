# BC_10 · Resultados · la temporalidad de ejecución

Pre-registro en `BC_09`, escrito antes de correr. La sospecha era razonable:
`EJEC_H = 1` estaba escrito a fuego en el motor y el material dice 15M y 10M.

## El resultado

Contexto 1D/12H/4H, lectura B, R:R ≥ 3, cinco instrumentos, 2020-2023. Lo único
que cambia es dónde se busca el rango de entrada.

| ejecución | n | ops/año | riesgo | R:R | %TP | **coste en R** | R bruta | **R neta** | z bloques | recortada |
|---|---|---|---|---|---|---|---|---|---|---|
| **1H** | 3.060 | 765 | 9,1 | 6,5 | 13,3 % | **13,1 %** | +0,024 | **−0,120** | −2,24 | −0,153 |
| 15M | 12.329 | 3.082 | 6,5 | 8,8 | 10,9 % | 18,3 % | +0,018 | −0,167 | −4,21 | −0,236 |
| 10M | 16.720 | 4.180 | 6,1 | 9,8 | 10,6 % | 19,6 % | +0,051 | −0,144 | −3,52 | −0,235 |
| 5M | 25.691 | 6.423 | 5,4 | 11,5 | 9,0 % | **22,0 %** | −0,025 | **−0,238** | −7,11 | −0,326 |

## Las cinco predicciones

1. **El R:R bruto sube al bajar.** ✔ 6,5 → 8,8 → 9,8 → 11,5
2. **La tasa de aciertos baja.** ✔ 13,3 % → 10,9 % → 10,6 % → 9,0 %
3. **El coste en R sube.** ✔ 13 % → 18 % → 20 % → 22 %
4. **El neto empeora al bajar.** ✔ en dirección, ✘ en monotonía estricta: 10M
   (−0,144) queda por encima de 15M (−0,167). Las tres temporalidades bajas son
   peores que 1H, que es lo que se predecía.
5. **La bruta se queda entre +0,05 y +0,20.** ✘ Se queda **más baja todavía**:
   entre −0,025 y +0,051. Con el filtro de contexto de bctrades encima, la
   ventaja bruta del CRT prácticamente desaparece.

## Lo que esto cierra

Bajar de temporalidad para entrar más fino **no es un ajuste**: es un empeoramiento
estructural, y se ve exactamente por qué. El coste es un número fijo de pips; el
stop se encoge; el cociente sube de 13 % a 22 % del riesgo. Para que compensara,
la tasa de aciertos tendría que superar el 1/(1+R:R) que da la pura geometría, y
no lo hace en ninguna de las cuatro.

**La hipótesis de «estábamos midiendo la temporalidad de ejecución equivocada»
queda descartada.** Era una hipótesis buena, estaba bien fundada en el material,
y era comprobable. Ha salido que no.

Lo que sigue sin probarse es el **order block** de 15M/1H del material del 31 de
mayo, que es otro esquema, no otra temporalidad.
