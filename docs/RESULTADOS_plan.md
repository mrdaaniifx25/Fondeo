# El plan · de 356 € a 300 €/mes

Código: `bt/plan.py`. Rendimientos por remuestreo de los **632 meses medidos**
(`RESULTADOS_momento_largo.md` + `RESULTADOS_carry.md`). 4.000 carreras de 48
meses por celda. Sistema al **4× de escala**, que es el óptimo de
`RESULTADOS_diez_mil.md`.

## Primero: las cuentas grandes son más baratas

```
  cuenta   10.000 €   reto  89 €  = 0,89 % del tamaño
  cuenta   25.000 €   reto 189 €  = 0,76 %
  cuenta   50.000 €   reto 289 €  = 0,58 %
  cuenta  100.000 €   reto 489 €  = 0,49 %
```

Pero eso no manda, porque lo que se arriesga no es el reto: es **quedarse sin
cuentas a la vez**. Con cuentas pequeñas cada muerte cuesta 89 € en vez de 489.

## El camino, simulado entero

Comprar retos, pasarlos, cobrar, reinvertir los cobros en más cuentas hasta
llegar al objetivo, y a partir de ahí retirar todo.

```
  MUESTRA COMPLETA (1971-2026)

  tamaño  presupuesto  máx cuentas  llega a 300€/mes  meses (mediana)  retos  renta
  10.000        89 €            4            67,0 %               22    602€   364€
  10.000       356 €            4            98,0 %               15    958€   479€
  10.000        89 €            6            69,5 %               20    910€   583€
  25.000       189 €            2            67,9 %               16    669€   341€
  50.000       578 €            2            88,5 %               12  1.307€   973€
 100.000       489 €            1            65,5 %               12    489€     0€
```

```
  SOLO 2013-2026 (el tramo flojo)

  10.000       356 €            4            67,8 %               25  1.017€   205€
  50.000       578 €            2            68,2 %               14  1.202€    39€
```

## La recomendación

**Cuatro cuentas de 10.000 €, escala 4×, empezando con 356 €.**

No es la que más renta da —la de 50.000 × 2 da casi el doble en el buen
régimen— pero es **la más robusta**: en el tramo flojo da 205 €/mes de mediana
frente a 39 €, porque cada muerte cuesta 89 € y no 289.

```
  entrada .................. 356 € (cuatro retos de 10k)
  probabilidad de llegar ... 98 % en el régimen completo · 68 % en el flojo
  tiempo hasta 300 €/mes ... 15 meses de mediana (25 en el flojo)
  gasto total en retos ..... ~958 € en cuatro años
  renta al cuarto año ...... 479 €/mes de mediana (205 en el flojo)
```

**Con un solo reto de 89 €** también se llega, reinvirtiendo los cobros: 67 % de
probabilidad y 22 meses de mediana. Es el camino lento pero no exige ahorrar.

## Por qué empezar con las cuatro a la vez cambia tanto

67 % → 98 %. Con una sola cuenta, si muere en el primer mes te quedas sin nada y
hay que esperar. Con cuatro, la probabilidad de que mueran las cuatro antes de
que alguna llegue a fondeada es pequeña.

**No es diversificación de rendimiento** —las cuatro corren la misma señal y se
mueven juntas— sino **diversificación del calendario**: cada una está en un punto
distinto de su ciclo de drawdown.

## Los lotes, para una cuenta de 10.000 al 4×

Riesgo **1,0 %** por posición (que es el 0,25 % base × 4). Señal de este mes:

```
  par        dirección  señal  σ mensual   nocional   lotes
  USDCNH       COMPRAR  -1.00      0.87%    11.468€    0.11
  USDSEK        VENDER  +1.00      3.14%     3.186€    0.03
  GBPUSD       COMPRAR  +1.00      1.93%     5.188€    0.05
  USDNOK       COMPRAR  -0.75      3.16%     2.370€    0.02
  USDSGD       COMPRAR  -0.75      1.39%     5.415€    0.05
  USDJPY        VENDER  +0.50      2.97%     1.685€    0.02
  USDMXN       COMPRAR  -0.50      2.63%     1.900€    0.02
  NZDUSD       COMPRAR  +0.50      3.13%     1.595€    0.02
  AUDUSD       COMPRAR  +0.25      2.63%       952€    0.01
  USDCAD        VENDER  +0.25      1.72%     1.455€    0.01
  EURUSD       COMPRAR  +0.25      1.95%     1.283€    0.01
  USDZAR        VENDER  +0.25      2.44%     1.025€    0.01
```

Nocional total **37.523 €** = 3,8 veces la cuenta. Es apalancamiento bajo para
una cartera de divisas que se compensan entre sí, y cabe de sobra en el 1:30 que
dan las fondeadoras.

**Las doce entran con el lote mínimo de 0,01 de MT5.** Ninguna se queda fuera por
redondeo, que era el riesgo real de operar esto en una cuenta pequeña.

## Lo que hay que verificar antes de pagar

De `RESULTADOS_carrera_fondeo.md`, y sigue sin respuesta:

1. **¿El reto tiene plazo máximo?** Con 18,7 % anual, +8 % tarda unos 5 meses.
   Si el reto caduca a los 30 o 60 días, este sistema no lo pasa.
2. ¿Se puede mantener posición el fin de semana?
3. ¿Hay regla de días mínimos operando? Con 12 operaciones al año puede
   incumplirse.
4. ¿Cuántas cuentas simultáneas permite la fondeadora?
5. ¿El swap lleva recargo? Se modeló 1,5 puntos anuales.

La primera y la tercera pueden invalidar el plan entero. Cuestan un correo.
