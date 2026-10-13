# Resultados · el techo de un filtro invisible

Pre-registro: `docs/PREREGISTRO_techo_filtro.md`, subido en `fb8d519` **antes**
de medir. Código: `bt/techo_filtro.py`. EURUSD, **29.614 operaciones**, 5,7 años.

## La pregunta

No «¿funciona su regla?» —eso ya está medido— sino: **si aplica un filtro que no
dice en los vídeos, ¿cuánto podría valer como máximo?**

El hueco a tapar, con la geometría leída de su pantalla: **+8,1 puntos** de
acierto. En la muestra mecanizada, cuyo coste medio es mayor, **+10,5**.

## Prueba A · el mejor decil de cada variable, elegido con trampa

Se mira el resultado y luego se elige el decil ganador. Deliberadamente tramposo.

```
  variable (mejor decil)      n        acierto   umbral   margen      neta
  hora                     2,924     36.0 ±1.7    39.5     -3.5    -0.1053
  dia_semana               6,058     35.7 ±1.2    44.1     -8.4    -0.2533
  ATR_M2                   2,955     35.0 ±1.7    37.5     -2.5    -0.0764
  exceso_barrido           2,962     35.1 ±1.7    42.3     -7.2    -0.2171
  stop_pips                2,972     38.2 ±1.7    37.4     +0.8    +0.0234
  stop_ATR                 2,955     34.8 ±1.7    37.4     -2.6    -0.0770
  edad_nivel_h             2,964     34.4 ±1.7    42.4     -8.0    -0.2390
  toques_previos           2,892     35.7 ±1.7    43.2     -7.5    -0.2254
  velas_espera             2,927     34.4 ±1.7    41.3     -6.8    -0.2054
  compra_venta            29,614     33.3 ±0.5    43.9    -10.5    -0.3155
  dist_dia_previo          2,966     36.8 ±1.7    43.6     -6.8    -0.2034
  recorrido_dia            2,958     37.0 ±1.7    39.8     -2.8    -0.0845
  dist_EMA50_M15           2,958     38.1 ±1.8    43.9     -5.8    -0.1744
  cuerpo_disparo           2,949     34.4 ±1.7    40.7     -6.3    -0.1892
```

El umbral de cada celda sale de su propio coste medio. **Ninguno de los 140
deciles llega.** El mejor margen es **+0,8** puntos, y el procedimiento regala
**+2,3** de media sólo por elegir el mejor de 140. Es decir: el mejor decil está
**por debajo** de lo que produce el azar.

Y el que gana, `stop_pips`, gana por el motivo previsto en el pre-registro: es
el decil de los stops más grandes, que baja el **umbral** del 43,9 % al 37,4 %.
No sube el acierto: lo baja el coste. Es el mismo hallazgo de
`RESULTADOS_stop_minimo.md`, otra vez.

## Prueba B · un modelo sobre las 14 variables a la vez

Gradient boosting, entrenado con el pasado y evaluado sobre el futuro en cinco
bloques. 24.679 operaciones predichas.

```
  AUC fuera de muestra: 0.4945      (0,500 = no sabe nada)

  modelo · decil superior    n 2,467   acierto 31.5 ±1.8   umbral 43.8   margen -12.3
  modelo · quinto superior   n 4,935   acierto 30.6 ±1.3   umbral 43.1   margen -12.5
  modelo · tercio superior   n 8,144   acierto 31.6 ±1.0   umbral 43.0   margen -11.4
```

**AUC 0,4945.** Por debajo de 0,5. Las operaciones que el modelo señala como
mejores aciertan **31,5 %**, menos que la media de 33,3 %. No es que la
combinación sea débil: es que **no existe**. Nada de lo que se ve en el gráfico
al entrar predice cómo acaba esa operación.

## Conclusión

Queda acotado lo que antes era una duda razonable. **Ningún filtro basado en el
gráfico —lo diga o no lo diga en los vídeos— tapa el hueco de +8 puntos.** Ni
eligiendo la casilla ganadora con el resultado delante, ni dejando que un modelo
busque combinaciones que un humano no sabría nombrar.

Lo que esto **no** descarta, y se declaró antes de medir: información que no
está en el precio —noticias, flujo de órdenes— o que simplemente no opere lo que
enseña.

## Y lo de los payouts, por el otro lado

`RESULTADOS_payouts.md` ya mostró que con ventaja **cero** el 84,3 % de la gente
acaba enseñando un papel de payout real. El papel no distingue nada.

Pero hay una forma de darle la vuelta que sí sirve, y es ésta: **cuanto más
grande es lo que afirma, menos operaciones hacen falta para comprobarlo.**

```
 si acierta   neta R/op   %/mes al 1%   n necesario     ~ tiempo
      36.0%      -0.162         -9.7%          2477    41.3 meses
      38.0%      -0.102         -6.1%           814    13.6 meses
      40.0%      -0.042         -2.5%           401     6.7 meses
      41.4%      -0.000         -0.0%           275     4.6 meses
      45.0%      +0.108         +6.5%           132     2.2 meses
      50.0%      +0.258        +15.5%            65     1.1 meses
      60.0%      +0.558        +33.5%            25     0.4 meses
```

Si de verdad convierte 120 $ en 1.000 $, eso es un acierto del orden del 50-60 %
con su geometría, y **eso se demuestra con 25 a 65 operaciones**. Un mes.

Él publica operaciones en directo en la comunidad. **Treinta de esas llamadas,
con los tres precios visibles, valen más que todos los payouts juntos** — y no
hace falta que colabore: basta con apuntarlas según salen, en
`docs/registro_operaciones.html`.

Ésa es la única medición pendiente que puede cambiar el veredicto.

## Récord de predicciones

Cuatro de cuatro.

| predicción | resultado |
|---|---|
| ningún decil llegará al umbral; el mejor entre 36 y 38 % | ninguno llega; el mejor 38,2 % ✔ |
| la variable con más recorrido será el tamaño del stop, y por el coste | `stop_pips`, +0,8, por el umbral ✔ |
| el modelo dará un decil por debajo de 37 % y AUC entre 0,50 y 0,53 | 31,5 % y AUC 0,4945 ✔ (aún peor) |
| el hueco de +8,1 no lo tapa nada del gráfico | no lo tapa ✔ |
