# Mes a mes · y una corrección a lo que le dije

El usuario: *«me cuesta creer que ninguna funcione… aunque falle, pero que me
permita retirar tranquilo cada mes»*. Código: `bt/mes_a_mes.py`, 20.000 caminos.

**Tiene razón y existe.** Lo que no existe es esa cosa dando 300 €/mes sobre
10.000 €. Son dos preguntas distintas y yo las había mezclado.

## La corrección

`RESULTADOS_diez_mil.md` decía «al 4× la mediana son 89-100 €/mes con el 96 % de
las carreras en positivo». **Es cierto y es engañoso**: es la *carrera entera*,
comprando retos nuevos cada vez que una cuenta muere. Lo que se vive es otra
cosa:

```
  cuenta de 10.000 al 4×, límite de caída 8 %
  meses que cobras algo ........ 9 de 36   (25 %)
  cobro mediano ................ 239 €
  la cuenta sigue viva a 3 años   11 %
  si muere, dura ............... 9 meses
```

El camino típico: siete cobros en trece meses, 1.994 € en total, y la cuenta
muere. **Eso no es «retirar tranquilo cada mes».**

## La pregunta que él hizo de verdad

Una cuenta que **aguante** y dé para retirar con regularidad. Es otra pregunta
—no la de maximizar el dinero esperado— y tiene otra respuesta:

```
  escala   %/año   viva a 3 años   meses que cobras   cobro mediano   €/mes   dura
   0,50×    2,3%        100 %            43 %              29 €        17 €   36m
   0,75×    3,5%         97 %            44 %              44 €        26 €   36m
   1,00×    4,7%         90 %            44 %              58 €        34 €   36m
   1,50×    7,0%         68 %            46 %              87 €        48 €   36m
   2,00×    9,3%         49 %            47 %             117 €        59 €   36m
   3,00×   14,0%         25 %            49 %             176 €        72 €   19m
   4,00×   18,7%         11 %            50 %             238 €        77 €   12m
```

**Al 0,75-1,0× es exactamente lo que él describe**: la cuenta sobrevive el 90-97 %
de las veces, cobras casi un mes de cada dos, y el cobro es de 44-58 €.

## El canje, que es la respuesta entera

```
  cuanto más dinero quieres, menos sobrevive la cuenta
  0,75×  ->  97 % sobrevive,  26 €/mes
  4,00×  ->  11 % sobrevive,  77 €/mes
```

No hay forma de rodearlo. El dinero esperado sube con la escala hasta el 4×
—porque reponer la cuenta cuesta sólo 89 €— pero la **tranquilidad** baja en
línea recta.

Él pidió tranquilidad. Eso está en el **1×**, y son **34 €/mes por cada 10.000 €
fondeados**.

## Lo que hace falta para 300 €/mes tranquilos

```
  300 € / 34 € por cada 10.000  =  ~88.000 € fondeados
```

Nueve cuentas de 10.000, o dos de 50.000, operadas al 1×. Con esa escala la
cuenta sobrevive el 90 % de los tres años y cobras casi todos los meses.

**Ése es el número honesto, y es el mismo al que llevan apuntando todas las
mediciones**: un sistema de Sharpe 1,00 con un límite de caída del 8-10 % da un
4-5 % anual, y 300 € al mes son 3.600 € al año.

## Qué le queda

Las dos cosas son verdad a la vez y hay que decirlas juntas:

1. **Sí existe** lo que pedía: un sistema que funciona, que falla el 56 % de los
   meses, que no es espectacular, y del que se retira con regularidad sin
   sobresaltos. Está medido sobre 632 meses con t +7,29.
2. **Da 34 € al mes por cada 10.000 € fondeados.** Para 300 hacen falta 88.000.

Lo que no existe —y esto ya no es opinión, son 175.000 operaciones medidas— es
la versión que da 300 € sobre 10.000.
