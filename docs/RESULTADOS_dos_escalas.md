# Pasar el reto más rápido · dos escalas

El usuario: *«no tiene plazo máximo, pero no puedo estar 3 meses para pasar una
cuenta»*. Código: `bt/dos_escalas.py`. 20.000 intentos por celda con los 632
meses medidos.

## La idea, que es del tercer operador y es correcta

> *«en challenge hay que ser mucho más agresivo en cuanto a la gestión del riesgo»*

Tiene razón, y se puede justificar: **durante el reto lo único que se arriesga
son 89 €. Una vez fondeado se arriesga un activo que produce.** Son apuestas
distintas y no deben llevar el mismo tamaño. Hasta ahora las había modelado con
la misma escala.

## Lo medido

```
  DOS FASES (+8 % y +5 %, caída 8 %) · muestra completa

  escala  %/año   pasa   meses (mediana)   coste por   meses hasta
                         de los que pasan  fondearse   fondearse
     2x    9,3%  80,5%         15m            111€        18m
     4x   18,7%  64,6%          7m            138€        10m
     6x   28,0%  17,3%          4m            515€        16m
     8x   37,3%   0,1%          2m        118.667€      1.440m
```

```
  UNA FASE (+10 %, caída 6 %) · muestra completa

     2x    9,3%  83,7%         10m            106€        12m
     4x   18,7%  72,0%          4m            124€         5m   <- el óptimo
     6x   28,0%  32,8%          2m            271€         6m
     8x   37,3%   2,2%          1m          4.130€        49m
```

## La respuesta

**El reto de UNA FASE al 4×.** Mediana de **4 meses** para pasarlo y **5 meses**
hasta estar fondeado contando los intentos fallidos, con 124 € de coste
esperado. Frente a los 10 meses de las dos fases.

Y si quiere ir aún más rápido, **6×**: mediana de **2 meses** para pasar. Pero
la probabilidad cae del 72 % al 33 % y el coste esperado sube a 271 €, así que
el tiempo total hasta fondearse sube a 6 meses. **Más rápido por intento, igual
de lento en total.**

En el tramo flojo, el 6× sí gana: 7 meses hasta fondearse frente a 9 del 4×.

## El muro, que es lo importante

**Por encima de 6× esto se cae a plomo.** Al 8× la probabilidad de pasar es del
2,2 % en una fase y del 0,1 % en dos: se toca el límite de caída antes que el
objetivo. Subir la escala **no compra tiempo** a partir de ahí, sólo compra
cuotas quemadas.

Ésa es la aritmética de barreras otra vez: el escalado no cambia el cociente
objetivo/límite, sólo la velocidad con que se resuelve. Y cuando el límite está
más cerca que el objetivo, la velocidad juega en contra.

## La corrección al plan

`RESULTADOS_plan.md` daba 15 meses hasta 300 €/mes usando la misma escala en
todo. Con dos escalas —reto de una fase al 4×, fondeada al 4×— el tramo de reto
pasa de 10 meses a 5.

**Sigue sin ser rápido.** Cinco meses de mediana hasta la primera cuenta
fondeada, y el p75 son 7. Lo que no hay es forma de comprimirlo más: está
probado hasta el 20× y ahí no se pasa nunca.
